#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "SYBIL-RATE-CONTROL"
#define LOG_LEVEL LOG_LEVEL_INFO

int sybil_attack_enabled = 0;

PROCESS(sybil_rate_control_router_process, "Sybil rate-variation control router");
AUTOSTART_PROCESSES(&sybil_rate_control_router_process);

PROCESS_THREAD(sybil_rate_control_router_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("SYBIL RATE CONTROL: started, normal RPL behaviour\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
