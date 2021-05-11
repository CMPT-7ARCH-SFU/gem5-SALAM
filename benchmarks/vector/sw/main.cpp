#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "host.h"
#include "../../common/m5ops.h"

int main(void) {
	m5_reset_stats();
    uint64_t *input = (uint64_t*) input_addr;
    *input = 0x12345678;
    uint64_t *params = (uint64_t*) params_addr;
    *params = 0x12345678;
    runHead(input_addr,output_addr,params_addr);

	m5_dump_stats();
	m5_exit();
    return 0;
}

void runHead(uint64_t input, uint64_t output, uint64_t params) {
    uint8_t  * MMR  = (uint8_t  *)(head_top);
    uint64_t * ARGS = (uint64_t *)(head_top+1);
    printf("Setting args for HEAD\n");
    ARGS[0] = input;
    ARGS[1] = output;
    ARGS[2] = params;
    printf("Running HEAD\n");
    MMR[0]  = 0x01;

}


