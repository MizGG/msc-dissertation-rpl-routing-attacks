#include "contiki.h"
#include "sys/log.h"

/*
 * Start normally so that the RPL network can converge.
 * The attack will be enabled after 90 seconds.
 */
int blackhole_attack_enabled = 0;

#define LOG_MODULE "BLACKHOLE"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (90 * CLOCK_SECOND)

PROCESS(blackhole_router_process, "Blackhole router");
AUTOSTART_PROCESSES(&blackhole_router_process);

PROCESS_THREAD(blackhole_router_process, ev, data)
{
  static struct etimer attack_timer;

  PROCESS_BEGIN();

  LOG_INFO("BLACKHOLE ROUTER: started, attack disabled\n");

  etimer_set(&attack_timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&attack_timer));

  blackhole_attack_enabled = 1;
  LOG_WARN("BLACKHOLE ATTACK: enabled\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
