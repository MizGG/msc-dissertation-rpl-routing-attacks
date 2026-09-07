# Cooja supplies CONTIKI when rebuilding a configuration. For manual builds:
# gmake CONTIKI=/path/to/contiki-ng sybil-router.cooja TARGET=cooja
CONTIKI ?= $(CONTIKI_NG)

MAKE_ROUTING = MAKE_ROUTING_RPL_LITE

CFLAGS += -DLOG_CONF_LEVEL_IPV6=LOG_LEVEL_INFO
CFLAGS += -DLOG_CONF_LEVEL_RPL=LOG_LEVEL_INFO

include $(CONTIKI)/Makefile.include
