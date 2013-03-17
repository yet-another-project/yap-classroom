from yap import *
from optparse import OptionParser
import ast
import configparser

# load configs
config = configparser.ConfigParser()
config.read('prototype1.ini')

MYLIB_PATH = config['Directories']['REPO_LOCATION']
CACHE_DIR = config['Directories']['CACHE_DIR']

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
