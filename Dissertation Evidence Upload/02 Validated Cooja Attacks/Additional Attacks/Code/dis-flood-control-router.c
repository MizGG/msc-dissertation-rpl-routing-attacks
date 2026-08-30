#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "DIS-CONTROL"
#define LOG_LEVEL LOG_LEVEL_INFO

PROCESS(dis_flood_control_router_process, "DIS flooding control router");
AUTOSTART_PROCESSES(&dis_flood_control_router_process);

PROCESS_THREAD(dis_flood_control_router_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("DIS FLOOD CONTROL: started, normal RPL behaviour\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
