#include "contiki.h"
#include "sys/log.h"

/* Control router: sinkhole rank advertisement is permanently disabled. */
int sinkhole_attack_enabled = 0;

#define LOG_MODULE "SINKHOLE_CTRL"
#define LOG_LEVEL LOG_LEVEL_INFO

PROCESS(sinkhole_control_router_process, "Sinkhole control router");
AUTOSTART_PROCESSES(&sinkhole_control_router_process);

PROCESS_THREAD(sinkhole_control_router_process, ev, data)
{
  PROCESS_BEGIN();

  sinkhole_attack_enabled = 0;
  LOG_INFO("SINKHOLE CONTROL: started, normal RPL behaviour\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
