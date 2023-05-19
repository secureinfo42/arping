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

APP = "arping"
MY_MAC = ""

def fatal(errtxt,errcode=1):
  sys.stderr.write("\033[1;31mError: %s\033[0m" % errtxt)
  sys.exit(errcode)

def _get_my_mac(my_ifce):
  global MY_MAC
  try:
    MY_MAC = popen("/sbin/ifconfig %s 2>/dev/null" % my_ifce,"r").read().split("ether")[1].split(" ")[1].split("\n")[0].strip()
  except:
    fatal("can't find device %s" % my_ifce)

def get_mac_by_ip(target_ip,my_ifce,timeout):
  global MY_MAC
  arp     = ARP(pdst=target_ip)
  ether   = Ether(src=MY_MAC,dst="ff:ff:ff:ff:ff:ff")
  packet  = ether/arp
  try:
    result  = srp(packet, timeout=3, verbose=0, iface=my_ifce,)[0]
  except:
    return("",0)
  clients = []
  for sent, received in result:
    if target_ip == received.psrc:
      return(received.hwsrc,len(received))


def usage(errcode):
  print("")
  print("Usage: arping <IP adress>")
  print("       arping <-t IP> [-I #] [-c #] [-w #] [-q] [-r] [-h]")
  print("")
  print(" -I   : interface")
  print(" -t   : target IP")
  print(" -r   : show only MAC on output")
  print(" -q   : less verbose")
  print(" -T # : timeout #")
  print(" -c # : send # packets")
  print(" -w # : wait between packets (default: 1s)")
  print("")
  exit(errcode)

def get_current_ifce():
  cmd="/usr/sbin/netstat -nr|/usr/bin/grep UG|/usr/bin/grep -v ':'|/usr/bin/egrep -o '\\b\\w+(\\s+)?$'|/usr/bin/egrep -o '^\\w+'|head -n1"
  my_ifce = popen(cmd,"r").read().strip()
  return(my_ifce)

def get_summary(target_ip,nb_transmitted,nb_received, nb_unanswered,min_time,max_time):
  avg_time = str((max_time+min_time)/2)[:6]
  summary  = "\n--- %s statistics ---" % target_ip
  summary += "\n%s packets transmitted, %s packets received, %s%% unanswered" % (nb_transmitted,nb_received, nb_unanswered)
  summary += "\nrtt min/avg/max = %s/%s/%s ms\n" % (min_time,avg_time,max_time)
  print(summary)


#######################################################################################################################
#
# Main
#
##

if( len(sys.argv) <= 1 ):
  usage(0)

ifce        = get_current_ifce()
target_ip   = ""
count       = 86400
verbose     = 1
wait        = 1
options,arg = getopt.getopt(sys.argv[1:],":c:w:vri:I:nhqT:")
timeout     = 60

for opt in options:
  if( opt[0] == '-c' ): count     = int(opt[1])
  if( opt[0] == '-I' ): ifce      = opt[1]
  if( opt[0] == '-v' ): verbose   = 1
  if( opt[0] == '-q' ): verbose   = 0
  if( opt[0] == '-r' ): verbose   = -1
  if( opt[0] == '-w' ): wait      = int(opt[1])
  if( opt[0] == '-T' ): timeout   = int(opt[1])
  if( opt[0] == '-h' ): usage(0)

if( len(sys.argv) == 2 ):  target_ip = sys.argv[1]
if( len(sys.argv) != 2 ):  target_ip = arg[0]
if( not target_ip ):       usage(1)

_get_my_mac(ifce)

if verbose >= 0:
  print("\n%s %s from %s [%s]" % (APP.upper(),target_ip,ifce,MY_MAC))

dlt_time = 0
seqnum = 0
nb_unanswered = 0
nb_received = 0
nb_transmitted = 0
max_time = 0
min_time = 60000

while seqnum < count:

  seqnum += 1

  target_mac = ""
  ref_time = cmp_time = dlt_time = 0
  ref_time = datetime.datetime.timestamp( datetime.datetime.now() )
  nb_bytes = 0
  nb_transmitted += 1

  try:
    target_mac,nb_bytes = get_mac_by_ip(target_ip,ifce,timeout)
    nb_received += 1
  except KeyboardInterrupt:
    get_summary(target_ip,nb_transmitted,nb_received, nb_unanswered,min_time,max_time)
    exit(130)
  except:
    error = "Timeout"
    nb_unanswered += 1

  cmp_time = datetime.datetime.timestamp( datetime.datetime.now() )
  dlt_time = (int(cmp_time*1000000)-int(ref_time*1000000))/1000 # delta
  # nb_bytes = 

  if( target_mac ):

    # Output --------------------------------------------------------------------------------------
    if verbose == 1:
      line = str(nb_bytes) + " bytes from "+target_mac+" ("+target_ip+"): index="+str(seqnum)+" time="+str(dlt_time)+"ms"
    elif verbose == 0:
      line = target_ip + "\t" + target_mac
    elif verbose == -1:
      line = target_mac
    print(line)

    # Stats ---------------------------------------------------------------------------------------
    if dlt_time > max_time:
      max_time = dlt_time
    if dlt_time < min_time:
      min_time = dlt_time

    # Errcode -------------------------------------------------------------------------------------
    exitcode = 0

  else:

    if verbose == 1:
      print("Timeout")
    exitcode = 1

  try:
    time.sleep(wait)
  except KeyboardInterrupt:
    get_summary(target_ip,nb_transmitted,nb_received, nb_unanswered,min_time,max_time)
    exit(130)

get_summary(target_ip,nb_transmitted,nb_received, nb_unanswered,min_time,max_time)

exit(exitcode)

