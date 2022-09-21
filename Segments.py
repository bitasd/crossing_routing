from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Segment_:
    id: int
    _nodes: List[int]
    _attributes: Dict


@dataclass
class Junction_:
    id: int
    _nodes: List[int]
    _attributes: Dict


@dataclass
class JuncLeg_:
    id: int
    _jnodes: list[int]
    _jcoord: list[float, float]
    cc_junclegs_df: Dict


@dataclass
class DualNode_:
    node1_id: int
    node2_id: int

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        else:

            if (self.node1_id == other.node1_id and self.node2_id == other.node2_id) or (
                    self.node1_id == other.node2_id and self.node2_id == other.node1_id):
                return True
            else:
                return False
