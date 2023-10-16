"""
This script defines the model of the input format for the 3DFier for generating the 3D model / obj format.

this will be inherited with the main script to enerate the output obj file and corresponding cityGML format
"""



from typing import List, Dict, Any

class InputPolygons:
    datasets: List[str]
    uniqueid: str
    lifting: str
    height_field: str = None
    handle_multiple_heights: bool = False

class InputElevation:
    datasets: List[str]
    omit_LAS_classes: List[int] = None
    thinning: int = None

class LiftingOptions:
    lod: int = None
    floor: bool = None
    inner_walls: bool = None
    triangulate: bool = None
    ground: Dict[str, Any] = None
    roof: Dict[str, Any] = None

class Options:
    building_radius_vertex_elevation: float = None
    radius_vertex_elevation: float = None
    threshold_jump_edges: float = None
