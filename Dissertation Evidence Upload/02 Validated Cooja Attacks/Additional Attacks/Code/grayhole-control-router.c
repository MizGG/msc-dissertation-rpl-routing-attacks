#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "GRAYHOLE-CONTROL"
#define LOG_LEVEL LOG_LEVEL_INFO

/* Strong definition keeps the forwarding hook disabled in control firmware. */
int grayhole_attack_enabled = 0;

PROCESS(grayhole_control_router_process, "Grayhole control router");
AUTOSTART_PROCESSES(&grayhole_control_router_process);

PROCESS_THREAD(grayhole_control_router_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("GRAYHOLE CONTROL: started, normal RPL behaviour\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
