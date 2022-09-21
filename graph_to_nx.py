"""functions for transforming spatial data into network and vice versa """

import networkx as nx
import geopandas
from shapely.geometry import Point


def gdf_to_nx(gdf_network):
    # generate graph from GeoDataFrame of LineStrings
    net = nx.MultiDiGraph()
    net.graph['crs'] = gdf_network.crs
    fields = list(gdf_network.columns)
    # fields = ['ID_TRC_int','lts_final', 'signed_sl', 'slope_edit', 'lts_imp', 'geometry']

    for index, row in gdf_network.iterrows():
        first = row.geometry[0].coords[0]
        last = row.geometry[0].coords[-1]

        data = [row[f] for f in fields]
        attributes = dict(zip(fields, data))
        net.add_edge(first, last, **attributes)

    return net


def nx_to_gdf(net, nodes=True, edges=True, crs=2950):
    # generate nodes and edges geodataframes from graph
    if nodes is True:
        print('nodes')
        node_xy, node_data = zip(*net.nodes(data=True))

        gdf_nodes = geopandas.GeoDataFrame(list(node_data), geometry=[Point(i, j) for i, j in node_xy])
        print("gdf_nodes: ", len(gdf_nodes))
        gdf_nodes.crs = crs

    if edges is True:
        print('edges')
        starts, ends, edge_data = zip(*net.edges(data=True))
        gdf_edges = geopandas.GeoDataFrame(list(edge_data))
        print("gdf_edges: ", len(gdf_edges))
        gdf_edges.crs = crs

    if nodes is True and edges is True:
        print('1')
        return gdf_nodes, gdf_edges
    elif nodes is True and edges is False:
        print('2')
        return gdf_nodes
    else:
        print('3')
        return gdf_edges



