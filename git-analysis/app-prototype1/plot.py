import yap
import networkx as nx

from functools import reduce
from time import time
START_TIME = time()
import pickle
import os
import numpy as np
import scipy as sp
import collections
from optparse import OptionParser

MYLIB_PATH = '/home/flav/projects/yet-another-project/My-library'
CACHE_DIR = '/home/flav/projects/yet-another-project/yap-analysis/data'

raw = yap.RawRepo(MYLIB_PATH, cachedir=CACHE_DIR)
topo = yap.TopoRepo(raw)

topo.build_pagerank_trails()
topo.build_pagerank_trails_stdev()
lonewolf_scores, interactivity_scores, team_productivity = topo.build_team_noteam()

topoplot = yap.TopoPlot(topo)
opts = OptionParser()
opts.add_option("-t", "--trends", action="store_true", default=False,
                help="Generate the pagerank trend groups")
opts.add_option("-r", "--ranks", action="store_true", default=False,
                help="Generate the pagerank ranks")
opts.add_option("--development", action="store_true", default=False,
                help="Development feature")
opts.add_option("--topology", action="store_true", default=False,
                help="Create topology GML")

(options, args) = opts.parse_args()

if options.trends:
    userstyles = {
            0: {'marker':'.', 'color': 'r', 'linestyle': 'None'},
            1: {'marker':'.', 'color': 'g', 'linestyle': 'None'},
        }
    topoplot.plot_pagerank_trendgroups('trendgroups', colorizeusers=True, userstyles=userstyles)
if options.ranks:
    topoplot.plotranks('ranks')
if options.topology:
    nx.readwrite.gml.write_gml(topo, 'topology.gml')
    nx.readwrite.gexf.write_gexf(topo, 'topology.gexf')
if options.development:
    for cid, commit in enumerate(raw.commits):
        print("cid", cid)
        if len(commit['renames']):
            print("commit['renames']", commit['renames'])
        print("commit['modifications']", commit['modifications'])
        deletes = [path for path, content in commit['contents'].items() if content==None]
        if len(deletes):
            print("deletes", deletes)
