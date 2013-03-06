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

MYLIB_PATH = '/home/flav/projects/yet-another-project/My-library'
CACHE_DIR = '/home/flav/projects/yet-another-project/yap-analysis/data'

raw = yap.RawRepo(MYLIB_PATH, cachedir=CACHE_DIR)
class_node_draw_props = {
        # identity_changes | user_changes
        # only_merge | only_merged | mixed_merge
        # late_merge
        # tagged
        # out_of_order
        ('identity_changes',): {'node_color': '#80F31F', 'node_size': 1000},
        ('mixed_merge',): {'node_color': '#A5DE0B', 'node_size': 1000},
        ('only_merge',): {'node_color': '#C7C101', 'node_size': 1000},
        ('only_merged',): {'node_color': '#E39E03', 'node_size': 1000},
        ('only_merge', 'identity_changes'): {'node_color': '#F6780F', 'node_size': 1000},
        ('only_merge', 'late_merge'): {'node_color': '#FE5326', 'node_size': 1000},
        ('out_of_order',): {'node_color': '#FB3244', 'node_size': 1000, 'node_shape': 'p'},
        ('out_of_order', 'identity_changes'): {'node_color': '#ED1868', 'node_size': 1000},
        ('out_of_order', 'mixed_merge'): {'node_color': '#D5078E', 'node_size': 1000},
        ('out_of_order', 'mixed_merge', 'identity_changes'): {'node_color': '#B601B3', 'node_size': 1000},
        ('out_of_order', 'mixed_merge', 'late_merge'): {'node_color': '#9106D3', 'node_size': 1000},
        ('out_of_order', 'only_merge'): {'node_color': '#6B16EC', 'node_size': 1000},
        ('out_of_order', 'only_merged'): {'node_color': '#472FFA', 'node_size': 1000},
        ('out_of_order', 'only_merged', 'identity_changes'): {'node_color': '#2850FE', 'node_size': 1000},
        ('out_of_order', 'only_merge', 'late_merge'): {'node_color': '#1175F7', 'node_size': 1000},
        ('tagged', 'mixed_merge'): {'node_color': '#039BE5', 'node_shape':'d', 'node_size': 2500},
        ('tagged', 'out_of_order', 'mixed_merge'): {'node_color': '#01BECA', 'node_shape':'d', 'node_size': 2500},
        ('user_changes',): {'node_color': '#0ADCA8', 'node_size': 1000},
        ('user_changes', 'mixed_merge'): {'node_color': '#1DF283', 'node_size': 1000},
        ('user_changes', 'out_of_order'): {'node_color': '#3AFD5D', 'node_size': 1000},
        ('user_changes', 'out_of_order', 'mixed_merge'): {'node_color': '#5CFD3A', 'node_size': 1000},
        ('user_changes', 'out_of_order', 'only_merge'): {'node_color': '#82F21E', 'node_size': 1000},
        ('user_changes', 'out_of_order', 'only_merged'): {'node_color': '#A7DD0A', 'node_size': 1000},
}

topo = yap.TopoRepo(raw)

topo.build_pagerank_trails()
topo.build_pagerank_trails_stdev()
lonewolf_scores, interactivity_scores, team_productivity = topo.build_team_noteam()

topoplot = yap.TopoPlot(topo)
userstyles = {
        0: {'marker':'.', 'color': 'r', 'linestyle': 'None'},
        1: {'marker':'.', 'color': 'g', 'linestyle': 'None'},
    }
#topoplot.plot_pagerank_trendgroups('trendgroups', colorizeusers=True, userstyles=userstyles)
#topoplot.plotranks('ranks')

topo.analyze_edges()
