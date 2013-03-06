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

        if 'Merge' in r:
            self.merge = r['Merge']

    def __str__(self):
        metas = ['modifications', 'renames', 'mod_and_renames', 'deletes',
                 'pagerank', 'pagerank_trail', 'pagerank_trail_len', 'pagerank_trend', 'trail_data']

        t = """Commit ({0.cid}): {0.sha}
Message: ""{0.message}""
Identity ({0.identity_no}): {0.identity[author_name]} <{0.identity[author_email]}>
""".format(self)

        if self.merge != None:
            t += """Merge: {0.merge}
""".format(self)

        t += "Classes: " + str(self.raw.get_classes_of_commit(self.cid)) + "\n"

        for meta in metas:
            if meta in self.raw.commits[self.cid]:
                t += meta + ": " + str(self.raw.commits[self.cid][meta]) + "\n"

        return t
