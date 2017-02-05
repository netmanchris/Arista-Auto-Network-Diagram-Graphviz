#!/usr/bin/env python2
import pyeapi
from graphviz import Digraph

pyeapi.load_config('.eapi.conf')

#test devices in lab see .eapi.conf file in same directory for connection parameters
switches = ['Arista249', 'Arista250']



def gather_topos(devices):
    """
    Function which takes a list of devices as input and runs the lldp neigh command against them
    using the Arista pyeapi library
    :param devices:
    :return: list of lldp neigh output
    """
    topo = []
    for switch in devices:
        node = pyeapi.connect_to(switch)
        output = node.enable('show lldp neighbors')
        device_neigh = {'name' :switch, 'neighbors': (output[0]['result']['lldpNeighbors'])}
        topo.append(device_neigh)
    return topo

# runs the gather_topos using the switches VAR from above and captures in the all_devs_neigh... VAR
all_devs_neighbors_output = gather_topos(switches)


def create_topo(dev_name, neigh_list):
    """
    Function to take the neighbor list output from a single device and split into the nodes and edges for DOT consumption
    :param dev_name:
    :param neigh_list:
    :return:
    """
    nodes = [dev_name]
    edges = []
    for neighbor in neigh_list:
        nodes.append(neighbor['neighborDevice'])
        edges.append([dev_name, neighbor['neighborDevice'], neighbor['neighborPort'] + "-" + neighbor['port'] ])
    return [nodes, edges]

def join_neighbors(all_devs_neighbors_output):
    """
    function to take output of all_devs_neighbors_output VAR and process them through the create topo function above
    :param all_devs_neighbors_output:
    :return:
    """
    links_list = []
    for device in all_devs_neighbors_output:
        dev_links = create_topo(device['name'], device['neighbors'])
        links_list.append(dev_links)
    return links_list

#gen full neighbors list and edge links
full = join_neighbors(all_devs_neighbors_output)

def clean_full_list(full_list):
    """Function to eliminate multiple nodes from the output of the join_neighbors"""
    cleaned_node = []
    cleaned_edge = []
    for dev in full_list:
        for node in dev[0]:
            if node in cleaned_node:
                continue
            else:
                cleaned_node.append(node)
        for edge in dev[1]:
            cleaned_edge.append(edge)
    return [cleaned_node, cleaned_edge]

my_topo = clean_full_list(full)


#Creating the Topo graphic

def make_topology(network_name, mytopo):
    dot = Digraph(comment=network_name, format='png')
    dot.attr('node', shape='box')
    dot.attr('node', image="./images/switch1.png")
    dot.attr('edge', weight='10')
    dot.attr('edge', arrowhead='none')
    dot.body.append(r'label = "\n\nMy Prettier Network Diagram"')
    dot.body.append('fontsize=20')
    for i in mytopo[0]:
        dot.node(i)
    for i in mytopo[1]:
        dot.edge(i[0], i[1], i[2])
    return dot


dot = make_topology("My New Network", my_topo)

#run the following command if you want to see the object in DOT format
#print dot.source

#render to file
dot.render(filename='MultiTopo')
