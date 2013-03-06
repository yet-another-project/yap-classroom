import matplotlib.pyplot as plt
import numpy as np

class TopoPlot:
    topo = None

    def __init__(self, topo):
        self.topo = topo

    def plotranks(self, basename, alpha=0.85):
        pageranks = self.topo.pagerank(alpha=alpha, max_iter=500)
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111)

        legend = []
        legend_labels = []
        for name, tag in self.topo.raw.tags.items():
            line = plt.Line2D([tag, tag], [0, 100], label=name)
            ax.add_line(line)

        ax.plot(list(pageranks.keys()), list(pageranks.values()), marker='o', color='r', linestyle='None')

        legend.append(line)
        legend_labels.append("Tags")
        ax.legend(legend, legend_labels, loc='lower left')
        ax.set_xlim(0, len(self.topo.raw.commits)+10)
        ax.set_ylim(0, np.max(list(pageranks.values()))+0.001)
        fig.savefig(basename + '-' + str(alpha) + '.png')

    def plot_pagerank_trendgroups(self, basename, colorizeusers=False, userstyles={}):
        trails_lengths = [commit['pagerank_trail_len'] for cid, commit in self.topo.nodes(data=True) if 'pagerank_trail_len' in commit]
        trails_lengths_len = len(trails_lengths)
        trails_lengths_max = np.max(trails_lengths)
        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        legend = []
        legend_labels = []
        for name, tag in self.topo.raw.tags.items():
            line = plt.Line2D([tag, tag], [0, np.max(trails_lengths)+1], color='y')
            ax.add_line(line)

        legend.append(line)
        legend_labels.append("Tags")
        no_devs = 2 # TODO detect number of main devs

        if not colorizeusers:
            commits = ax.plot(trails_lengths, marker='.', color='b', linestyle='None') # TODO instead of plotting them en masse, do it by type and author, highlighting long runs and teamwork
            legend.append(commits[0])
            legend_labels.append("Commits")
        else:
            for uid, style in userstyles.items():
                trails_lengths_user = {cid:commit['pagerank_trail_len'] for cid, commit in self.topo.nodes(data=True) if 'pagerank_trail_len' in commit and commit['userid'] == uid}
                commits = ax.plot(list(trails_lengths_user.keys()), list(trails_lengths_user.values()), **style)
                main_id = self.topo.raw.users[uid]['main_identity']
                real_name = self.topo.raw.identities[main_id]['author_name']
                legend.append(commits[0])
                legend_labels.append(real_name)


        stdev_line = plt.Line2D([0, trails_lengths_len+1], [self.topo.pagerank_trails_stdev, self.topo.pagerank_trails_stdev], color='r')
        ax.add_line(stdev_line)
        legend.append(stdev_line)
        legend_labels.append("$\sigma$")

        stdev_line_bydevs = plt.Line2D([0, trails_lengths_len+1],
                [self.topo.pagerank_trails_stdev/no_devs, self.topo.pagerank_trails_stdev/no_devs], color='g', linestyle='--')
        ax.add_line(stdev_line_bydevs)
        legend.append(stdev_line_bydevs)
        legend_labels.append("$\\frac{\sigma}{d}$")

        from collections import Counter
        histo = sorted(Counter(trails_lengths).values())
        trails_h_median = np.median(list(histo))
        traillen_median_line = plt.Line2D([0, trails_lengths_len+1], [trails_h_median, trails_h_median])
        ax.add_line(traillen_median_line)
        legend.append(traillen_median_line)
        legend_labels.append("Median")

        ax.legend(legend, legend_labels, loc='upper right', borderaxespad=-1.)
        ax.set_xlim(0, trails_lengths_len+1)
        ax.set_ylim(0, trails_lengths_max+1)
        fig.savefig(basename + '.png')
