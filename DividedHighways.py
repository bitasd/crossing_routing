import collections
class Mixin:

    def merge_nodes(self, nodes_id_lst: list):
        # family_nodes = []
        lats = []
        lons = []
        combin_inc_segs = []

        for _node_id in nodes_id_lst:
            node_ = self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[_node_id]}']
            lats.append(node_.lat)
            lons.append(node_.lon)
            combin_inc_segs.append(node_.incident_segments)

        m_lon = sum(lons) / len(lons)
        m_lat = sum(lats) / len(lats)

        loc_prps = [m_lon, m_lat]
        m_node_id = self.get_or_add_node_id(loc_prps)
        # Getting only the external links
        combin_inc_segs_p = []
        for lst in combin_inc_segs:
            for el in lst:
                combin_inc_segs_p.append(el)
        combin_external_inc_segs = [item for item, count in collections.Counter(combin_inc_segs_p).items() if count < 2]

        return combin_external_inc_segs, loc_prps, m_node_id

