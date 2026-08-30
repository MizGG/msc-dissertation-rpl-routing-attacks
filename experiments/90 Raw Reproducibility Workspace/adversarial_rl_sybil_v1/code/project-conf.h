#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

/*
 * Keep the new Sybil package self-observing: the existing Contiki IPv6 hook
 * reports the actual virtual source address for each spoofed RPL DIO.
 * This is a logging-only setting and does not alter routing behaviour.
 */
#define LOG_CONF_LEVEL_IPV6 LOG_LEVEL_WARN

#endif /* PROJECT_CONF_H_ */
