import pandas
import geopandas
from typing import List, Dict
from Segments import Segment_


class Mixin:

    def first_order_import(
            self,
            streets: geopandas.GeoDataFrame,
            field_val_spec_dual_cargwy: Dict[str, str] = None,
            field_street_name=None
    ):
        if field_val_spec_dual_cargwy is None:
            field_val_spec_dual_cargwy = {'DIVIDED': 'DIVIDED'}
        self.field_val_spec_dual_cargwy = field_val_spec_dual_cargwy
        self.field_street_name = field_street_name
        _attrs = list(streets.columns)
        print(_attrs)
        del _attrs[-1]
        for i in range(len(streets)):
            # print(i)
            _street = streets.loc[streets.index == i, ]
            if not _street.empty:
                self._in_seg_id += 1
                seg = Segment_(self._in_seg_id, [], {})
                for streetM in _street['geometry']:  # MultiLineString
                    # print("this is streetM: ", streetM)
                    for street in streetM:  # Should be LineString
                        # print("this is street: ", street)
                        for vert_index in range(len(list(street.coords))):
                            vert = list(street.coords)[vert_index]
                            ndid = self.get_or_add_node_id(vert)
                            self.nodeid_to_reversedicindex.update({
                                ndid: f"{float(vert[0]):.15f}{float(vert[1]):.15f}"
                            })
                            seg._nodes.append(ndid)
                            if (vert_index == 0) or (vert_index == len(list(street.coords)) - 1):
                                self.save_incident_segment(ndid, self._in_seg_id)
                for _attr in _attrs:
                    seg._attributes.update({
                        f"{_attr}": _street[f'{_attr}'].values[0]
                    })
            # having the dictionary will be making the process faster but will be very memory costly
            # some kind of logic for this comprimise is needed
            self.segments_dict.update({
                self._in_seg_id: seg
            })
