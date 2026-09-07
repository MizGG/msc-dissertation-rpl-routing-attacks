#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "DIO-SUPPRESSION-CONTROL"
#define LOG_LEVEL LOG_LEVEL_INFO

/* Strong definition keeps the DIO-output hook disabled in control firmware. */
int dio_suppression_attack_enabled = 0;

PROCESS(dio_suppression_control_router_process, "DIO suppression control router");
AUTOSTART_PROCESSES(&dio_suppression_control_router_process);

PROCESS_THREAD(dio_suppression_control_router_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("DIO SUPPRESSION CONTROL: started, normal RPL behaviour\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
