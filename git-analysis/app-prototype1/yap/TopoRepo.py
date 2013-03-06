import networkx as nx
import yap
import numpy as np
import collections

class TopoRepo(nx.DiGraph):
    raw = None
    start = None
    categories = None

    pagerank_trails = None
    pageranks = None
    pagerank_trails_stdev = None

    lonewolf_scores = None
    interactivity_scores = None
    team_productivity = None

    pagerank_alpha = 0.75

    def __init__(self, raw):
        nx.DiGraph.__init__(self)

        self.raw = raw

        for cid, commit in enumerate(raw.commits):
            self.add_node(cid, attr_dict=commit)

            if 'Merge' in commit:
                merged = [number for number in commit['Merge'] if number >= 0]
                node_attrs = {}
                if len(merged) == 0:
                    node_attrs['only_merged'] = True
                elif len(merged) == len(commit['Merge']):
                    node_attrs['only_merge'] = True
                else:
                    node_attrs['mixed_merge'] = True

                self.add_node(cid, attr_dict=node_attrs)

                for merge in merged:
                    self.add_edge(merge, cid, attr_dict={'is_merge': True})

            if 'parent' in commit:
                self.add_edge(commit['parent'], cid, attr_dict={'is_parent': True})

    def connected_components(self):
        return nx.algorithms.components.connected.connected_components(self.to_undirected())

    def pagerank(self, **kwargs):
        return nx.algorithms.link_analysis.pagerank_alg.pagerank(self, **kwargs)
        #return nx.algorithms.link_analysis.pagerank_alg.pagerank_numpy(self, **kwargs)
        #return nx.algorithms.link_analysis.pagerank_alg.pagerank_scipy(self, **kwargs)

    def eig(self):
        lapl = nx.generalized_laplacian(self)
        return np.linalg.eig(lapl)

    def get_pageranks(self):
        if self.pageranks == None:
            self.pageranks = list(self.pagerank().values())
        return self.pageranks

    def build_pagerank_trails(self):
        prev_trend = -2

        ranks = self.get_pageranks()
        self.pagerank_trails = {}

        trail_id = -1

        for cid, trend in yap.iter_trend(ranks):
            if trend != prev_trend:
                trail_id += 1
                self.pagerank_trails[trail_id] = {'start': cid, 'end':cid}
            self.add_node(cid, attr_dict={'pagerank_trail':trail_id, 'pagerank_trend':trend, 'pagerank': ranks[cid]})
            self.pagerank_trails[trail_id]['end'] = cid
            prev_trend = trend

        self.add_node(0, attr_dict={'pagerank_trail':-1, 'pagerank_trend':0, 'pagerank_trail_len':0, 'pagerank': ranks[0]})

        stdev = np.std(list({tid: trail['end']-trail['start']+1 for tid, trail in self.pagerank_trails.items()}.values()))
        self.pagerank_trails_stdev = stdev

        for cid in range(1, len(self.nodes())):
            tid = self.node[cid]['pagerank_trail']
            trail = self.pagerank_trails[tid]
            length = trail['end'] - trail['start'] + 1
            self.node[cid]['pagerank_trail_len'] = length
            ###
            # commits belonging to a trail that has its length over the standard deviations are either
            #  - commits where the members have closely worked together
            #  - or commits where the members have worked on different subsystems of the code base
            # XXX research if this assumption is true
            # XXX the "mergedness" also depends on how many team members there are, this should also be taken into account
            ###
            self.node[cid]['pagerank_trail_len_over_stdev'] = length >= stdev

    def build_pagerank_trails_stdev(self):
        for tid, trail in self.pagerank_trails.items():
            trail_ranks = self.pageranks[trail['start']:trail['end']]
            if trail_ranks:
                self.pagerank_trails[tid]['stdev'] = np.std(trail_ranks)
                self.pagerank_trails[tid]['median'] = np.median(trail_ranks)

    def build_team_noteam(self):
        longruns = collections.defaultdict(list)
        lonewolf_scores = collections.defaultdict(int)
        interactivity_scores = collections.defaultdict(int)
        team_productivity = collections.defaultdict(int)

        for tid, trail in self.pagerank_trails.items():
            classes = self.raw.get_classes_histogram_for_commits(range(trail['start'], trail['end']+1))
            size = trail['end']-trail['start']+1
            if 'user_changes' not in classes:
                clean = None in classes and size == classes[None]
                userid = self.raw.commits[trail['start']]['userid']
                very_long = size >= self.pagerank_trails_stdev
                just_long = False == very_long and size >= self.pagerank_trails_stdev/2 # TODO: get number of team members from raw
                score = size * (3 if very_long == True else (2 if just_long == True else 1))
                trail_data = {'size': size, 'clean': clean,
                    'very': very_long, 'just': just_long, 'start':trail['start'],
                    'end':trail['end']+1, 'tid':tid, 'userid':userid, 'score':score,
                    'alone':True}
                longruns[userid].append(trail_data)
                lonewolf_scores[userid] += score
                self.add_nodes_from(list(range(trail['start'], trail['end'])), trail_data=trail_data)
            elif 'user_changes' in classes and None in classes and classes[None] >= self.pagerank_trails_stdev/2: # TODO: get number of team members from raw
                very_long = size >= self.pagerank_trails_stdev
                just_long = False == very_long and size >= self.pagerank_trails_stdev/2 # TODO: get number of team members from raw
                commitsmap = { cid: self.raw.commits[cid]['userid'] for cid in range(trail['start'], trail['end']+1)}
                userids = list(commitsmap.values())
                hist = collections.Counter(userids)
                for userid, commit_counts in hist.items():
                    interactivity_factor = classes['user_changes'] * (commit_counts / size)
                    interactivity_scores[userid] += interactivity_factor 
                    nonecommits = [ cid for cid in commitsmap if userid == self.raw.commits[cid]['userid'] and None == self.raw.get_classes_of_commit(cid) ]
                    team_productivity[userid] += interactivity_factor * len(nonecommits)
                    trail_data = {'size': size, 'alone':False,
                        'very': very_long, 'just': just_long, 'start':trail['start'],
                        'end':trail['end']+1, 'tid':tid, 'userid':userid,
                        'commit_counts': commit_counts, 'interactivity_factor': interactivity_factor,
                        'nonecommits': nonecommits}
                    longruns[userid].append(trail_data)
                    self.add_nodes_from(list(range(trail['start'], trail['end'])), trail_data=trail_data)
        self.lonewolf_scores = lonewolf_scores
        self.interactivity_scores = interactivity_scores
        self.team_productivity = team_productivity
        self.longruns = longruns
        return lonewolf_scores, interactivity_scores, team_productivity

    def analyze_edges(self):
        edges = nx.algorithms.traversal.depth_first_search.dfs_edges(self)
        for node1, node2 in edges:
            print(yap.Commit(self.raw, node1))
            print(yap.Commit(self.raw, node2))
            print("---------------")
