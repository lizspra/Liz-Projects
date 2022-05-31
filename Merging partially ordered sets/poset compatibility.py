#!/usr/bin/env python
# coding: utf-8

# In[1]:


import networkx as nx
import numpy as np
import lattice as lat
import setsystem as ss
import itertools as it
from itertools import combinations
import more_itertools as mtools #want to use more_itertools.powerset
from tabulate import tabulate
import random


# In[2]:


def freeze_sets(L): #inputs a list of sets (or a list of tuples) and outputs the same list as frozensets
    J=[]
    for i in range(len(L)):
        J.append(frozenset(L[i])) 
    return J

def booleandag(S): #input a set and output a DAG which is the boolean lattice obatined from the power set of S
    P = list(mtools.powerset(S))
    P = freeze_sets(P)
    return lat.subsetdag(P)

#the following is a pseudo-random DAG, where choice of n,m,p yeilds varying results
#Note that if p and m large, then WHP random_DAG(n,m,p)=sinlge vtx
#n is number of vertices in output, m is number of vertices used to generate random graph with edge prob. p
def random_DAG(n,m,p): #outputs a DAG on n vertices obtained from the condensation of a directed G(m,p)
    x=0
    while x != n:
        D = nx.gnp_random_graph(m, p, seed=None, directed=True)
        C = nx.condensation(D)
        x = nx.number_of_nodes(C)
    mapping = dict(zip(C.nodes(), sorted(C.nodes(), key=lambda k: random.random()))) #randomly permutes nodes since condensation reordered the vtx in some predictable way
    return nx.relabel_nodes(C, mapping)

#inputs a dictionary of intervals (ex. {1: [1,4], 2: [0,7]}) and outputs the DAG with vertex set from the dictionary key and an edge between intervals based on the weak interval order (i.e. [a,b]<=[c,d] iff a<=c and b<=d) 
def weak_interval_DAG(intervals): 
    G = nx.DiGraph()
    G.add_nodes_from(intervals)
    for key in it.combinations(intervals.keys(), 2):
        if intervals[key[0]][0]<=intervals[key[1]][0] and intervals[key[0]][1]<=intervals[key[1]][1]:
            G.add_edge(key[0],key[1]) 
        if intervals[key[1]][0]<=intervals[key[0]][0] and intervals[key[1]][1]<=intervals[key[0]][1]:
            G.add_edge(key[1],key[0]) 
    return G


# In[3]:


#Inputs a list of DAGS
#Outputs: verbose: Edge and vtx dsitribution, sum, union, and condenstion statistics
#         print_compatibility: Edge and vtx compatibilities
def order_compatibility(Digraphs, verbose = True, print_compatability = True, print_compatability_only = False): 
    G = nx.DiGraph()
    sum_vert  = 0
    sum_edges = 0
    list_of_orders = []
    list_of_sizes = []
    for D in Digraphs:
        sum_vert = sum_vert + D.number_of_nodes()
        sum_edges = sum_edges + D.number_of_edges()
        G = nx.compose(G,D)
        list_of_orders.append(D.number_of_nodes())
        list_of_sizes.append(D.number_of_edges())
    C = nx.condensation(G)
    if print_compatability_only == True:
        return C.number_of_edges()/G.number_of_edges()
    if verbose == True:
        print(tabulate([['Vertices', list_of_orders, sum_vert, G.number_of_nodes(),C.number_of_nodes()], ['Edges', list_of_sizes, sum_edges,G.number_of_edges(),C.number_of_edges()]], headers=['','Distribution','Sum', 'Union', 'Condensation']))
    if print_compatability == True:
        print('Vertex compatability ', C.number_of_nodes()/G.number_of_nodes())
        print('Edge compatability ', C.number_of_edges()/G.number_of_edges())
    return C


# In[4]:


#Example: chain vs itself
D1 = nx.DiGraph([(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)])
order_compatibility([D1,D1])


# In[5]:


#Example: chain vs itself vs itself 
D1 = nx.DiGraph([(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7)])
order_compatibility([D1,D1,D1])


# In[6]:


#Example: chain vs its reverse chain
D1 = nx.DiGraph([(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)])
D2 = nx.DiGraph([(1,0),(2,1),(3,2),(4,3),(5,4),(6,5),(7,6),(8,7),(9,8)])
order_compatibility([D1,D2])


# In[7]:


#Example: chain vs anti-chain
D1 = nx.DiGraph([(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7)])
D2 = nx.DiGraph() 
D2.add_nodes_from([0,1,2,3,4,5,6,7])
order_compatibility([D1,D2])


# In[8]:


#Example: chain 0...9 vs edge (9,0)
D1 = nx.DiGraph([(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)])
D2 = nx.DiGraph([(9,0)])
D2.add_nodes_from([1,2,3,4,5,6,7,8])
order_compatibility([D1,D2])


# In[9]:


#Example: chain 0...9 vs edge (3,0)
D1 = nx.DiGraph([(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)])
D2 = nx.DiGraph([(3,0)])
D2.add_nodes_from([1,2,4,5,6,7,8,9])
order_compatibility([D1,D2])


# In[10]:


#Example: Boolean DAG vs. chain 0..7
S1 = {1,2,3}
D1 = booleandag(S1)
print(D1.nodes())
D1 = nx.convert_node_labels_to_integers(D1)

D2 = nx.DiGraph([(1,0),(0,2),(2,3),(3,4),(4,5),(5,6),(6,7)])

order_compatibility([D1,D2])


# In[11]:


#Example: Boolean DAG vs random DAG 
S1 = {1,2,3}
D1 = booleandag(S1)
D1 = nx.convert_node_labels_to_integers(D1)

i = 0
L=[]
E=[]
n = 10000 #numb of iterations
while i <= n:
    R = random_DAG(8,10,.25)
    L.append(order_compatibility([D1,R], print_compatability_only = True))
    i = i+1
    
print(sum(L)/n)


# In[12]:


#Example: Boolean DAG vs lexicalgraphic 
S1 = {1,2,3}
D1 = booleandag(S1)
D1 = nx.convert_node_labels_to_integers(D1)

D2 = nx.DiGraph([(1,0),(0,4),(4,7),(7,5),(5,2),(2,6),(6,3)])

order_compatibility([D1,D2])


# In[13]:


#Example: Boolean DAG vs lexicalgraphic 
S1 = {1,2,3}
D1 = booleandag(S1)
D1 = nx.convert_node_labels_to_integers(D1)

D2 = nx.DiGraph([(0,1),(4,0),(7,4),(5,7),(2,5),(6,2),(3,6)])

order_compatibility([D1,D2])


# In[ ]:





# In[ ]:




