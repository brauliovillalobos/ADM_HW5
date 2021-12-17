import math
from collections import deque
from itertools import product
import multiprocessing as mp


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



# parallel algorithm to get betweeness centrality
def betweeness_centrality(G):
    pool = mp.Pool(mp.cpu_count())
    betweeness = dict()
    counter = 0
    # get the betweeness centrality for all the nodes
    for v in G:
        delta = pool.apply(delta_routine, args=(v, G))
        betweeness[v] = delta
        counter += 1
        if counter % 5 == 0:
            print(counter)
    pool.close()
    return betweeness


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



def degree_centrality(G):
    degreeness = dict()
    users_number = len(G)
    for node in G:
        degreeness = len(G[node])/users_number
    return degreeness


    
    
    
    
