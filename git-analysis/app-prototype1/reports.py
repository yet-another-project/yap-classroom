from yap import *
from optparse import OptionParser
import ast

MYLIB_PATH = '/home/flav/projects/yet-another-project/My-library'
CACHE_DIR = '/home/flav/projects/yet-another-project/yap-analysis/data'

raw = RawRepo(MYLIB_PATH, cachedir=CACHE_DIR)

def normalize_pythonic(option, opt, value, parser):
    setattr(parser.values, option.dest, ast.literal_eval(value))

opts = OptionParser()
opts.add_option("-o", "--overview", action="store_true", default=False,
                help="View the raw repository's overview")
opts.add_option("-c", "--commits", action="callback", callback=normalize_pythonic,
                type="string",
                help="View information about commits")
opts.add_option("-s", "--sha",
                help="Display the raw data of commit with the sha")
opts.add_option("-a", "--all", action="store_true", default=False,
                help="View all commits, pretty-printed")
opts.add_option("-n", "--notable", action="store_true", default=False,
                help="Show noteworthy commits and the reason they're noteworthy")
opts.add_option("-m", "--merges", action="store_true", default=False,
                help="Show a merge report")
opts.add_option("-t", "--classified", action="store_true", default=False,
                help="Show the commits by their classification")
opts.add_option("--topological", action="store_true", default=False,
                help="Build topological structure first")

opts.add_option("--development", action="store_true", default=False,
                help="Do whatever action is in development")

(options, args) = opts.parse_args()

if options.overview:
    print(raw)
else:
    if options.topological:
        topo = TopoRepo(raw)
        topo.build_pagerank_trails()
        topo.build_pagerank_trails_stdev()
        lonewolf_scores, interactivity_scores, team_productivity = topo.build_team_noteam()
    if options.commits:
        for cid in options.commits:
            print(Commit(raw, cid))

    if options.sha:
        cid = raw.commits_by_sha.index(options.sha)
        print(Commit(raw, cid))
        print("------------------------------------")
        print(raw.commits[cid])

    if options.all:
        for cid, _ in enumerate(raw.commits):
            print(Commit(raw, cid))
    if options.notable:
        #TODO: make this more informative
        classified = raw.classify_commits()
        notable_count = 0
        for tags, commits in classified.items():
            notable_count += len(commits)

        for cid, commit in enumerate(raw.commits):
            for tags, commits in classified.items():
                if cid in commits:
                    print(cid, tags)
                    break
        print("total notable commits:", notable_count)
    if options.merges:
        print(raw.commits_report())
    if options.classified:
        for tags, commits in raw.classify_commits().items():
            print(tags)
            print("-----------------------------------------------------")
            print(commits)
            print("")

#TODO get the date as unix timestamp of the committer, %ct
#TODO: check out_of_order for Merge commits only if necessary

def get_diffing_of_path_commit(raw, cid, path):
    """
    Given a commit and a path, get the list of commits that also contain the
    same path, ordered by probability.

    A probability less than 1 signals an unclean file rename
    """

    by_commits = raw.get_related_path_commits(path, lessthan=cid)
    if path in raw.commits[by_commits[-1]]['contents']:
        return (1, by_commits[-1], path)
    else:
        by_commits.reverse()
        cid2 = by_commits[0]
        infos = raw.commits[cid2]['info']
        #print("infos", infos)
        for cid2 in by_commits:
            for info in infos:
                if info['type'] == RawRepo.TYPE_RENAME:
                    if info['to'] == path:
                        prob, newcid, newpath = get_diffing_of_path_commit(raw, cid2, info['from'])
                        return prob, newcid, newpath
                    if info['from'] == path:
                        prob, newcid, newpath = get_diffing_of_path_commit(raw, cid2, info['from'])
                        return prob, newcid, newpath
                else:
                    print("not matched", info)
        # TODO start using soundexes and the like ... desperate measures
        return (0, None, path)


if options.development:
    import jellyfish as jf
    import networkx as nx
    import os
    import sys
                    #lev = jf.damerau_levenshtein_distance(text1, text2)
                    #dlev = jf.levenshtein_distance(text1, text2)

    notableextensions = ['.php', '.js', '.sql']

    exts = set()
    # '', '.MD', '.txt', '.php-dist', '.sql', '.md', '.ep', '.php', '.gan', '.css'

    filegraph = nx.DiGraph()

    for cid, commit in enumerate(raw.commits):
        raw_creations = [info['path'] for info in raw.commits[cid]['info'] if info['type'] == RawRepo.TYPE_NEW]
        for path in raw_creations:
            if path in filegraph:
                attrs = filegraph.node[path]
                if 'created' in attrs:
                    attrs['created'].append(cid)
                    pass
                else:
                    pass
                    #print("not in created")
            else:
                #attrs = {'created': []}
                attrs = {'created': [cid]}
            filegraph.add_node(path, attr_dict=attrs)

        raw_renames = {info['from']:info['to'] for info in raw.commits[cid]['info'] if info['type'] == RawRepo.TYPE_RENAME}
        for fr, to in raw_renames.items():
            filegraph.add_edge(fr, to)
            filegraph.edge[fr][to]['via'] = cid
            #filegraph.edge[fr][to]['label'] = cid
            #filegraph.add_edge(fr, to, attr_dict={'via':cid})

        raw_modified = [info['path'] for info in raw.commits[cid]['info'] if info['type'] == RawRepo.TYPE_MODIFIED]
        for path in raw_modified:
            attrs = filegraph.node[path]
            if 'modified' in attrs:
                attrs['modified'].append(cid)
            else:
                attrs['modified'] = [cid]
            filegraph.add_node(path, attr_dict=attrs)

        raw_mod_rename = {info['from']:info['to'] for info in raw.commits[cid]['info'] if info['type'] == RawRepo.TYPE_RENAME|RawRepo.TYPE_MODIFIED}
        for fr, to in raw_mod_rename.items():
            filegraph.add_edge(fr, to)
            filegraph.edge[fr][to]['via'] = cid
            attrs = filegraph.node[fr]
            if 'modified' not in attrs:
                attrs['modified'] = []
            attrs['modified'].append(cid)
            filegraph.add_node(fr, attr_dict=attrs)

    #nx.drawing.nx_pydot.write_dot(filegraph, 'filenames.dot')
    nx.readwrite.gml.write_gml(filegraph, 'filenames.gml')

    def get_predecessor_of_path(filegraph, raw, path, cid):
        candidates = filegraph.node[path]['modified'] + filegraph.node[path]['created']
        candidates = [c for c in candidates if c < cid]
        candidates.sort()
        candidates.reverse()
        print("candidates", candidates)
        for c in candidates:
            if path in raw.commits[c]['contents']:
                print("found candidate", c)
                return c, path

        print("ERROR predec")
        sys.exit()
        # TODO try to iterate older paths of path
        return None

        #print("BEGIN ------")
        #for pred in filegraph.predecessors_iter(path):
            #pass
            #print("pred", pred)
            #print(filegraph.node[pred])
        #print("END --------")

    #for cid, commit in enumerate(raw.commits[:100]):
        #if cid < 60:
            #continue
        ##print(Commit(raw, cid))
        #print("")
        #print("-----")
        #print("cid", cid)
        #if len(commit['contents']) > 10:
            #continue
        #for info in commit['info']:
            #if info['type'] == RawRepo.TYPE_NEW:
                #print("created", info['path'])
                #if None != commit['contents'][info['path']]:
                    #print("file of size", len(commit['contents'][info['path']]))
            #elif info['type'] == RawRepo.TYPE_MODIFIED:
                #path = info['path']
                #print("path", path)
                #if path in filegraph.node:
                    #cid2, path2 = get_predecessor_of_path(filegraph, raw, path, cid)
                    #if path in commit['contents']:
                        #text1 = raw.commits[cid]['contents'][path].decode('utf-8')
                        ##if len(text1) > 12000:
                            ##continue
                        #text2 = raw.commits[cid2]['contents'][path2].decode('utf-8')
                        #print("compare", path2, "->", path)
                        ##lev = jf.damerau_levenshtein_distance(text1, text2)
                        ##lev = jf.levenshtein_distance(text1, text2)
                        ##if lev == 0:
                            ##print("ERROR, equal len", len(text1))
                            ##sys.exit()
                        ##print("lev", lev)
                #else:
                    #print("NOT in graph")

##print(raw._get_files_from_sha('7a54b58773d1412cf92ee4f9e3ec92a60490ed9b', ['src/functions/base/functions.php']))
#print(raw.commits[62]['contents'])
