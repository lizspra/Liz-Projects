"""lattice.py

Functions for lattice operations modeled as a NetworkX DAG
Cliff Joslyn, MAY 2021

"""
import networkx as nx
import setsystem as ss

from math import log2
from typing import List, Set, Any, Tuple
from collections import defaultdict

# TODO: how do we enforce acyclicity?
def subsetdag(setlist: List[Set]) -> nx.DiGraph:
    """Creates a DAG given a list of sets

    Parameters
    ----------
    setlist : List[set]
        list of sets

    Returns
    -------
    nx.DiGraph
        a DAG of sets where an edge $s_1 \\then s_2$ means $s_1 \\subseteq s_2$
    """
    D = nx.DiGraph()
    for i in range(0, len(setlist)):
        for j in range(i + 1, len(setlist)):
            if setlist[i] == setlist[j]:
                continue
            if setlist[i] >= setlist[j]:
                D.add_edge(setlist[i], setlist[j])
            if setlist[i] <= setlist[j]:
                D.add_edge(setlist[j], setlist[i])
    return nx.transitive_reduction(D)


def uppersiblings(D, n):
    """uppersiblings(D,n): Return children of parents of node n in DAG D"""
    us = set()
    for p in D.predecessors(n):
        us = us.union(set(D.successors(p)))
    return us - {n}


def lowersiblings(D, n):
    """lowersiblings(D,n): Return parents of children of node n in DAG D"""
    ls = set()
    for s in D.successors(n):
        ls = ls.union(set(D.predecessors(s)))
    return ls - {n}


def siblings(D, n):
    """siblings(D,n): Union of lower and upper siblings of node n in DAG D"""
    return uppersiblings(D, n).union(lowersiblings(D, n))


def family(D, n):
    """family(D,n):Union of parents, children, and sibling of node n in DAG D"""
    return set(D.predecessors(n)).union(D.successors(n), siblings(D, n))


def upset(D, n):
    """upset( D, n ): Return ancestors of node n in DAG D"""
    return nx.ancestors(D, n) | {n}


def downset(D, n):
    """downset( D, n ): Return descendants of node n in DAG D"""
    return nx.descendants(D, n) | {n}


def hourglass(D, n):
    """hourglass( D, n ): Return upset(n) \\union downset(n) of node n in DAG D"""
    return downset(D, n).union(upset(D, n))


def comparable(D, n1, n2):
    """
    comparable( D, n1, n2 ):
    For nodes n1, n2 in DAG D, return:
            1 if n2 is reachable from n1
            -1 if n1 is reachable from n2
            0 if neither n1 nor n2 is reachable from the other
            2 if n1==n2
    """
    if n1 == n2:
        return 2
    elif n2 in upset(D, n1):
        return 1
    elif n2 in downset(D, n1):
        return -1
    else:
        return 0


def interval(D, n1, n2):
    """
    interval( D, n1, n2 ):
    For nodes n1, n2 in DAG D, return the nodes n reachable from n1 and reaching n2
    """
    return upset(D, n1).intersection(downset(D, n2))


def roots(D):
    """roots(D): Return nodes n in DAG d with indegree 0"""
    return {v for v, d in D.in_degree() if d == 0}


def leaves(D):
    """leaves(D): Return nodes n in DAG d with outegree 0"""
    return {v for v, d in D.out_degree() if d == 0}


def join(D, n1, n2):
    """join(D,n1,n2): Return the "first set" of nodes n in D reachable from both n1 and n2"""
    return leaves(D.subgraph(upset(D, n1).intersection(upset(D, n2))))


def meet(D, n1, n2):
    """join(D,n1,n2): Return the "first set" of nodes n in D reaching both n1 and n2"""
    return roots(D.subgraph(downset(D, n1).intersection(downset(D, n2))))


def chains(D):
    """chains(D): Return all paths between all leaves and all roots of DAG D"""
    chains = []
    for root in roots(D):
        for leaf in leaves(D):
            c = nx.all_simple_paths(D, root, leaf)
            chains.extend(c)
    return chains


def height(D):
    """height(D): Return max chain length in DAG D"""
    # 	return( max( [ len(c) for c in chains(D) ] ) )
    return nx.dag_longest_path_length(D) + 1


def upperbounded(D):
    """upperbounded(D): Return true iff DAG D has a single root"""
    return len(roots(D)) == 1


def lowerbounded(D):
    """lowerbounded(D): Return true iff DAG D has a single leaf"""
    return len(leaves(D)) == 1


def bounded(D):
    """bounded(D): Return true iff DAG D is both upper and lower bounded"""
    return upperbounded(D) and lowerbounded(D)


def atoms(D):
    """coatoms(D): Return all the chidlren of all the roots of DAG D"""
    return set().union(*[D.predecessors(y) for y in leaves(D)])


"""
def atoms(D):
	''' atoms(D): Return all the parents of all the leaves of DAG D '''
	a=set()
	for y in leaves(D):
		a=a.union( D.predecessors(y) )
	return( a )
"""


def coatoms(D):
    """coatoms(D): Return all the parents of all the leaves of DAG D"""
    return set().union(*[D.successors(y) for y in roots(D)])


"""
def coatoms(D):
	''' coatoms(D): Return all the chidlren of all the roots of DAG D '''
	a=set()
	for y in roots(D):
		a=a.union( D.successors(y) )
	return( a )
"""

"""
Class CDict:

	mb: Should be a class of course
		I'm using a dictionary to store what should be class attributes, no doubt

	Dictionary for a Digraph condensation and its DAG
	Cdict = { D:DAG, C:Condensation, h:height }
"""

# mb: Should be a constructor
def CDict(D):
    CD = {}
    CD["D"] = D
    CD["n"] = len(D)
    CD["C"] = nx.condensation(D)
    CD["h"] = lat.height(CD["C"])
    return CD


"""
mb: Since condensations and heights can be expensive, we also want
constructors which take them as inputs, not to be calculated. This is
what I do in my notebook
"""

# Return condensation component #
def cond_comp(Cdict, n):
    """
    cond_comp(Cdict,n):
    For node n in the graph of condensation dict Cdict, return its component number
    """
    return Cdict["comp"][n]


# Return a list of graph members of a condensation component
def cond_members(Cdict, c):
    """
    cond_members(Cdict,c):
    For component number c in the condensation dict Cdict, return all of its graph members
    """
    return list(Cdict["memb"][c])


# Return a list of lists of graph members of a list of condesation components
# mb: I have no idea if this kind of syntactic sugar over a list comprehension is wise
def cond_membersl(Cdict, l):
    """
    cond_membersl(Cdict,l):
    Takes a list l of component numbers in the condensation dict Cdict
    Returns a list of all of their graph members
    """
    return [cond_members(Cdict, c) for c in l]


def toprank(Cdict, n):
    """
    toprank(Cdict,n):
        Take node n in condensation dictionary Cdict
        Return max chain length down from any root of DAG
    """
    C = Cdict["C"]
    return height(C.subgraph(upset(C, cond_comp(Cdict, n))))


def botrank(Cdict, n):
    """
    botrank(Cdict,n):
    Take node n in condensation dictionary Cdict
    Return height minus max chain length up from any leaf of DAG
    """
    C = Cdict["C"]
    return Cdict["h"] - height(C.subgraph(downset(C, cond_comp(Cdict, n))))


def rank(Cdict, n):
    """
    rank(Cdict,n):
    Take node n in condensation dictionary Cdict
    Return interval between its top and bottom rank as a numeric tuple
    """
    return (toprank(Cdict, n), botrank(Cdict, n))


def rankn(Cdict, n):
    """
    rankn(Cdict,n):
    Take node n in condensation dictionary Cdict
    Return interval between its top and bottom rank as a numeric tuple,
            but proportional to (normalize by) the height
    """
    h = Cdict["h"]
    return ((toprank(Cdict, n) - 1) / h, (botrank(Cdict, n) + 1) / h)


"""
Ontology distance functions
"""


def IC(D, n):
    """IC(D,n): Returns the "information content" of node n in DAG D"""
    return -log2(len(downset(D, n)) / len(D))


def M(D, n1, n2):
    return max(IC(D, j) for j in join(D, n1, n2))


def LowerOrderDist(D, n1, n2):
    """
    LowerOrderDist(D,n1,n2):
            Return the lower order distance of nodes n1, n2 in DAG D
    """
    x = downset(D, n1)
    y = downset(D, n2)
    return len(x) + len(y) - 2 * len(x.intersection(y))


def UpperOrderDist(D, n1, n2):
    """
    UpperOrderDist(D,n1,n2):
            Return the upper order distance of nodes n1, n2 in DAG D
    """
    x = upset(D, n1)
    y = upset(D, n2)
    return len(x) + len(y) - 2 * len(x.intersection(y))


def UpperOrderDistN(D, n1, n2):
    """
    UpperOrderDistN(D,n1,n2):
            Return the normalized upper order distance of nodes n1, n2 in DAG D
    """
    x = upset(D, n1)
    y = upset(D, n2)
    return len(x) + len(y) - 2 * len(x.intersection(y))


def JCDist(D, n1, n2):
    """
    JCDist(D,n1,n2):
            Return the Jiang-Conrath measure of nodes n1, n2 in DAG D
    """
    return IC(D, n1) + IC(D, n2) - 2 * M(D, n1, n2)


def ResnickDist(D, n1, n2):
    """
    ResnickDist(D,n1,n2):
            Return the Resnick measure of nodes n1, n2 in DAG D
    """
    return 1 + M(D, n1, n2) / len(D)


def LinDist(D, n1, n2):
    """
    LinDist(D,n1,n2):
            Return the Resnick measure of nodes n1, n2 in DAG D
    """
    return 1 - 2 * M(D, n1, n2) / (IC(D, n1) + IC(D, n2))


# importlib.reload(lat)
