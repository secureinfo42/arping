#!/usr/bin/env python3



#######################################################################################################################
#
# Imports
#
##

import warnings
import logging
warnings.filterwarnings("ignore")
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
try:
  from scapy.all import *
except:
  print("Error: you need to install scapy.")
  exit()

import sys
import time
import datetime
import getopt
from os import popen



#######################################################################################################################
#
# Funcz
#
##

MY_MAC = ""

def _get_my_mac(my_ifce):
  global MY_MAC
  MY_MAC = popen("/sbin/ifconfig "+my_ifce,"r").read().split("ether")[1].split(" ")[1].strip()

def _getmacbyip(target_ip,my_ifce):
  global MY_MAC
  arp     = ARP(pdst=target_ip)
  ether   = Ether(src=MY_MAC,dst="ff:ff:ff:ff:ff:ff")
  packet  = ether/arp
  result  = srp(packet, timeout=3, verbose=0, iface=my_ifce,)[0]
  clients = []
  for sent, received in result:
    if target_ip == received.psrc:
      return(received.hwsrc)


def usage(errcode):
  print("")
  print("Usage: arping <IP adress>")
  print("       arping <-t IP> [-I #] [-c #] [-w #] [-q] [-r] [-h]")
  print("")
  print(" -I   : interface")
  print(" -t   : target IP")
  print(" -r   : show only MAC on output")
  print(" -q   : less verbose")
  print(" -c # : send # packets")
  print(" -w # : wait between packets (default: 1s)")
  print("")
  exit(errcode)


if( len(sys.argv) <= 1 ):
  usage(0)

def get_current_ifce():
  cmd="/usr/sbin/netstat -nr|/usr/bin/grep UG|/usr/bin/grep -v ':'|/usr/bin/egrep -o '\\b\\w+(\\s+)?$'|/usr/bin/egrep -o '^\\w+'"
  my_ifce = popen(cmd,"r").read().strip()
  return(my_ifce)



#######################################################################################################################
#
# Main
#
##

ifce        = get_current_ifce()
target_ip   = ""
count       = 86400
verbose     = 1
wait        = 1
options,arg = getopt.getopt(sys.argv[1:],":c:w:vri:I:nhq")

for opt in options:
  if( opt[0] == '-c' ): count     = int(opt[1])
  if( opt[0] == '-I' ): ifce      = opt[1]
  if( opt[0] == '-v' ): verbose   = 1
  if( opt[0] == '-q' ): verbose   = 0
  if( opt[0] == '-r' ): verbose   = -1
  if( opt[0] == '-w' ): wait      = int(opt[1])
  if( opt[0] == '-h' ): usage(0)

if( len(sys.argv) == 2 ):
  target_ip = sys.argv[1]
if( len(sys.argv) != 2 ):
  target_ip = arg[0]

if( not target_ip ):
    usage(1)

_get_my_mac(ifce)

if verbose >= 0:
	print("\nARPING "+target_ip+" from "+ifce+" ["+MY_MAC+"]\n")

dlt_time = 0
seqnum = 0

while seqnum < count:
  seqnum += 1

  try:
    time.sleep(wait)
  except KeyboardInterrupt:
    print("\nUser aborted operation.\n")
    exit(130)

  target_mac = ""
  ref_time = cmp_time = dlt_time = 0
  ref_time = datetime.datetime.timestamp( datetime.datetime.now() )

  try:
    target_mac = _getmacbyip(target_ip,ifce)
  except:
    error = "Error: unable to resolve MAC by IP"

  cmp_time = datetime.datetime.timestamp( datetime.datetime.now() )
  dlt_time = (int(cmp_time*1000000)-int(ref_time*1000000))/1000 # delta

  if( target_mac ):
    if verbose == 1:
      line = "Packet from "+target_mac+" ("+target_ip+"): index="+str(seqnum)+"\ttime="+str(dlt_time)+"ms"
    elif verbose == 0:
      line = target_ip + "\t" + target_mac
    elif verbose == -1:
      line = target_mac

    print(line)
    
    exitcode = 0
  else:
    if verbose == 1:
      line = "No answer from: '"+target_ip+"', date="+str(datetime.datetime.now())
      print(line)
    exitcode = 1

print("")

exit(exitcode)
