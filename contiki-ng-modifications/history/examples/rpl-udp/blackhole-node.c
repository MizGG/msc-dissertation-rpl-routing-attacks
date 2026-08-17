#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "Blackhole"
#define LOG_LEVEL LOG_LEVEL_INFO

/* This overrides the weak default in os/net/ipv6/uip6.c */
int blackhole_attack_enabled = 1;

PROCESS(blackhole_node_process, "Blackhole node");
AUTOSTART_PROCESSES(&blackhole_node_process);

PROCESS_THREAD(blackhole_node_process, ev, data)
{
  static struct etimer alive_timer;

  PROCESS_BEGIN();

  LOG_WARN("BLACKHOLE NODE: started\n");
  LOG_WARN("BLACKHOLE NODE: forwarding drop switch enabled\n");

  etimer_set(&alive_timer, CLOCK_SECOND * 10);

  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&alive_timer));
    LOG_INFO("BLACKHOLE NODE: alive, waiting for forwarded packets\n");
    etimer_reset(&alive_timer);
  }

  PROCESS_END();
}
