"""
TODO: optimize, do more stuff in parallel
particularily, more stuff could be done while iterating the commits, thus
reducing the number of iterations
"""
import re, os, sys
from subprocess import Popen, PIPE
import itertools
from email.utils import parsedate
from time import mktime
import pickle
import yap
from collections import defaultdict

class RawRepo:
    """
    Raw data from the .git repository.

    This class also stores some more details which can be deduced by simple
    algorithms from the raw data - no big number crunching, nothing.

    This approach makes it easy to cache data and swap algorithms and maths
    more easily in the more complex classes like Repository.
    """

    rawcommits = None
    """
    The output of the git log command, containing only the meta data of the each
    commit.
    """
    rawhist = None
    """
    The location of the repository
    """
    repodir = None
    cachedir = None
    GIT = None

    """
    Types and flags for commits
    """
    TYPE_NEW = 1
    TYPE_RENAME = 2
    TYPE_BINARY = 4
    TYPE_MODIFIED = 8
    
    #TODO deletions

    FLAG_NONE = 0
    FLAG_MERGE = 1

    DIRTY_NONE = 0
    DIRTY_DETACHED = 1
    DIRTY_TIMESTAMP = 2

    """
    List of commits, whereas each commit is a dictionary, with its meta data
    as keys
    """
    commits = None
    """
    List of users, each user is a dictionary with the meta data:
    main_identity: <identity-id>,
    identities: [<list-of-identity-ids-of-this-user>]
    friendly_name: First Last, it is redundant from main_identity, easy to work
    """
    users = None
    """
    List of identities, each identity is identified by the index.
    """
    identities = None

    identities_by_name = None
    identities_by_email = None

    """
    List of identities and frequencies. The index is the identity id, the value
    is the frequency of commits made by that identity
    """
    identities_freq = None

    """
    Dictionary of identity_id => commit id with last appearance.
    """
    identities_last_appearance = None

    """
    List of SHAs and commit IDs from self.commits
    """
    commits_by_sha = None
    """
    List of short SHAs and commit IDs from self.commits
    """
    commits_by_shortsha = None
    """
    List of timestamps and commit IDs from self.commits
    """
    commits_by_timestamp = None

    """
    List of user IDs and list of commit IDs from self.commits
    """
    commits_by_user = None

    """
    List of identity IDs and list of commit IDs from self.commits
    """
    commits_by_identity = None

    """
    Dictionary of file => commit_id list with commits who have created a file
    """
    path_to_commits = None

    """
    Dictionary of treeish (tag, HEAD) and corresponding shas. General commits
    of interest.
    """
    refs = None

    """
    List of tags, usually marking milestones
    """
    tags = None

    """
    List of merge commits
    """
    merge_commits = None

    """
    List of identities and merges issued by that identity
    """
    identities_and_merges = None

    """
    List of users and merges issued by that user
    """
    users_and_merges = None

    """
    List of milestones, basically tags converted to commit ids and sorted
    """
    milestones = None

    """
    Classified commits
    """
    classified_commits = None # TODO cache at some point


    """
    These are merely aesthetical details, useful for report formatting, which
    we agreggate during the calculations.
    """
    max_size_of_merges = None
    #TODO add more variables
    
    def __init__(self, repodir, cachedir=None):
        self.repodir = os.path.abspath(os.path.expanduser(repodir))
        if cachedir:
            self.cachedir = os.path.abspath(os.path.expanduser(cachedir))
            #TODO load stuff from cache, at least the direct outfrom from git
        self.GIT = ["git", "--git-dir=" + repodir + "/.git", "--work-tree=" + repodir]

        if cachedir:
            if os.path.isfile(self.cachedir + '/rawrepo.cache'):
                self._reload_cache()
            else:
                self.dohardwork()
                self._store_cache()
        else:
            self.dohardwork()

    def dohardwork(self):
        self._build_linear_stats()
        self._consolidate_users()
        self._build_pairwise_stats()
        self._consolidate_users_and_commits()

    def get_cacheable(self):
        return {
                'commits': self.commits,
                'users': self.users,
                'refs': self.refs,
                'tags': self.tags,
                'path_to_commits': self.path_to_commits,
                'commits_by_sha': self.commits_by_sha,
                'commits_by_shortsha': self.commits_by_shortsha,
                'commits_by_timestamp': self.commits_by_timestamp,
                'commits_by_identity': self.commits_by_identity,
                'identities': self.identities,
                'identities_by_name': self.identities_by_name,
                'identities_by_email': self.identities_by_email,
                'identities_freq': self.identities_freq,
                'identities_last_appearance': self.identities_last_appearance,
                'merge_commits': self.merge_commits,
                'identities_and_merges': self.identities_and_merges,
                'users_and_merges': self.users_and_merges,
                'milestones': self.milestones,
                'max_size_of_merges': self.max_size_of_merges
            }

    def _reload_cache(self):
        cache = self.get_cache('rb')
        cacheable = pickle.load(cache)
        cache.close() #yeah, dirty, asymmetrical close call
        for i, k in cacheable.items():
            setattr(self, i, k)

    def _store_cache(self):
        cache = self.get_cache('wb')
        data = self.get_cacheable()
        pickle.dump(data, cache)
        cache.close() #yeah, dirty, asymmetrical close call
    
    def get_cache(self, mode='rb'):
        return open(self.cachedir + '/rawrepo.cache', mode)

    def _get_rawhist(self):
        """
        Get the raw short history
        """
        if self.rawhist:
            return self.rawhist
        p = Popen(self.GIT + ["log", "--reverse", "--date-order", "--date=rfc",
            "--log-size", "--boundary", "--full-history", "--numstat",
            "--dirstat=0", "-z", "--no-abbrev-commit", "-M", "--full-index", "-t",
            "--decorate"], bufsize=4096, stdout=PIPE)
        self.rawhist = p.communicate()[0].decode('utf-8')
        return self.rawhist

    def _grouper(self, number, iterable, fillvalue=None):
        """
        Helper function which groups elements.
        """
        args = [iter(iterable)] * number
        return itertools.zip_longest(fillvalue=fillvalue, *args)

    def _build_pairwise_stats(self):
        """
        Build associations between identities and merges and users and merges.

        Also create boundaries of commit intervals for user changes and
        identity changes on the timeline.
        """

        self.merge_commits = []
        identities_and_merges = {}
        users_and_merges = {}
        for i in range(len(self.identities)):
            identities_and_merges[i] = []

        for i in range(len(self.users)):
            users_and_merges[i] = []

        for cid, commit in enumerate(self.commits):
            if 'Merge' in commit:
                lst = []
                for merge in commit['Merge']:
                    lst.append(self.commits_by_shortsha[merge])
                commit['Merge'] = lst
                self.merge_commits.append(cid)
                identities_and_merges[commit['identity']].append(cid)
            if 'parent' in commit:
                #print("DBG (alpha/app/yap/RawRepo.py:260) commit['parent']", commit['parent']) # XXX: what to do?
                pass

        for iid, identity in enumerate(self.identities):
            users_and_merges[identity['userid']] += identities_and_merges[iid]

        self.identities_and_merges = identities_and_merges
        self.users_and_merges = users_and_merges

    def _build_linear_stats(self):
        """
        Build the statistics which can be built by just iterating over the
        commits once.
        """

        commits = []
        commits_by_sha = []
        commits_by_shortsha = {}
        commits_by_timestamp = []
        commits_by_identity = []

        identities = []
        identities_by_name = []
        identities_by_email = []
        identities_freq = []
        identities_last_appearance = {}

        path_to_commits = defaultdict(list)

        self.tags = {}
        self.refs = {}

        prev_identity_id = -1
        prev_ts = 0

        commits_raw = self._get_raw_commits()
        for i, commit in enumerate(commits_raw):
            commit = self._get_commit(commit)
            short_sha = commit['sha'][:7]
            if commit['sha'] in commits_by_sha:
                print("ALREADY THERE: " + commit['sha'])
                sys.exit(1) #TODO: throw exception

            commit['dirty'] = RawRepo.DIRTY_NONE

            if len(commits):
                # Task: gather information about the topological structure, parent -> child
                p = Popen(self.GIT + ['rev-parse', commit['sha'] + '^'], bufsize=4096, stdout=PIPE, stderr=PIPE)

                out, err = p.communicate()

                out = out.decode('utf-8')
                err = err.decode('utf-8')
                returncode = p.returncode
                del p
                if returncode == 0:
                    out = out.strip()
                    if out not in commits_by_sha:
                        commit['parent'] = -1 # XXX this should never happen, but who knows?
                        print("DBG (alpha/app/yap/RawRepo.py:308) something went wrong")
                        sys.exit(42)
                    else:
                        commit['parent'] = commits_by_sha.index(out)
                else:
                    ref = "fatal: ambiguous argument '" + commit['sha'] + "^': unknown revision or path not in the working tree."
                    if err.startswith(ref):
                        commit['dirty'] |= RawRepo.DIRTY_DETACHED
                # End Task

            commits.append(commit)
            if commit['identity'] not in identities:
                identity = commit.pop('identity')
                identity_id = len(identities)
                identities.append(identity)
                commit['identity'] = identity_id
                identities_by_name.append(identity['author_name'])
                identities_by_email.append(identity['author_email'])
                identities_freq.append(0)
            else:
                identity_id = identities.index(commit['identity'])

            commit['identity'] = identity_id
            commit_id = len(commits)-1

            if 'refs' in commit:
                refs = commit['refs']
                for ref in refs:
                    if 'tag: ' == ref[:5]:
                        self.tags[ref[5:]] = commit_id
                    else:
                        if ref not in self.refs:
                            self.refs[ref] = []
                        self.refs[ref].append(commit_id)
            if 'Merge' in commit:
                commit['Merge'] = commit['Merge'].split()

            commits_by_sha.append(commit['sha'])
            commits_by_shortsha[short_sha] = commit_id
            commit['Date'] = mktime(parsedate(commit['Date']))
            commits_by_timestamp.append(commit['Date'])

            if commit['Date'] < prev_ts:
                commit['dirty'] |= RawRepo.DIRTY_TIMESTAMP
                print("DBG (alpha/app/yap/RawRepo.py:364) commit['dirty']", commit['dirty'])

            commits_by_identity.append(identity_id)

            identities_last_appearance[identity_id] = commit_id

            identities_freq[identity_id] += 1
            paths = {path: info['type'] for path, info in commit['modifications'].items()}
            paths.update({path[0]: info['type'] for path, info in commit['renames'].items()})
            paths.update({path[1]: info['type'] for path, info in commit['renames'].items()})

            for path, info in paths.items():
                path_to_commits[path].append({'commit_id': commit_id, 'type': info})

            prev_identity_id = identity_id
            prev_ts = commit['Date']

        milestones = list(self.tags.values())
        milestones.sort()
        self.milestones = milestones

        self.commits = commits
        self.commits_by_sha = commits_by_sha
        self.commits_by_shortsha = commits_by_shortsha
        self.commits_by_timestamp = commits_by_timestamp
        self.commits_by_identity = commits_by_identity

        self.identities = identities
        self.identities_by_name = identities_by_name
        self.identities_by_email = identities_by_email
        self.identities_freq = identities_freq
        self.identities_last_appearance = identities_last_appearance

        self.path_to_commits = path_to_commits

    def _get_raw_commits(self):
        reg1 = re.compile(r'((?:^|\0\0|\n\0)commit [0-9a-f]{40,40})')
        rawhist = self._get_rawhist()
        split1 = reg1.split(rawhist)
        split1.insert(0,'')
        commits = []
        for c_pair in self._grouper(2, split1):
            if c_pair[1]:
                cut = str(c_pair[0]).rfind('\0')
                commit = c_pair[0][cut+1:]+c_pair[1]
                commits.append(commit)
        return commits

    def _get_commit(self, commitstr):
        """
        Extract the commit meta data from the git log string commitstr
        containing details about one single commit.

        Also collect identities and each identity's histogram.
        """
        reg1 = re.compile(r'(^(\n\0)?|\0{1,2})commit (?P<sha>[0-9a-f]{40,40})( \((?P<refs>[^)]+)\))?\nlog size (?P<log_size>\d+)\n(?P<rest>.+)', re.DOTALL)
        match1 = reg1.match(commitstr)
        if not match1:
            return None
        commit = match1.groupdict()
        commit['log_size'] = int(commit['log_size'])
        refs = commit.pop('refs')
        if refs != None:
            refs = refs.split(", ")
            commit['refs'] = refs
        rest = commit['rest']
        del commit['rest']
        reg2 = re.compile(r'(Author|Date|Merge):\s+([^\n]+)') #TODO get the date as unix timestamp of the committer, %ct
        consumed_len = 0
        for line in rest.split("\n"):
            match2 = reg2.match(line)
            if match2:
                meta = {match2.group(1) : match2.group(2)}
                consumed_len += len(match2.group(0)) + 1
                commit.update(meta)
            else:
                reg3 = re.compile(r'([^:]+):\s+([^\n]+)')
                match3 = reg3.match(line)
                if match3:
                    meta = {match3.group(1) : match3.group(2)}
                    print("not matched but meta" + str(meta))
                break
        if 'Author' in commit:
            idstr = commit.pop('Author')
            reg4 = re.compile(r'(?P<author_name>[^<]+) <(?P<author_email>[^>]*)>')
            t = reg4.match(idstr).groupdict()
            identity = (t['author_name'], t['author_email'])
            commit['identity'] = t

        commit['message'] = rest[consumed_len:commit['log_size']].strip()
        rest = rest[commit['log_size']:].lstrip()

        rest = rest.split("\0")
        commit['modifications'], commit['mod_and_renames'], commit['renames'], commit['dirs'], commit['flags'] = self._commit_meta_info(rest)

        files = [path for path, d in commit['modifications'].items()] + \
                [path[1] for path, d in commit['mod_and_renames'].items()]

        commit['contents'] = self._get_files_from_sha(commit['sha'], files)
        commit['deletes'] = [path for path, content in commit['contents'].items() if content==None]
        for d in commit['deletes']:
            del commit['modifications'][d]

        return commit

    def _commit_meta_info(self, lst):
        re_modified = re.compile(r'^(?P<lines_added>\d+)\t(?P<lines_deleted>\d+)\t(?P<path>.+)$')
        re_newfile = re.compile(r'^(?P<lines_added>\d+)\t0\t(?P<path>.+)$')
        re_rename_file = re.compile(r'^0\t0\t$') # from -> to
        re_dirpercent = re.compile(r'^\s+\d+\.\d+%.+') # list of dirs
        re_binary = re.compile(r'^-\t-\t(?P<path>.+)$')
        re_modified_and_renamed = re.compile(r'^(?P<lines_added>\d+)\t(?P<lines_deleted>\d+)\t$')

        modifications = defaultdict(dict)
        renames = defaultdict(dict)
        mod_and_rename = defaultdict(dict)
        dirs = []
        flags = RawRepo.FLAG_NONE
        it = enumerate(lst)
        for i, item in it:
            match = re_newfile.match(item)
            if match:
                match = match.groupdict()
                match['type'] = RawRepo.TYPE_NEW
                match['lines_added'] = int(match['lines_added'])
                modifications[match['path']] = match
                continue
            match = re_modified.match(item)
            if match:
                match = match.groupdict()
                match['type'] = RawRepo.TYPE_MODIFIED
                match['lines_added'] = int(match['lines_added'])
                match['lines_deleted'] = int(match['lines_deleted'])
                modifications[match['path']] = match
                continue
            match = re_rename_file.match(item)
            if match:
                del match
                match = {'type': RawRepo.TYPE_RENAME}
                _, from_f = next(it)
                _, to_f = next(it)
                match['from'] = from_f
                match['to'] = to_f
                renames[(match['from'], match['to'])] = match
                continue
            match = re_dirpercent.match(item)
            if match:
                dirs = item.split("\n")
                continue
            match = re_binary.match(item)
            if match:
                match = match.groupdict()
                match['type'] = RawRepo.TYPE_BINARY
                modifications[match['path']] = match
                continue
            if '' == item:
                flags = flags | RawRepo.FLAG_MERGE
                continue
            match = re_modified_and_renamed.match(item)
            if match:
                match = match.groupdict()
                match = {'type': RawRepo.TYPE_RENAME|RawRepo.TYPE_MODIFIED}
                _, from_f = next(it)
                _, to_f = next(it)
                match['from'] = from_f
                match['to'] = to_f
                mod_and_rename[(match['from'], match['to'])] = match
                continue
            else:
                print("NONE at", item)
                return None

        return dict(modifications), dict(mod_and_rename), dict(renames), dirs, flags

    def _get_files_from_sha(self, sha, files):
        from subprocess import Popen, PIPE
        import tarfile
        if 0 == len(files):
            return {}
        p = Popen(self.GIT + ["archive", sha], bufsize=10240, stdout=PIPE)
        tar = tarfile.open(fileobj=p.stdout, mode='r|')
        contents = {}
        doall = files == '*'
        if not doall:
            files = set(files)
        for entry in tar:
            if (isinstance(files, set) and entry.name in files) or doall:
                tf = tar.extractfile(entry)
                contents[entry.name] = tf.read()
                if not doall:
                    files.discard(entry.name)

        if not doall:
            for fname in files:
                contents[fname] = None
        tar.close()
        p.stdout.close()
        p.wait()
        return contents

    def all_indices(self, value, qlist):
        indices = []
        idx = -1
        while True:
            try:
                idx = qlist.index(value, idx+1)
                indices.append(idx)
            except ValueError:
                break
        return indices

    def _consolidate_users(self):
        """
        Group identities into users, based on information which may happen
        to be common to individual identities, like email or name.
        
        Set a user's main identity based on the histogram of the identity's
        usage in commits.
        """
        users_data = {}
        user_id = 0
        for identity_id, identity in enumerate(self.identities):
            same_name = self.all_indices(identity['author_name'], self.identities_by_name)
            same_email = self.all_indices(identity['author_email'], self.identities_by_email)
            newids = list(set(same_name + same_email))
            self.identities[identity_id]['no_commits'] = self.identities_freq[identity_id]
            if newids not in users_data.values():
                users_data[user_id] = newids
                user_id += 1

        users = {}
        for userid, user_identities in users_data.items():
            max = 0
            max_id = -1
            user = {'identities': user_identities, 'no_commits': 0}
            for identity in user_identities:
                self.identities[identity]['userid'] = userid
                user['no_commits'] += self.identities[identity]['no_commits']
                if max < self.identities_freq[identity]:
                    max_id = identity
                    max = self.identities_freq[identity]
            user['main_identity'] = max_id
            users[userid] = user

        self.users = users
    
    def _consolidate_users_and_commits(self):
        """
        1. For each commit, set its user, based on the identity of that commit.

        This just makes the data easier to process via memoization.

        2. This also sets merged (merged, not merge) to -1 multiplied with the
        list of the commit ids which have merged the respective commits.

        3. TODO: group commits by user

        """

        max_size_of_merges = 0
        for cid, commit in enumerate(self.commits):
            # task 1: memoize userid for each commit
            self.commits[cid]['userid'] = self.identities[commit['identity']]['userid']
            # task 2: create the reversed merge direction
            if 'Merge' in commit:
                for mid in commit['Merge']:
                    if 'Merge' not in self.commits[mid]:
                        self.commits[mid]['Merge'] = []
                    self.commits[mid]['Merge'].append(-1 * cid)
                    l = len(self.commits[mid]['Merge'])
                    if l > max_size_of_merges:
                        max_size_of_merges = l

        self.max_size_of_merges = max_size_of_merges


    def get_related_path_commits(self, path, lessthan=None):
        """
        Given a path, return the list of commits that have modified that path
        in some way
        """
        lst = []
        if path not in self.path_to_commits:
            return None
        for p in self.path_to_commits[path]:
            if lessthan and p['commit_id'] >= lessthan:
                break
            lst.append(p['commit_id'])
        return lst

    def get_files_of_commit(self, treeish):
        p = Popen(self.GIT + ['ls-tree', '--full-tree', '-r', '--name-only', treeish], bufsize=4096, stdout=PIPE)

        out = p.stdout.read().decode('utf-8')
        p.wait()
        return out.splitlines() #TODO: cache

    def get_tag_of_commit(self, cid):
        """
        Given a commit id, return its tag, or None
        """
        for tag, refcid in self.tags.items():
            if cid == refcid:
                return tag
        return None

    def get_effective_commits_for(self, treeish):
        """
        Get a dictionary of commits and their factors (if greater than 1)
        for all the paths reachable, starting from treeish.

        In other words, how "relevant" the commits are, relative to treeish.

        Treeish is most usual in tag name.
        """
        from collections import Counter
        files = self.get_files_of_commit(treeish)
        class1_commits = []
        for path in files:
            commits = self.get_related_path_commits(path)
            if commits != None:
                class1_commits += commits

        if treeish in self.tags:
            t = [ v for v in class1_commits if v <= self.tags[treeish] ]
            class1_commits = t
        hist = Counter(class1_commits)
        effective = {}
        for k, v in hist.items():
            if v > 1: effective[k] = v
        return effective

    def get_treeish_commit(self, treeish):
        """
        Given a treeish, return its associated commit number, a list of
        numbers, or None
        """
        if treeish in self.tags:
            return self.tags[treeish]
        elif treeish in self.refs:
            return self.refs[treeish]
        else:
            return None

    def get_milestone_of_commit(self, cid):
        """
        Get the milestone for the given commit id cid
        """

        from bisect import bisect_left
        t = bisect_left(self.milestones, cid)
        if t == len(self.milestones): return None
        return t+1

    def get_tagger_of_tag(self, tagname):
        return self.commits[self.tags[tagname]]['identity'], self.commits[self.tags[tagname]]['userid']


    def generate_timelines(self):
        timeline_user_changes = [] #user changes throughout time
        timeline_identity_changes = [] # identity changes which are not user changes
                                        # XXX: this skips per-user identity changes
                                        # if there are user changes interleaved
                                        # TODO: is inspecting this worthwile? are there
                                        # any relevant information we can squeeze
                                        # out of it? ATM, it looks like the answer is "no"
        timeline_out_of_order_commits = [] # commits which do not have as parent
                                            # the commit id of themselves minus 1

        timeline_merge_only_commits = [] # list of pure merge commits
        timeline_merged_only_commits = [] # list of pure merged commits, that is, commits
                                            # which have only been merged into other commits
        timeline_merge_mixed_commits = []

        timeline_out_of_milestone_merges = []

        tagged = list(self.tags.values())

        from functools import reduce
        def red_mergetype(x, y):
            if x > 0 and y > 0:
                return 1
            elif x < 0 and y < 0:
                return -1
            else:
                return 0

        prev_user = -1
        prev_ident = -1
        prev_cid = -1
        for cid, commit in enumerate(self.commits):
            if commit['userid'] != prev_user:
                timeline_user_changes.append(cid)
            if commit['identity'] != prev_ident:
                timeline_identity_changes.append(cid)

            if 'parent' not in commit or commit['parent'] != prev_cid:
                timeline_out_of_order_commits.append(cid)

            if 'Merge' in commit:
                type = reduce(red_mergetype, commit['Merge'])
                if type == 1:
                    timeline_merge_only_commits.append(cid)
                elif type == -1:
                    timeline_merged_only_commits.append(cid)
                else:
                    timeline_merge_mixed_commits.append(cid)

                if type != -1:
                    merges = [mid for mid in commit['Merge'] if mid >= 0]
                    if len(merges) == 2:
                        m1 = self.get_milestone_of_commit(merges[0])
                        m2 = self.get_milestone_of_commit(merges[1])
                        if m1-m2:
                            timeline_out_of_milestone_merges.append(cid)

            prev_user = commit['userid']
            prev_ident = commit['identity']
            prev_cid = cid

        timeline_identity_changes = list(set(timeline_identity_changes)-set(timeline_user_changes))
        return timeline_user_changes, timeline_identity_changes, timeline_out_of_order_commits, \
                timeline_merge_only_commits, timeline_merged_only_commits, timeline_merge_mixed_commits, \
                tagged, timeline_out_of_milestone_merges

    def classify_commits(self):
        if self.classified_commits:
            return self.classified_commits

        user_changes, identity_changes, out_of_order, only_merge, only_merged, mixed_merge, tagged, late_merge = self.generate_timelines()
        subsets = yap.compact('user_changes', 'identity_changes', 'out_of_order',
                'only_merge', 'only_merged', 'mixed_merge', 'tagged', 'late_merge')
        parents = defaultdict(int)
        meta = list(subsets.keys())
        meta.sort()

        for i,key in enumerate(meta):
            for elem in subsets[key]:
                parents[elem] += 2**i

        meta.reverse()

        children = defaultdict(list)
        for elem, p in parents.items():
            globk = tuple()
            for key, bit in enumerate(yap.bits(p, len(subsets))):
                if bit:
                    globk += (meta[key],)
            children[globk].append(elem)

        self.classified_commits = children
        return children

    def get_classes_of_commit(self, cid):
        classified = self.classify_commits()

        for classes, commits in classified.items():
            if cid in commits:
                return classes

        return None

    def get_classes_histogram_for_commits(self, lst):
        classified = self.classify_commits()
        ctrlset = set(lst)
        res = defaultdict(int)
        for cid in lst:
            notfound = False
            for classes, commits in classified.items():
                if cid in commits:
                    notfound = False
                    for cls in classes:
                        res[cls] += 1
                    break
                else:
                    notfound = True
            if notfound == True:
                res[None] += 1
        return dict(res)

    def commits_report(self):
        # TODO: add some more columns, covering more data
        merged_width = self.max_size_of_merges * 5 + 2

        r = "CId  User  Merged" + ' ' * (merged_width-4) + "Tag\n"

        fmt = "{{:<5}}{{:<6}}{{:<{0}}}{{:<15}}{{:<10}}\n".format(merged_width+2)
        nonfmt = '-' * merged_width

        for cid, commit in enumerate(self.commits):
            is_merge = 'Merge' in commit

            userid = commit['userid']

            tag = self.get_tag_of_commit(cid) or '      '

            if is_merge:
                merged = commit['Merge']
            else:
                merged = nonfmt

            if 'parent' in commit:
                if commit['parent'] == cid-1:
                    parent = '    '
                else:
                    parent = commit['parent']
            else:
                parent = '<no parent>'

            r += fmt.format(cid, userid, merged, tag, parent)

        return r

    def iter_chain_from_commit(self, start):
        if isinstance(start, str):
            if start in self.tags:
                start = self.tags[start]
            elif start in self.refs:
                if len(self.refs[start]) != 1:
                    raise
                else:
                    start = self.refs[start][0]
            else:
                raise

        commit = self.commits[start]

        while 'parent' in commit:
            yield commit['parent']
            commit = self.commits[commit['parent']]

    def __str__(self):
        no_commits = len(self.commits)
        no_users = len(self.users)
        no_identities = len(self.identities)

        tagged_commits = list(self.tags.values())
        tagged_commits.sort()

        identities = "Id      Name                          Email                                   #Commits #Merges\n" + \
                     "----------------------------------------------------------------------------------------------\n"
        for i, id, in enumerate(self.identities):
            identities += "{}\t{:<30}{:<40}{:<9}{:<9}\n".format(i,
                    id['author_name'],
                    '<' + id['author_email'] + '>',
                    self.identities_freq[i],
                    len(self.identities_and_merges[i]))

        users = "Real name                  Main Id     Identities          #Commits #Merges\n" + \
                "---------------------------------------------------------------------------\n"
        for uid, user in self.users.items():
            users += "{:<30}{:<9}{:<20}{:<9}{:<9}\n".format(self.identities[user['main_identity']]['author_name'],
                    user['main_identity'],
                    user['identities'],
                    user['no_commits'],
                    len(self.users_and_merges[uid]))

        user_merges = ""
        for uid, merges in self.users_and_merges.items():
            user_merges += "{}\t{}\n".format(uid, merges)

        identity_merges = ""
        for iid, merges in self.identities_and_merges.items():
            identity_merges += "{}\t{}\n".format(iid, merges)

        tag_stats = "Tag    Commit Id   Complex commits\n" + \
                    "----------------------------------\n"
        for tree in self.tags:
            tag_stats += "{:<10}{:<9}{}\n".format(tree, self.get_treeish_commit(tree),
                    self.get_effective_commits_for(tree))

        data = yap.compact('no_commits', 'no_users', 'no_identities',
                'identities', 'users', 'user_merges', 'tagged_commits',
                'tag_stats', 'identity_merges')

        return """
#Commits: {no_commits}
#Users: {no_users}
#Identities: {no_identities}

Tagged commits: {tagged_commits}

Identities
==========
{identities}

Users
=====
{users}

Users and their merges
======================
{user_merges}

Identities and their merges
===========================
{identity_merges}

Tags
====
{tag_stats}
""".format(**data)
