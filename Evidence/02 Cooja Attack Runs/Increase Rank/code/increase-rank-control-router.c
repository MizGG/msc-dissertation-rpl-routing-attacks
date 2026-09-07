#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "INCREASE-RANK-CONTROL"
#define LOG_LEVEL LOG_LEVEL_INFO

/* Strong definition keeps the advertised-rank hook disabled in control firmware. */
int increase_rank_attack_enabled = 0;

PROCESS(increase_rank_control_router_process, "Increase-rank control router");
AUTOSTART_PROCESSES(&increase_rank_control_router_process);

PROCESS_THREAD(increase_rank_control_router_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("INCREASE RANK CONTROL: started, normal RPL behaviour\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
