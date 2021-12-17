import random
import math

def from_date_to_int(date):
    '''
    INPUT: (day,month,year)
    OUTPUT: correspondent integer
    '''
    if date[1]==2:
        integer=date[0]+date[1]*28+(date[2]-1970)*365
    if date[1] in [4,6,9,11]:
        integer=date[0]+date[1]*30+(date[2]-1970)*365
    else:
        integer=date[0]+date[1]*31+(date[2]-1970)*365
    return(integer)


def convert_interval(interval):
    '''
    INPUT= interval of time in format [(dd,mm,yyyy),(dd,mm,yyyy)] --> [start,end]
    OUTPUT: interval of time in format [encoded_start,encoded_end] where encoded are integers values
    '''
    new_int=[]
    for date in interval:
        new_int.append(from_date_to_int(date))
    
    return( new_int)

def filter_dictionary(dictionary,converted_interval): 
    '''
    INPUT: dictionary 
           interval of time encoded 
    OUTPUT: dictionary filtered that has just the interactions in that time interval
    '''
    filtered_dictionary={}
    for key,value in dictionary.items():
        for elem in value:
            if ( (elem[1]>=converted_interval[0] and elem[1]<converted_interval[1]) ): # or (elem[1]>converted_interval[2] and elem[1]<converted_interval[3]) ):
                try:
                    filtered_dictionary[key].append(elem)
                except:
                    filtered_dictionary[key]=[elem]
    return(filtered_dictionary)  

def final_transformation (filtered_dictionary):
    G={}
    # go through the dictionary
    for k,v in  filtered_dictionary.items():
        # slice the list attached to every element
        for value in v:
            # remove people that speaks with themselves
            if k!=value[0]:
                try:
                    #sum weight between the same nodes
                    previous= G[str(k)+','+str(value[0])]
                    G[str(k)+','+str(value[0])].append(previous+value[2])
                except:
                    G[str(k)+','+str(value[0])]=[value[2]]
    return G


#### KARGER


def contraction (G):
    '''
    INPUT: a graph 
    during every itertion also len(G) became len(G)-1
    OUTPUT: the graph in which I have contracted to random nodes 
    '''
    
    edge_between=random.choice(list(G))
    node1_to_merge=edge_between.split(',')[0]
    node2_to_merge=edge_between.split(',')[1]

    #delete edge between the two  nodes
    del G[edge_between]
    t=node1_to_merge+'|'+node2_to_merge
    

    G_new=G.copy()

    for k,v in G.items():
        
        #edges from node1_to_merge
        if k.split(',')[0]==node1_to_merge:
            if k in G_new:
                del G_new[k]
            try:
                previous=G_new[t+','+k.split(',')[1]]
                G_new[t+','+k.split(',')[1]]=v+previous
            except:
                G_new[t+','+k.split(',')[1]]=v

        #edges from node2_to_merge
        if k.split(',')[0]==node2_to_merge:
            if k in G_new:
                del G_new[k]
            try:
                previous=G_new[t+','+k.split(',')[1]]
                G_new[t+','+k.split(',')[1]]=v+previous
            except:
                G_new[t+','+k.split(',')[1]]=v

        #edges directed to node1_to_merge
        if k.split(',')[1]==node1_to_merge:
            if k in G_new:
                del G_new[k]
            try:
                previous=G_new[k.split(',')[0]+','+t]
                G_new[k.split(',')[0]+','+t]=v+previous
            except:
                G_new[k.split(',')[0]+','+t]=v

        #edges directet to node2_to_merge except the one that cinnect node1_to_merge and node2_to_merge
        if k.split(',')[1]==node2_to_merge:
            if k in G_new:
                del G_new[k]
            try:
                previous=G_new[k.split(',')[0]+','+t]
                G_new[k.split(',')[0]+','+t]=v+previous
            except:
                G_new[k.split(',')[0]+','+t]=v

    return G_new
        

def iteration(G,s,t):
    '''
    INPUT= G
    OUTPUT= cut of G if it is ammisible, inf otherwise
    '''
    G_new=G.copy()
    while len(G_new)>1:
        G_new=contraction(G_new)


    ###check if it  is a valid cut: s and t need to be in two different partition. I store the partitions because they are necessary for the visualization
    for k,v in G_new.items():
        partition1=k.split(',')[0]
        partition2=k.split(',')[1]

    elements=[x for x in partition1.split('|')]
    cont=0
    for elem in elements:
        if (elem==s or elem==t):
            cont+=1

    if cont==1:
        cut=sum(list(G_new.values())[0]) 
    else:
        cut=math.inf
    
    return cut,partition1,partition2

def Karger(G,s,t):

    # check if s and t are in the graph otherwise we can not compute the algorithm
    conts=0
    contt=0
    for k,v in G.items():
        if (k.split(',')[0]==s or k.split(',')[1]==s):
            conts+=1
        if (k.split(',')[0]==t or k.split(',')[1]==t):
            contt+=1
    if (conts<1 or contt<1):
        return(' users not in the graph')

    #### If we can efctively run the algorithm###   
    min_cut=math.inf
    partitionA={}
    partitionB={}
    # I ran len G times even if it is not correct just for time reason but we can change this parameter
    for i in range(len(G)):
        cut,partition1,partition2=iteration(G,s,t)
        if cut<min_cut:
            min_cut=cut
            partitionA=partition1
            partitionB=partition2
            
    return(min_cut,partitionA,partitionB)
