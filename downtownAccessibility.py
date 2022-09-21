"""

"""

from typing import Tuple
from build_nx import gdf_to_nx, nx_to_gdf
from calcSteepnessLevel import calc_SL, sl_signage
from funcs import decay_func, make_route_line, short_segments_smoothen
import networkx as nx
import geopandas
import pandas
import numpy
geopandas.options.display_precision = 9

# source = (298960.2725999993, 5040110.302200001)  point in downtown, messounive

class NetworkPath:
    def __init__(self, G: nx.MultiDiGraph, source: Tuple):
        # self.SG = None
        self.G = G
        self.source = source

    def subgraphGetter(self, attr_lts: str, cutoff_lts: int, attr_sl: str = None, cutoff_sl: float = None)->nx.MultiDiGraph:
        """
        :param attr_lts: name of the lts related field (String)
        :param cutoff_lts: the cutoff value for lts (int)
        :param attr_sl: name of the SL related field (String)
        :param cutoff_sl: the value for SL (3.5, 5)
        :return: a subgraph that satisfies the filters of LTS and SL
        """
        if attr_lts and attr_sl:  # or you could define a weight function
            SG = nx.MultiDiGraph([(u,v,d) for u,v,d in self.G.edges(data=True) if d[attr_lts] <= cutoff_lts and
                                d[attr_sl]<= cutoff_sl])
        elif attr_lts and not attr_sl:
            SG = nx.MultiDiGraph([(u, v, d) for u, v, d in self.G.edges(data=True) if d[attr_lts] <= cutoff_lts])
        return SG


if __name__ == '__main__':
    streets = geopandas.read_file(
        'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\accessibility\\data\\downtown_test.shp')
    # 'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\accessibility\\data\\downtown_ToAll_2.shp')
    print("number of lines: ", len(streets))

    streets[['lts', 'lts_c', 'lts_negD', 'length', 'slope','slope_edit']] = streets[['lts', 'lts_c','lts_negD','length', 'slope', 'slope_edit']].replace(numpy.nan, 0)
    streets['slope_edit'] = streets['slope_edit'].replace(-8888, 0)
    # streets['slope_edit'] = streets['slope_edit'].replace([-8888, numpy.nan], 0)  # or


    # Getting the source point in the network (Peel st & Messounive)
    source_coords = list(streets[streets['ID_TRC_int'] == 1260415]['geometry'].item().coords)[-1]

    print("Computing Steepness Level...")
    streets[['sl_35', 'sl_5', 'sl_65']] = streets.apply(lambda row: pandas.Series(calc_SL(row['length'], row['slope_edit'])),
                                               axis=1)
    streets['unsigned_sl'] = streets.apply(lambda row: min(row['sl_35'], row['sl_5'], row['sl_65']), axis=1)
    streets['signed_sl'] = streets.apply(lambda row: sl_signage(row['slope'], row['unsigned_sl']), axis=1)

    print("Transforming to networkX...")
    G = gdf_to_nx(streets)
    net = NetworkPath(G, source_coords)

    print("Computing Shortest Path...")
    # LTS 4 : shortest allowed path to other points on the network
    scenario_name = "lts4"
    subG_shortestPath = net.subgraphGetter("lts_final", 4)
    dist_dict, path_dict = nx.single_source_dijkstra(subG_shortestPath, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")

    print("Computing Scenario A1...")
    # A1. Current network limited to LTS1
    scenario_name = "lts1"
    subG_A1 = net.subgraphGetter("lts_final", 1)
    # net.set_shortestPath_value_toNode(subG_A1, "lts1")
    dist_dict, path_dict = nx.single_source_dijkstra(subG_A1, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")

    print("Computing Scenario A2...")
    # A2. Current network limited to LTS2
    scenario_name = "lts2"
    subG_A2 = net.subgraphGetter("lts_final", 2)
    # net.set_shortestPath_value_toNode(subG_A2, "lts2")
    dist_dict, path_dict = nx.single_source_dijkstra(subG_A2, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")

    print("Computing Scenario B1...")
    # B1. Current network limited to LTS1 and SL 5.0
    scenario_name = "lts1_sl5"
    subG_B1 = net.subgraphGetter("lts_final", 1, "signed_sl", 5)
    # net.set_shortestPath_value_toNode(subG_B1, "lts1_sl5")
    dist_dict, path_dict = nx.single_source_dijkstra(subG_B1, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")

    print("Computing Scenario B2...")
    # B2. Current network limited to LTS2 and SL 5.0
    scenario_name = "lts2_sl5"
    subG_B2 = net.subgraphGetter("lts_final", 2, "signed_sl", 5)
    # net.set_shortestPath_value_toNode(subG_B2, "lts2_sl5")
    dist_dict, path_dict = nx.single_source_dijkstra(subG_B2, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")


    print("Computing Scenario B3...")
    # B3. Current network limited to LTS1 and SL 3.5
    scenario_name = "lts1_sl3.5"
    subG_B3 = net.subgraphGetter("lts_final", 1, "signed_sl", 3.5)
    # net.set_shortestPath_value_toNode(subG_B3, "lts1_sl3.5")
    dist_dict, path_dict = nx.single_source_dijkstra(subG_B3, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")


    print("Computing Scenario B4...")
    # B4. Current network limited to LTS1 and SL 3.5
    scenario_name = "lts2_sl3.5"
    subG_B4 = net.subgraphGetter("lts_final", 2, "signed_sl", 3.5)
    # net.set_shortestPath_value_toNode(subG_B4, "lts2_sl3.5")
    dist_dict, path_dict = nx.single_source_dijkstra(subG_B4, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")


    print("Computing Scenario C1...")
    # C1. Improved network limited to LTS1 and SL 5.0.
    scenario_name = "imLts1_5"
    subG_C1 = net.subgraphGetter("lts_imp", 1, "signed_sl", 5)
    dist_dict, path_dict = nx.single_source_dijkstra(subG_C1, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")


    print("Computing Scenario C2...")
    # C2. Improved network limited to LTS2 and SL 5.0.
    scenario_name = "imLts2_5"
    subG_C2 = net.subgraphGetter("lts_imp", 2, "signed_sl", 5)
    dist_dict, path_dict = nx.single_source_dijkstra(subG_C2, source_coords, target=None, weight="length")
    nx.set_node_attributes(G, dist_dict, scenario_name)
    nx.set_node_attributes(G, path_dict, f"{'r_' + scenario_name}")


    net_vertices, net_links = nx_to_gdf(G)
    # del net_links["fid"]
    net_links.to_file('C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\accessibility\\data\\downtown_l.gpkg', driver="GPKG")



    for sc in ["lts4","lts1", "lts2", "lts1_sl5", "lts2_sl5", "lts1_sl3.5", "lts2_sl3.5", "imLts1_5", "imLts2_5"]:
        p = f"p_{sc}"
        r = f"r_{sc}"
        print(p)
        net_vertices[p] = net_vertices.apply(lambda row : decay_func(row["lts4"], row[sc]), axis =1)

        net_shortest_path = geopandas.GeoDataFrame()
        net_shortest_path["coords"] = net_vertices[r]
        net_shortest_path["geometry"] = net_shortest_path.apply(lambda row: make_route_line(row["coords"]), axis=1)
        del net_shortest_path["coords"]
        net_shortest_path.to_file(
            'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\accessibility\\data\\downtown_path.gpkg',
            driver="GPKG", layer=sc)


    _columns = [i for i in net_vertices.columns if not i.startswith("r_")]
    net_vertices[_columns].to_file('C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\accessibility\\data\\downtown_p.gpkg', driver="GPKG", layer="vertices")



    # net_shortest_path = geopandas.GeoDataFrame()
    # net_shortest_path["coords"] = net_vertices["r_lts4"]
    # net_shortest_path["pid"] = net_vertices["pid"]
    # net_shortest_path["geometry"] = net_shortest_path.apply(lambda row: make_route_line(row["coords"]), axis=1)
    #
    # net_shortest_path[['pid', 'geometry']].to_file(
    #     'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\accessibility\\data\\downtown_test_shortest_path.gpkg',
    #     driver="GPKG")
    #
    # net_shortest_path["coords_lts2"] = net_vertices["r_lts2"]
    #
    # net_shortest_path["geometry_lts2"] = net_shortest_path.apply(lambda row: make_route_line(row["coords_lts2"]), axis=1)
    # net_shortest_path[['pid', 'geometry_lts2']].to_file(
    #     'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\accessibility\\data\\downtown_test_shortest_path_lts.gpkg', layer="lts2",
    #     driver="GPKG")

# The weight function can be used to hide edges by returning None. So:
# _weight = lambda u, v, d: d["length"] if (d["lts_final"]<=4 and d["signed_sl"]<=3.5)  else None
# dist_dict, path_dict = nx.single_source_dijkstra(G, source_coords, target=None, weight=_weight)
# will find the shortest red path.
