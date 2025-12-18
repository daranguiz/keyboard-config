cmake_minimum_required(VERSION 3.20.0)

project(dario_contextual_hold_tap)

if(CONFIG_DARIO_CONTEXTUAL_HOLD_TAP)
  target_sources(app PRIVATE src/contextual_hold_tap.c src/contextual_hold_tap_listener.c)
endif()
