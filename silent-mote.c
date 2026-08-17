#include "contiki.h"
#include "sys/log.h"

#define LOG_MODULE "SILENT"
#define LOG_LEVEL LOG_LEVEL_INFO

PROCESS(silent_mote_process, "Silent control mote");
AUTOSTART_PROCESSES(&silent_mote_process);

PROCESS_THREAD(silent_mote_process, ev, data)
{
  PROCESS_BEGIN();

  LOG_INFO("Silent control mote started\n");

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
