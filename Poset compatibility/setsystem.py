"""

setsystem.py

Functions for operations on sets of sets
Cliff Joslyn, MAY 2021

"""

import networkx as nx
import numpy as np
from math import *

### Set operations

# l is an nd.array of positive integers
def kappa(l):
    if len(l) == 1:
        return 1
    else:
        return log2(len(l)) / log2(sum(l))


def smoothness(l):
    if len(l) == 1:
        return 1
    else:
        f = l / sum(l)
        return -np.sum(f * np.log2(f)) / log2(len(l))


def listunion(l1, l2):
    return list(set(l1) | set(l2))


def listintersection(l1, l2):
    return list(set(l1) & set(l2))


def jaccard(x, y):
    return len(x.intersection(y)) / len(x.union(y))


def lefts(x, y):
    return len(x.difference(y)) / len(x.union(y))


def rights(x, y):
    return len(y.difference(x)) / len(x.union(y))


def powerset(s):
    l = len(s)
    x = [{e for e, b in zip(s, f"{i:{l}b}") if b == "1"} for i in range(2 ** l)]
    # 	x=[{frozenset(e) for e, b in zip(s, f'{i:{l}b}') if b == '1'} for i in range(2 ** l)]
    return x


# 	return {
# 		{e for e, b in zip(s, f'{i:{l}b}') if b == '1'}
# 		for i in range(2 ** l)
# 	}


### Setlist operations

# Setlist: list of frozen sets
# l: lambda function taking two sets and returning another
# Returns: list of frozen sets, recursive closure of l
def closure(setlist, l, removeempty=False, sortsl=True):
    x = [
        [l(setlist[i], setlist[j]) for i in range(0, j)] for j in range(0, len(setlist))
    ]
    nextlist = list(set(setlist + [i for s in x for i in s]))
    if len(nextlist) != len(setlist):
        setlist = list(set(setlist + closure(nextlist, l)))
    if (removeempty) and frozenset() in setlist:
        setlist.remove(frozenset())
    if sortsl:
        return sortsetlist(setlist)
    else:
        return setlist


def intclose(setlist, removeempty=False):
    return closure(setlist, lambda x, y: x.intersection(y), removeempty)


def intglobal(setlist):
    ret = frozenset()
    for n in setlist:
        ret = ret.intersection(n)
    return ret


def unionclose(setlist, removeempty=False):
    return closure(setlist, lambda x, y: x.union(y), removeempty)


def unionglobal(setlist):
    ret = frozenset()
    for n in setlist:
        ret = ret.union(n)
    return ret


def topology(setlist, removeempty=False):
    return unionclose(intclose(setlist, removeempty), removeempty)


# Input: setlist
# Output: sorted setlist
def sortsetlist(setlist):
    return [frozenset(t) for t in sorted([list(frozenset(sorted(s))) for s in setlist])]


### Sheaf functions


def edgetovertexw(H):
    vw = {
        n.uid: (
            sum(e.ew / len(e.elements) for e in H.nodes[n.uid].memberships.values())
        )
        for n in H.nodes()
    }
    return vw


"""
#	vw={}
#	for n in H.nodes():
#		vw[n.uid]=sum(e.ew/len(e.elements) for e in H.nodes[n.uid].memberships.values())
#		vw[n.uid]=sum(e.ew for e in H.nodes[n.uid].memberships.values())
#		vw[n.uid]=[(e.ew,len(e.elements)) for e in H.nodes[n.uid].memberships.values()]
#		vw[n.uid]= H.nodes[n.uid].memberships
"""

# Assignment over a weight dictionary
def assignment(node, vwd):
    return sum(vwd[i] for i in node) / len(node)


# Assignment over a weight function
def assignmentf(node, vwf):
    return sum(vwf(i) for i in node) / len(node)


def radius(D, wf, debug=False):
    maxnorm = 0
    maxes = []
    for n1 in D:
        if n1 == frozenset():
            continue
        n1ass = assignmentf(n1, wf)
        for n2 in nx.descendants(D, n1):
            if n2 == frozenset():
                continue
            n2ass = assignmentf(n2, wf)
            norm = np.linalg.norm(n1ass - n2ass)
            res = (norm, n1, n1ass, n2, n2ass, sortsetlist(interval(D, n1, n2)))
            if debug:
                print(res)
            if norm == maxnorm:
                maxes.append(res)
            elif norm > maxnorm:
                maxnorm = norm
                maxes = [res]
    return maxes


"""

def upset( D, n ):
	a = [n]
	x = [ i for i in D.predecessors(n) ]
	if x != []:
		for y in x:
			a = listunion( a, upset(D,y) )
	return(a)

def downset( D, n ):
	a = [n]
	x = [ i for i in D.successors(n) ]
	if x != []:
		for y in x:
			a = listunion( a, downset(D,y) )
	return(a)


AdjacencyView(
	{
		frozenset({2, 5}):
			{
				frozenset({1, 2, 4, 5}): {},
				frozenset({2, 3, 5, 6}): {}
			},
		frozenset({1, 2, 4, 5}): {},
		frozenset({2, 3, 5, 6}): {}
	}
)
"""

# importlib.reload(ss)
