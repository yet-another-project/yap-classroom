import yap

class Commit:
    cid = None
    sha = None
    message = None
    identity = None
    identity_no = None
    touched_files = None
    merge = None

    raw = None

    def __init__(self, raw, cid):
        r = raw.commits[cid]

        self.raw = raw

        self.cid = cid
        self.sha = r['sha']
        self.message = r['message']
        self.identity_no = r['identity']
        self.identity = raw.identities[self.identity_no]
        self.touched_files = [i['path'] for i in r['info'] if 'path' in i]
        self.touched_files += [i['from'] for i in r['info'] if 'from' in i]
        self.touched_files += [i['to'] for i in r['info'] if 'to' in i]

        if 'Merge' in r:
            self.merge = r['Merge']

    def __str__(self):
        metas = ['pagerank', 'pagerank_trail', 'pagerank_trail_len', 'pagerank_trend', 'trail_data', 'parent', 'dirty', 'flags', 'info']

        shown = ['message', 'sha', 'identity', 'from', 'to', 'path'] + metas

        t = """Commit ({0.cid}): {0.sha}
Message: ""{0.message}""
Identity ({0.identity_no}): {0.identity[author_name]} <{0.identity[author_email]}>
Files ({1}): {0.touched_files}
""".format(self, len(self.touched_files))
        
        if self.merge != None:
            t += """Merge: {0.merge}
""".format(self)

        t += "Classes: " + str(self.raw.get_classes_of_commit(self.cid)) + "\n"

        for meta in metas:
            if meta in self.raw.commits[self.cid]:
                t += meta + ": " + str(self.raw.commits[self.cid][meta]) + "\n"

        notshown = []
        for meta in self.raw.commits[self.cid]:
            if meta not in shown:
                notshown.append(meta)
        t += "Not shown: " + str(notshown) + "\n"

        renames = {info['from']:info['to'] for info in self.raw.commits[self.cid]['info'] if info['type'] == yap.RawRepo.TYPE_RENAME}
        if len(renames):
            t += "Renames\n=======\n"
            for fr, to in renames.items():
                t += fr + " -> " + to + "\n"

        return t
