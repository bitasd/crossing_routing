import math
import numpy
import pyproj
from shapely.geometry import Point, LineString


class Mixin:
    def get_bearing(self, _from, _to):
        """
        from https://github.com/martinfleis/momepy/blob/9af821dfaf05ab7abdde5e96e12de0e90c4481b4/momepy/utils.py#L112
        :param _from:
        :param _to:
        :return:
        """
        #  aa method
        # dLon = _to[0] - _from[0]
        # y = math.sin(dLon) * math.cos(_to[1])
        # x = math.cos(_from[1]) * math.sin(_to[1]) - math.sin(_from[1]) * math.cos(_to[1]) * math.cos(dLon)
        # brng = numpy.rad2deg(math.atan2(y, x))
        # if brng < 0: brng += 360
        # return brng

        # Bita and Peter method
        dLon = _to[0] - _from[0]
        dLat = _to[1] - _from[1]
        rad = math.atan2(dLon, dLat)
        deg = numpy.rad2deg(rad)
        if deg < 0:
            deg += 360
        return deg

    def split_line(self, line, distance):
        # Cuts a line in two at a distance from its starting point
        if distance <= 0.0 or distance >= line.length:
            return [LineString(line)]
        coords = list(line.coords)
        for i, p in enumerate(coords):
            pd = line.project(Point(p))
            if pd == distance:
                return [
                    LineString(coords[:i + 1]),
                    LineString(coords[i:])]
            if pd > distance:
                cp = line.interpolate(distance)
                return [
                    LineString(coords[:i] + [(cp.x, cp.y)]),
                    LineString([(cp.x, cp.y)] + coords[i:])]

    def midpoint(self, x1, y1, x2, y2):
        return [(x1 + x2) / 2, (y1 + y2) / 2]

    def _update_node_attrs(self, _ndid: int, _attrb_to_updateoradd: str, val):
        """
        TODO: will be used for impoting the node features such as traffic signal point layer
        :param _ndid:
        :param _attrb_to_updateoradd:
        :param val:
        :return:
        """
        pass

    def save_incident_segment(self, ndid: int, segid: int):
        _n = self.nodes_reversed_dict[self.nodeid_to_reversedicindex[ndid]]
        if segid not in _n.incident_segments:
            _n.incident_segments.append(segid)

    def get_segment_attributes(self, segm_id, attr_list):
        attr_vals = list()
        for attr_to_f in attr_list:
            try:
                attr_vals.append(self.segments_dict[segm_id]._attributes[attr_to_f])
            except KeyError:
                print('attribute ', attr_to_f, 'doesn"t exist')
                raise
        return attr_vals

    def node_winc_segm_wsam_name(self, tname: str = '', this_node_d: str = '') -> list:
        # get the incident segments of this_node
        nodes_id_found = []
        node_id_found = -1
        end_node_those_inc_segs = list()
        this_node_id = self.nodes_reversed_dict[f'{this_node_d}'].id
        for those_incid_seg_id_ in self.nodes_reversed_dict[f'{this_node_d}'].incident_segments:
            street_name_of_theseg_to_check_end = self.get_segment_attributes(
                those_incid_seg_id_, [self.field_street_name]
            )
            if f'{tname}' not in street_name_of_theseg_to_check_end:
                first_node_those_incid_seg = self.segments_dict[those_incid_seg_id_]._nodes[0]
                last_node_those_incid_seg = self.segments_dict[those_incid_seg_id_]._nodes[-1]
                # get the end node of those segments
                if first_node_those_incid_seg == this_node_id:
                    end_node_those_inc_seg = self.segments_dict[those_incid_seg_id_]._nodes[-1]
                    end_node_those_inc_segs.append(end_node_those_inc_seg)
                elif last_node_those_incid_seg == this_node_id:
                    end_node_those_inc_seg = self.segments_dict[those_incid_seg_id_]._nodes[0]
                    end_node_those_inc_segs.append(end_node_those_inc_seg)
                else:
                    pass
                # check if the incident segments of
                # the end node of those segments is also dual carriageway, and its name = tname,
                if len(end_node_those_inc_segs) > 0:

                    # TODO this might return in a not found situation which isnt  handled fix
                    for incsegid_endnode_those_segs in self.nodes_reversed_dict[
                        f"{self.nodeid_to_reversedicindex[end_node_those_inc_seg]}"
                    ].incident_segments:
                        is_also_on_dual_cargwy_val = self.get_segment_attributes(incsegid_endnode_those_segs, [
                            list(self.field_val_spec_dual_cargwy.keys())[0]])
                        if is_also_on_dual_cargwy_val[0] == self.field_val_spec_dual_cargwy[
                            list(self.field_val_spec_dual_cargwy.keys())[0]]:
                            is_also_on_dual_cargway = True
                        else:
                            is_also_on_dual_cargway = False

                        its_street_names = self.get_segment_attributes(
                            incsegid_endnode_those_segs, [self.field_street_name]
                        )

                        if f'{tname}' == f'{its_street_names[0]}':
                            it_has_samname = True
                        else:
                            it_has_samname = False

                        if is_also_on_dual_cargway and it_has_samname:
                            node_id_found = end_node_those_inc_seg
                            nodes_id_found.append(node_id_found)
                        is_also_on_dual_cargway = False
                        it_has_samname = False
                else:
                    pass

        return nodes_id_found


    def inc_seg_geom(self, incid_seg_id_, node_id):
        # creates an array from the x node to the closest vertex on the incident segment
        # (takes care of the digitalization too)

        first_node = self.segments_dict[incid_seg_id_]._nodes[0]
        last_node = self.segments_dict[incid_seg_id_]._nodes[-1]
        if first_node == node_id:
            adj_incident_segment = [
                self.segments_dict[incid_seg_id_]._nodes[0],
                self.segments_dict[incid_seg_id_]._nodes[1]
            ]
            incident_seg_geom = [
                [
                    self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[adj_incident_segment[0]]}'].lon,
                    self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[adj_incident_segment[0]]}'].lat
                ],
                [
                    self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[adj_incident_segment[1]]}'].lon,
                    self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[adj_incident_segment[1]]}'].lat
                ]
            ]
        elif last_node == node_id:
            adj_incident_segment = [
                self.segments_dict[incid_seg_id_]._nodes[-1],
                self.segments_dict[incid_seg_id_]._nodes[-2]
            ]

            incident_seg_geom = [
                [
                    self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[adj_incident_segment[0]]}'].lon,
                    self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[adj_incident_segment[0]]}'].lat
                ],
                [
                    self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[adj_incident_segment[1]]}'].lon,
                    self.nodes_reversed_dict[f'{self.nodeid_to_reversedicindex[adj_incident_segment[1]]}'].lat
                ]
            ]
        else:
            print("elsed out in inc_seg_geom", self.segments_dict[incid_seg_id_])
            incident_seg_geom = []

        return incident_seg_geom

