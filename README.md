# arping

Scapy version of ARPing linux tool for every UNIX system

# Synopsis

```
Usage: arping <IP adress>
       arping <-t IP> [-I #] [-c #] [-w #] [-q] [-r] [-h]

 -I   : interface
 -t   : target IP
 -r   : show only MAC on output
 -q   : less verbose
 -c # : send # packets
 -w # : wait between packets (default: 1s)
 ```
 
 # Exemples
 
 ```sh
# arping -c 2 172.20.10.1

ARPING 172.20.10.1 from en5 [72:3c:69:c1:95:cf]

Packet from 72:3c:69:1c:96:64 (172.20.10.1): index=1	time=33.461ms
Packet from 72:3c:69:1c:96:64 (172.20.10.1): index=2	time=37.162ms
```
