# this scripts uses the node pairs to detect multi-node sections and create junctions features
import geopandas
import pandas
import pyproj
import itertools
from Segments import Junction_, DualNode_


class GeoJuncs:

    def junc_layer(self, my_id='ID_TRC'):

        pair_nodes = {}
        junc_id = 100
        for el in list(self.nodes_reversed_dict.values()):

            # SINGLE NODE INTERSECTIONS
            if len(el.dual_name_to_nodeid) == 0 and len(el.incident_segments) > 2:
                # print(el)
                _attr = {}
                legs_ = el.incident_segments

                myids = list()
                inc_seg_geoms = list()
                bearings = list()
                duals = list()
                road_names = list()

                for leg in legs_:
                    myids.append(self.get_segment_attributes(leg, [my_id])[0])
                    duals.append(self.get_segment_attributes(leg, ['DIVIDED'])[0])
                    road_names.append(self.get_segment_attributes(leg, ['NOM_VOIE'])[0])
                    incident_seg_geom = self.inc_seg_geom(leg, el.id)
                    bearing = self.get_bearing(incident_seg_geom[0], incident_seg_geom[1])
                    # appending to a list
                    # inc_seg_geoms.append(incident_seg_geom)
                    bearings.append(float("{:.1f}".format(bearing)))

                # dataframe for bearings
                incident_segs_df = pandas.DataFrame({
                    'incid_seg_id_': legs_,
                    'bearing': bearings,
                    'bearing_r': bearings,
                    'dual': duals,
                    'name': road_names
                    # 'adj_inc_seg_geom': inc_seg_geoms
                })
                incident_segs_df['cc_rank'] = incident_segs_df['bearing'].rank(ascending=False, method='first')
                # incident_segs_dict = incident_segs_df.to_dict(orient='list')

                _attr.update({
                    'id': [junc_id], 'lon': [el.lon], 'lat': [el.lat],
                    'ID_TRCs': [",".join(list(map(str, myids)))],
                    'nodes': [el.id],
                    'bearings': [",".join(list(map(str, bearings)))],
                    'incident_segs': [",".join(list(map(str, legs_)))],
                    'bearings_r': [",".join(list(map(str, bearings)))],
                    'cc_rank': [",".join(list(map(str, incident_segs_df['cc_rank'].tolist())))],
                    # 'inc_seg_geoms': [",".join(list(map(str, inc_seg_geoms)))],
                    'cc_ordered_segs': [incident_segs_df]
                })

                _j = Junction_(id=junc_id, _nodes=el.id, _attributes=_attr)
                self.juncs_dict.update({
                    junc_id: _j
                })
                junc_id += 1

            # MULTI NODE INTERSECTIONS
            elif len(el.dual_name_to_nodeid) > 0 and len(el.incident_segments) > 2:

                pair_nodes[el.id] = [pid for pid in el.dual_name_to_nodeid.values()]

        num_single_node = len(self.juncs_dict)  # number of single node processed

        # MULTI-NODE X PROCESSING
        # Finding all the intersection nodes that belong to a junction
        # print("pair_nodes: ", pair_nodes)
        # Identifying pairs
        temp = {}
        for key, value in pair_nodes.items():
            if len(value) == 1:
                temp[key] = DualNode_(value[0], None)
            else:
                temp[key] = DualNode_(value[0], value[1])
        # print("temp: ", temp)

        # Forming the junctions with all the sub-nodes
        super_nodes_lst = []
        for k in temp:
            for k_ in temp:
                if k != k_ and temp[k] == temp[k_] and None not in [temp[k].node2_id, temp[k].node1_id]:
                    super_nodes_lst.append([k, k_, temp[k].node1_id, temp[k].node2_id])
        for k in temp:
            if None in [temp[k].node2_id, temp[k].node1_id]:
                super_nodes_lst.append([k, temp[k].node1_id])

        # print("super_nodes_lst: ", super_nodes_lst)
        # Keeping unique node families
        pairs_lst = []
        for v in super_nodes_lst:
            v.sort()
            pairs_lst.append(v)

        pairs_lst.sort()
        pairs_uniq = list(k for k, _ in itertools.groupby(pairs_lst))
        # print("pairs_lst:", pairs_lst)
        # print("pairs_uniq:", pairs_uniq)
        # Creating junction from family nodes
        for jid in range(len(pairs_uniq)):
            _attr = {}
            junction_nodes = pairs_uniq[jid]
            # Merging family nodes into the averaged point
            legs_, coord, m_node_id = self.merge_nodes(junction_nodes)
            self.nodeid_to_reversedicindex.update({
                m_node_id: f"{float(coord[0]):.15f}{float(coord[1]):.15f}"
            })

            myids = []
            inc_seg_geoms = []
            bearings = []
            inc_seg_geoms_r = []
            bearings_r = []
            duals = []
            road_names = []

            for inc_segs_i in legs_:

                myids.append(self.get_segment_attributes(inc_segs_i, [my_id])[0])
                duals.append(self.get_segment_attributes(inc_segs_i, ['DIVIDED'])[0])
                road_names.append(self.get_segment_attributes(inc_segs_i, ['NOM_VOIE'])[0])
                first_n = self.segments_dict[inc_segs_i]._nodes[0]
                last_n = self.segments_dict[inc_segs_i]._nodes[-1]

                # Bearing relative to the original node within the junction
                nod_w_junc = first_n if first_n in junction_nodes else last_n
                incident_seg_geom_r = self.inc_seg_geom(inc_segs_i, nod_w_junc)
                bearing_r = self.get_bearing(incident_seg_geom_r[0], incident_seg_geom_r[1])
                # appending to a list
                inc_seg_geoms_r.append(incident_seg_geom_r)
                bearings_r.append(float("{:.1f}".format(bearing_r)))

                # Bearing relative to the averaged point
                if first_n in junction_nodes:
                    seg_gem = [
                        self.nodes_reversed_dict[f"{float(coord[0]):.15f}{float(coord[1]):.15f}"].id,
                        self.segments_dict[inc_segs_i]._nodes[-1]
                    ]
                elif last_n in junction_nodes:
                    seg_gem = [
                        self.nodes_reversed_dict[f"{float(coord[0]):.15f}{float(coord[1]):.15f}"].id,
                        # relative to averaged node
                        self.segments_dict[inc_segs_i]._nodes[0]
                    ]
                incident_seg_geom = [
                    [
                        self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[seg_gem[0]]}'].lon,
                        self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[seg_gem[0]]}'].lat
                    ],
                    [
                        self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[seg_gem[1]]}'].lon,
                        self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[seg_gem[1]]}'].lat
                    ]
                ]

                bearing = self.get_bearing(incident_seg_geom[0], incident_seg_geom[1])
                inc_seg_geoms.append(incident_seg_geom)
                bearings.append(float("{:.1f}".format(bearing)))

            # dataframe for bearings
            incident_segs_df = pandas.DataFrame({
                'incid_seg_id_': legs_,
                'bearing': bearings,
                'bearing_r': bearings_r,
                'dual': duals,
                'name': road_names
                # 'adj_inc_seg_geom': inc_seg_geoms
            })
            # ranking should be based on "bearing" which is relative to the averaged point
            # "bearing" can be later on removed and "bearing_r" should be used for detecting links in a leg
            incident_segs_df['cc_rank'] = incident_segs_df['bearing'].rank(ascending=False, method='first')
            # incident_segs_dict = incident_segs_df.to_dict(orient='list')
            id_ = jid + num_single_node + 100
            _attr.update(
                {'id': [id_], 'lon': [coord[0]], 'lat': [coord[1]],
                 'ID_TRCs': [",".join(list(map(str, myids)))],
                 'nodes': [",".join(list(map(str, junction_nodes)))],
                 'bearings': [",".join(list(map(str, bearings)))],
                 'incident_segs': [",".join(list(map(str, legs_)))],
                 'bearings_r': [",".join(list(map(str, bearings_r)))],
                 'cc_rank': [",".join(list(map(str, incident_segs_df['cc_rank'].tolist())))],
                 # 'inc_seg_geoms': [",".join(list(map(str, inc_seg_geoms)))],
                 'cc_ordered_segs': [incident_segs_df]
                 })

            _j = Junction_(id=id_, _nodes=junction_nodes, _attributes=_attr)
            self.juncs_dict.update({
                id_: _j
            })

        df = pandas.DataFrame()
        for idx, value in self.juncs_dict.items():
            df = df.append(pandas.DataFrame(value._attributes))

        gdf = geopandas.GeoDataFrame(
            df, geometry=geopandas.points_from_xy(df.lon, df.lat))
        gdf.crs = pyproj.CRS.from_epsg(4326).to_wkt()
        return gdf
