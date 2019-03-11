#include <iostream>
#include <fstream>
#include "hwacc/cgra_mapper.hh"


CGRAMapper::CGRAMapper(CGRAMapperParams *p) :
    ComputeUnit(p) {
    running = false;
}

void
CGRAMapper::tick() {
/*********************************************************************************************
 CN Scheduling

 As CNs are scheduled they are added to an in-flight queue depending on operation type.
 Loads and Stores are maintained in separate queues, and are committed by the comm_interface.
 Branch and phi instructions evaluate and commit immediately. All other CN types are added to
 an in-flight compute queue.

 Each tick we must first check our in-flight compute queue. Each node should have its cycle
 count incremented, and should commit if max cycle is reached.

 New CNs are added to the reservation table whenever a new BB is encountered. This may occur
 during device init, or when a br op commits. For each CN in a BB we reset the CN, evaluate
 if it is a phi or uncond br, and add it to our reservation table otherwise.
*********************************************************************************************/

    DPRINTF(IOAcc, "\n%s\n%s %d\n%s\n",
            "********************************************************************************",
            "   Cycle", cycle,
            "********************************************************************************");
    cycle++;
    comm->refreshMemPorts();
    clearFU();
}

void
CGRAMapper::initialize() {
    DPRINTF(CGRAMapper, "Initializing CGRA and CGRA Mapper!\n");
    tick();
}

