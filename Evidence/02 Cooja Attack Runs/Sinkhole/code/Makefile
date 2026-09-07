# Cooja supplies CONTIKI when rebuilding a configuration. For manual builds:
# gmake CONTIKI=/path/to/contiki-ng sinkhole-router.cooja TARGET=cooja
CONTIKI ?= $(CONTIKI_NG)

MAKE_ROUTING = MAKE_ROUTING_RPL_LITE

CFLAGS += -DLOG_CONF_LEVEL_RPL=LOG_LEVEL_WARN

include $(CONTIKI)/Makefile.include
