# Set CONTIKI to the local Contiki-NG checkout when building manually.
CONTIKI ?= $(CONTIKI_NG)

MAKE_ROUTING = MAKE_ROUTING_RPL_LITE

CFLAGS += -DLOG_CONF_LEVEL_RPL=LOG_LEVEL_INFO

include $(CONTIKI)/Makefile.include
