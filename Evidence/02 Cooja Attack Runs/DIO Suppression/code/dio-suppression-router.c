#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "DIO-SUPPRESSION"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (240 * CLOCK_SECOND)

/* Strong application definition overrides the disabled weak Contiki default. */
int dio_suppression_attack_enabled = 0;

PROCESS(dio_suppression_router_process, "Delayed DIO suppression attacker");
AUTOSTART_PROCESSES(&dio_suppression_router_process);

PROCESS_THREAD(dio_suppression_router_process, ev, data)
{
  static struct etimer timer;

  PROCESS_BEGIN();

  LOG_INFO("DIO SUPPRESSION ROUTER: started, attack disabled\n");
  etimer_set(&timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

  dio_suppression_attack_enabled = 1;
  LOG_WARN("DIO SUPPRESSION ATTACK: enabled\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
