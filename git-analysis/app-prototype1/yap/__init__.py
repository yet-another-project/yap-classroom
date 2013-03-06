__all__ = ["RawRepo", "TopoRepo", "TopoPlot", "Commit", "compact", "extract", "bits", "iter_trend"]
from .RawRepo import RawRepo
from .Commit import Commit
from .TopoRepo import TopoRepo
from .TopoPlot import TopoPlot
import inspect

def compact(*names):
    caller = inspect.stack()[1][0] # caller of compact()
    vars = {}
    for n in names:
        if n in caller.f_locals:
            vars[n] = caller.f_locals[n]
        elif n in caller.f_globals:
            vars[n] = caller.f_globals[n]
    return vars

def extract(vars):
    caller = inspect.stack()[1][0] # caller of extract()
    for n, v in vars.items():
        caller.f_locals[n] = v   # NEVER DO THIS ;-)

def bits(i,n): return tuple((0,1)[i>>j & 1] for j in range(n-1,-1,-1)) 

def iter_trend(ranks):
    prev_rank = ranks[0]
    for cid, rank in enumerate(list(ranks)[1:]):
        diff = rank - prev_rank
        if diff > 0:
            yield cid+1, 1
        elif diff < 0:
            yield cid+1, -1
        else:
            yield cid+1, 0
        prev_rank = rank
