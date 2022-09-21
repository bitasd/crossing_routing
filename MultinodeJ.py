import geopandas
from shapely.geometry import LineString


class MultinodeJ:

    def mergeGeom(self) -> geopandas.GeoDataFrame:

        # Populating the lookup dictionary for junctions that have more than one node
        for k, v in self.juncs_dict.items():
            if type(v._nodes)==list:
                for _node in v._nodes:
                    self.multinode_lookup_dict.update({_node:v.id})

        # Recreating the geometry of line segments-- for multinode junctions, replacing the nodes with the averaged point
        for sk, sv in self.segments_dict.items():
            seg_attributes = sv._attributes
            seg_coords = []
            for node_id in sv._nodes:
                if node_id not in self.multinode_lookup_dict:
                    seg_coords.append((self.nodes_reversed_dict[self.nodeid_to_reversedicindex[node_id]].lon,
                                       self.nodes_reversed_dict[self.nodeid_to_reversedicindex[node_id]].lat))
                else:
                    seg_coords.append((self.juncs_dict[self.multinode_lookup_dict[node_id]]._attributes['lon'][0],
                                       self.juncs_dict[self.multinode_lookup_dict[node_id]]._attributes['lat'][0]))
            # print(seg_coords)

            geom = LineString(seg_coords)
            seg_attributes['geometry'] = geom
            self.merged_junc_segments.append(seg_attributes)

        merged_junc_gdf = geopandas.GeoDataFrame(self.merged_junc_segments)
        return merged_junc_gdf