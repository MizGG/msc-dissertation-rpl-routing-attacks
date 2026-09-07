#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "GRAYHOLE"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (240 * CLOCK_SECOND)

/* Strong application definition overrides the disabled weak Contiki default. */
int grayhole_attack_enabled = 0;

PROCESS(grayhole_router_process, "Delayed grayhole attacker");
AUTOSTART_PROCESSES(&grayhole_router_process);

PROCESS_THREAD(grayhole_router_process, ev, data)
{
  static struct etimer timer;

  PROCESS_BEGIN();

  LOG_INFO("GRAYHOLE ROUTER: started, attack disabled\n");
  etimer_set(&timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

  grayhole_attack_enabled = 1;
  LOG_WARN("GRAYHOLE ATTACK: enabled\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
