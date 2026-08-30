#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "WORST-PARENT-CONTROL"
#define LOG_LEVEL LOG_LEVEL_INFO

/* Strong definition keeps the parent-selection hook disabled in control firmware. */
int worst_parent_attack_enabled = 0;

PROCESS(worst_parent_control_router_process, "Worst-parent control router");
AUTOSTART_PROCESSES(&worst_parent_control_router_process);

PROCESS_THREAD(worst_parent_control_router_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("WORST PARENT CONTROL: started, normal RPL behaviour\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
