#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "INCREASE-RANK"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (240 * CLOCK_SECOND)

/* Strong application definition overrides the disabled weak Contiki default. */
int increase_rank_attack_enabled = 0;

PROCESS(increase_rank_router_process, "Delayed increase-rank attacker");
AUTOSTART_PROCESSES(&increase_rank_router_process);

PROCESS_THREAD(increase_rank_router_process, ev, data)
{
  static struct etimer timer;

  PROCESS_BEGIN();

  LOG_INFO("INCREASE RANK ROUTER: started, attack disabled\n");
  etimer_set(&timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

  increase_rank_attack_enabled = 1;
  LOG_WARN("INCREASE RANK ATTACK: enabled\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
