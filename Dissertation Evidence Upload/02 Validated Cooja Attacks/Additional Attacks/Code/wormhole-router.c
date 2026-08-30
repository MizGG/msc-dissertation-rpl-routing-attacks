#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "WORMHOLE"
#define LOG_LEVEL LOG_LEVEL_INFO

PROCESS(wormhole_router_process, "Wormhole endpoint router");
AUTOSTART_PROCESSES(&wormhole_router_process);

PROCESS_THREAD(wormhole_router_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("WORMHOLE ENDPOINT: normal radio links only\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
