#include "contiki.h"
#include "sys/log.h"

/* Control router: packet dropping is permanently disabled */
int blackhole_attack_enabled = 0;

#define LOG_MODULE "CONTROL"
#define LOG_LEVEL LOG_LEVEL_INFO

PROCESS(control_router_process, "Control router");
AUTOSTART_PROCESSES(&control_router_process);

PROCESS_THREAD(control_router_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("CONTROL ROUTER: started, forwarding enabled\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
