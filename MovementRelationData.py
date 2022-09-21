from typing import List, Dict
from dataclasses import dataclass, field
from shapely.geometry import LineString


@dataclass
class AttributesForCrossingRelation_:
    junction_id: int
    from_seg_id: List = field(default_factory=list)
    to_seg_id: List = field(default_factory=list)
    from_cc: List = field(default_factory=list)
    to_cc: List = field(default_factory=list)
    cross_cc: List = field(default_factory=list)
    trc_attrs: Dict = field(default_factory=dict)
    other_cross_over_attrs: Dict = field(default_factory=dict)


@dataclass
class MovementRelation_:
    id: int
    crosing_attr: AttributesForCrossingRelation_
    rels_geom: LineString


@dataclass
class Crossing_:
    id: int
    _juncid: int
    _depLeg: int
    _arrivLeg: int
    _crossLeg: int
    _attributes: Dict

@dataclass
class FieldAttrLookup:
    field: str
    attrib: str

@dataclass
class FieldAttrs:
    lookup: List

    def translate(self, attrb, val):
        rets = []
        for f_at in self.lookup:
            if f_at.attrib == attrb:
                ret = val[f_at.field]
                rets.append(ret)
        return rets[0]



# first we have fields, we want to translate them to attributes

# field_attr_lookup

_adt = FieldAttrLookup(field="CURRENT_AA", attrib="ADT")
_num_lanes = FieldAttrLookup(field="lanes", attrib="NBLane")
_speed = FieldAttrLookup(field="speed_limit", attrib="Q85")

lk = FieldAttrs([_adt,_num_lanes,_speed])


relation_attr={'from_lts':2, 'Control':'Signal', 'PocketTrig': 2, 'XDistSig': 24, 'TwoStage':1, 'lanes': 1, 'speed_limit': 35,
               'CURRENT_AA': 1200, 'XlleStop': 0, 'from_trail':0
               }
v = lk.translate("ADT", relation_attr)