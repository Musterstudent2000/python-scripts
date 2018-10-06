#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demonstrates how to construct and send raw Ethernet packets on the network.
"""

import os, socket, sys, time

def checkSystem():
    if not (sys.platform == "linux" or sys.platform == "linux2"):
        print("This script is only for Linux!")
        result = input("Press Enter to continue...")
        sys.exit(0)

def checkLinuxRoot():
  if not os.geteuid() == 0:
    sys.exit('This script must be run as root!')

def sendNetworkInterface(data, interface = "eno1"):
  s = socket(AF_PACKET, SOCK_RAW)
  s.bind((interface, 0))
  return s.send(data)

if __name__ == "__main__":
  checkSystem()
  checkLinuxRoot()

  last_mode = ["", ""]

  frame = [
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, # dst mac 0-5
    0xFE, 0xED, 0xFE, 0xED, 0xFE, 0xED, # src mac 6-11
    0x33, 0x33, # ethertype 12-13
    0x00, # remote frame 14
    0x00, # extended frame 15
    0x04, 0x03, 0x02, 0x01, # can id 16-19
    0x08, # dlc 20
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # data 21-28
    # 0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef, # data 21-28
    0xcc, # frame crc 29
    0x02, # can port 30
    0x01, # command flag 31
    0x00, 0x00, 0x00, 0x00, # timestamp can frames 32-35
    0x00, 0x00, # 15-bit can frame crc 36-37
    0x00, 0x00, # 16-bit counter recieved can frames 38-39
    0x00, 0x00, # 16-bit counter sent can frames 40-41
    0x00, # can status 42
    0x00, # can bus rx error counter 43
    0x00, # can bus tx error counter 44
    0x00, # can tx buffer status 45
    0x02, # baud rate index 46
    0x01, # can active passive 47
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # 48-57
    0x00, 0x00, # 16-bit crc byte 12-57 58-59
    ]

  while (True):
    mode = input("mode: ")
    mode_array = mode.split(" ")
    #print(mode_array[0])

    if mode_array[0] == "!!":
      mode_array = last_mode

    if mode_array[0] == "reset":
      frame[13] = 0x34
      print("Sent %d-byte Ethernet packet on eth0" %
        sendNetworkInterface(bytearray(frame)))

    elif mode_array[0] == "config":
      if len(mode_array) != 4:
        print("Please type 'reset' to send a reset packet, "
          "'config <baud1> <baud2> <baud3>' to send 3 config packets or 'data <port> <data1> <data2> ... <data8>' to send a data packet")

      else:
        frame[13] = 0x33
        frame[31] = 1

        frame[30] = 1 # can port
        frame[47] = 1 # status
        frame[46] = int(mode_array[1]) # baud index
        print("Sent %d-byte Ethernet packet on eth0" %
          sendNetworkInterface(bytearray(frame)))
        time.sleep(0.5)
        frame[30] = 2 # can port
        frame[47] = 1 # status
        frame[46] = int(mode_array[2]) # baud index
        print("Sent %d-byte Ethernet packet on eth0" %
          sendNetworkInterface(bytearray(frame)))
        time.sleep(0.5)
        frame[30] = 3 # can port
        frame[47] = 1 # status
        frame[46] = int(mode_array[3]) # baud index
        print("Sent %d-byte Ethernet packet on eth0" %
          sendNetworkInterface(bytearray(frame)))

    elif mode_array[0] == "data":
      if len(mode_array) == 2:
        frame[13] = 0x33 # ethernet type
        frame[30] = int(mode_array[1]) # can port
        frame[31] = 0 # command flag
        print("Sent %d-byte Ethernet packet on eth0" %
          sendNetworkInterface(bytearray(frame)))

      elif len(mode_array) > 2:
        frame[13] = 0x33 # ethernet type
        frame[30] = int(mode_array[1]) # can port
        frame[20] = len(mode_array)-2
        for i in range(21, 29):
          frame[i] = 0 # empty data field
        for i in range(len(mode_array)-2):
          frame[21+i] = int(mode_array[2+i]) # data definition
        frame[31] = 0 # command flag
        print("Sent %d-byte Ethernet packet on eth0" %
          sendNetworkInterface(bytearray(frame)))

      else:
        print("Please type 'reset' to send a reset packet, "
          "'config <baud1> <baud2> <baud3>' to send 3 config packets or 'data <port> <data1> <data2> ... <data8>' to send a data packet")
    else:
      print("Please type 'reset' to send a reset packet, "
        "'config' to send 3 config packets or 'data <port> <data1> <data2> ... <data8>' to send a data packet")

    last_mode = mode_array
