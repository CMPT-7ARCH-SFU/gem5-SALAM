#include <stdio.h>
#include "host.h"

void head_isr(void)
{
	printf("Interrupt\n\r");
	//stage += 1;
}

