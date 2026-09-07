#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "WORST-PARENT"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (240 * CLOCK_SECOND)

/* Strong application definition overrides the disabled weak Contiki default. */
int worst_parent_attack_enabled = 0;

PROCESS(worst_parent_router_process, "Delayed worst-parent attacker");
AUTOSTART_PROCESSES(&worst_parent_router_process);

PROCESS_THREAD(worst_parent_router_process, ev, data)
{
  static struct etimer timer;

  PROCESS_BEGIN();

  LOG_INFO("WORST PARENT ROUTER: started, attack disabled\n");
  etimer_set(&timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

  worst_parent_attack_enabled = 1;
  LOG_WARN("WORST PARENT ATTACK: enabled\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
