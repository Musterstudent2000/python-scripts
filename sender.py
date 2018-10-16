#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demonstrates how to construct and send raw Ethernet packets on the network.
"""

import argparse, os, socket, sys, time

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', dest = 'debug', action='store_true', required = False, help='Dry run')
parser.add_argument('-i', '--interface', dest = 'interface', default = 'eth0', required = False, help='Network interface card')
parser.add_argument('-r', '--reset', dest = 'reset', action='store_true', required = False, help='Send reset packet')
parser.add_argument('-c', '--config', dest = 'config', metavar = 'baud', nargs = 3, default = [], required = False, help = 'Send config packets')
parser.add_argument('-d', '--data', dest = 'data', metavar = ('port', 'baud'), nargs = '+', default = [], required = False, help = 'Send a data packet')
args = parser.parse_args()

def checkSystem():
    if not (sys.platform == 'linux' or sys.platform == 'linux2'):
      sys.exit('This script is only for Linux!')

def checkLinuxRoot():
  if not os.geteuid() == 0:
    sys.exit('This script must be run as root!')

def sendNetworkInterface(data, interface = 'eth0'):
  if args.debug != True:
    s = socket(AF_PACKET, SOCK_RAW)
    s.bind((interface, 0))
    return s.send(data)
  else:
    return len(data)

def sendReset(frame):
  frame[13] = 0x34
  renderInfoPackageSend(sendNetworkInterface(bytearray(frame)))

def renderInfoPackageSend(packages):
  print("Sent %d-byte Ethernet packet on %s" % (packages, args.interface))

def sendConfig(frame, bauds):
  frame[13] = 0x33 # ethernet type
  frame[31] = 1 # command flag
  frame[47] = 1 # status
  for i in range(len(bauds)):
    frame[30] = i + 1 # can port
    frame[46] = int(bauds[i])
    print(frame[30])
    print(frame[46])
    renderInfoPackageSend(sendNetworkInterface(bytearray(frame)))
    if i < 3:
      time.sleep(0.5)

def sendData(frame, port, bauds):
  # Build can port
  frame[13] = 0x33 # ethernet type
  frame[30] = int(port) # can port
  frame[31] = 0 # command flag

  # Build bauds if exists
  if len(bauds) != 0:
    # Empty data field
    for i in range(21, 29):
      frame[i] = 0

    # Build bauts
    for i in range(len(bauds)):
      frame[21 + i] = int(bauds[i])

  # Send package
  renderInfoPackageSend(sendNetworkInterface(bytearray(frame)))

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

if __name__ == '__main__':
  checkSystem()
  checkLinuxRoot()

  # Check arguments
  if args.reset == True:
    sendReset(frame)

  if len(args.config) != 0:
    if len(args.config) == 3:
      sendConfig(frame, args.config)
    else:
      sys.exit('Arguments must be three baut.')

  if len(args.data) != 0:
    if len(args.data) > 0 and len(args.data) <= 9:
      sendData(frame, args.data.pop(0), args.data)
    else:
      sys.exit('Arguments must be one port and max eight baut.')
