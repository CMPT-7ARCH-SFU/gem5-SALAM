from m5.params import *
from m5.proxy import *
from m5.SimObject import SimObject
from ComputeUnit import ComputeUnit

class CGRAMapper(ComputeUnit):
    type = 'CGRAMapper'
    cxx_header = "hwacc/cgra_mapper.hh"
