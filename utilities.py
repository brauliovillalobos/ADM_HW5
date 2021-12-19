import math
from collections import deque
from itertools import product
import multiprocessing as mp
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def get_version():
    print("Last-version")

def filter_by_time_interval(initial_time, final_time, graph):
    '''
    Function that filters a graph and leaves only those edges with a timestamp within the interval of 
    initial_time and final_time, defined by the user. 
    '''
    # instantiate a new graph/dict
    time_graph = {}
    # for each node in the graph
    for node in graph: 
        times = np.array(graph[node])[:,1] 
        #Get indexes of the timestamps that are within the desired time interval
        positions = np.where(np.bitwise_and(times >= initial_time, times <= final_time))
        positions = [el for pos in positions for el in pos]
        # get all edges associated with a specific node and redefine its edges
        # keep only those edges that were created within the desired time interval
        if  len([graph[node][i] for i in positions]) > 0:
            time_graph[node] = [graph[node][i] for i in positions] # if i % 5 == 0]
    return time_graph


def filter_by_users(users, graph):
    '''
    Function that filters a graph and leaves only those edges between two nodes both present in the users list. 
    '''
    # instantiate a new graph/dict
    user_graph = {}
    for node in users: 
        user_graph[node] = [t for t in graph[node] if t[0] in users] 
    return user_graph


def get_users(G):
    keys = set(G.keys())
    total_users = keys
    for k in keys.copy():
        nodes = set(np.array(G[k])[:,0])
        difference = nodes.difference(total_users)
        total_users.update(difference)
    return total_users


def get_total_graph(G, total_users):
    for node in total_users:
        if node not in G:
            G[node] = []
    return G

#################################################################################################################################

def dijkstra(graph, source):
    dist = dict()
    prev_nodes = dict()
    dist[source] = 0
    prev_nodes[source] = []
    Q = list(graph.keys())
    for v in graph:
        if v != source:
            dist[v] = math.inf
            prev_nodes[v] = list()
    while len(Q) > 0:
        # v := vertex in Q with min dist[v]
        d = {k: dist[k] for k in Q}
        v = min(d, key=d.get)
        Q.remove(v)
        for neighbor, t, weight in graph[v]:
            # each neighbor has this structure : (user2, time, weight)
            distance = dist[v] + weight
            if distance <= dist[neighbor]:
                dist[neighbor] = distance
                prev_nodes[neighbor].append(v)
    return dist, prev_nodes


# ITERATIVE ALGORITHM TO RETRIEVE THE PATHS ############################
# prev_nodes is the dict with parents array
def iter_paths(source, target, prev_nodes, distances):
    if distances[target] < math.inf:
        targets = list()
        order = deque()
        order.append(target)
        targets.append(target)
        lists = [[target]]
        while len(order) > 0:
            o_target = order.popleft()
            for t in prev_nodes[o_target]:
                if t not in targets:
                    targets.append(t)
                    order.append(t)
        for t in targets:
            if len(prev_nodes[t]) > 0 and prev_nodes[t] not in lists:
                lists.append(prev_nodes[t])
        return list(product(*lists))
    else:
        return []

    
# RECURSIVE ALGORITHM TO RETRIEVE THE PATHS - not used but left for completeness ############################
def get_paths(source, target, prev_nodes):
    if len(prev_nodes[target]) > 0 or target == source:
        paths = list()
        rec_paths(source, target, prev_nodes, [target], paths)
        return paths
    else:
        return []


def rec_paths(source, target, prev_nodes, cur_path, paths):
    # base case --> the source has been reached via reverse path
    if target == source:
        paths.append(cur_path)
    else:
        for prev in prev_nodes[target]:
            # to avoid loops
            if prev not in cur_path:
                rec_paths(source, prev, prev_nodes, cur_path + [prev], paths)



# PARALLEL AGORITHM TO COMPUTE THE BETWEENESS CENTRALITY ###############
def betweeness_centrality(G):
    pool = mp.Pool(mp.cpu_count())
    betweeness = dict()
    counter = 0
    # get the betweeness centrality for all the nodes
    for v in G:
        delta = pool.apply(delta_routine, args=(v, G))
        betweeness[v] = delta
        counter += 1
        if counter % 50 == 0:
            print(counter)
    pool.close()
    return betweeness


# -- SUB-ROUTINE FOR PARALLEL ALGO FOR BETWEENESS
def delta_routine(v, G):
    # for all the sources, but v, compute Dijkstra
    total_delta = 0
    for s in G:
        if s != v:
            # get all the paths information from source s
            dist, paths = dijkstra(G, s)
            # for all the targets, but s and v, get the shortest paths numbers
            for t in G:
                if t != v and t != s:
                    all_paths = iter_paths(s, t, paths, dist)
                    sigma_st = len(all_paths)
                    if sigma_st > 0:
                        v_path = [p for p in all_paths if v in p]
                        sigma_st_v = len(v_path)
                        delta_stv = sigma_st_v / sigma_st
                        total_delta += delta_stv
    return total_delta

####################################################################################

# DEGREE CENTRLITY ALGORITHM
def degree_centrality(G):
    degreeness = dict()
    users_number = len(G)
    for node in G:
        degreeness[node] = len(G[node])/users_number
    return degreeness

#####################################################################################
# PAGE RANK ALGORITHM

def reverse_graph(G):
    reverse = dict()
    for node in G:
        reverse[node] = []
    for parent in G:
        children = set([child[0] for child in G[parent]])
        for child in list(children):
            reverse[child] += [parent]
    return reverse


def initialize_pagerank(G):
    n = len(G)
    page_rank = dict()
    for node in G:
        page_rank[node] = 1 / n
    reversed = reverse_graph(G)
    return page_rank, reversed


def update_pagerank(G, reversed, page_rank):
    for node in G:
        new_rank = 0
        for parent in reversed[node]:
            # previous page_rank / len(out-going)
            new_rank += page_rank[parent] / len(G[parent])
        page_rank[node] = new_rank
    return page_rank


def page_ranking(G, iterations):
    page_rank, reversed_graph = initialize_pagerank(G)
    for i in range(iterations):
        page_rank = update_pagerank(G, reversed_graph, page_rank)
    return page_rank


# PARALLEL AGORITHM TO COMPUTE THE BETWEENESS CENTRALITY -- SUB-ROUTINE ###########################
def close_routine(node, G):
    dist, parents = dijkstra(G, node)
    return sum([1/d for d in dist.values() if d != 0])

# PARALLEL AGORITHM TO COMPUTE THE BETWEENESS CENTRALITY ###############
def closeness_centrality(G):
    pool = mp.Pool(mp.cpu_count())
    closeness = dict()
    n = len(G)
    # get the betweeness centrality for all the nodes
    for v in G:
        denominator = pool.apply(close_routine, args=(v, G))
        if denominator == 0:
            closeness[v] = 0
        else:
            closeness[v] = round((n - 1)/denominator, 4)
    pool.close()
    return closeness


###########################################################################################################
    
    
    
