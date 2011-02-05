#!/usr/bin/env python
import time, struct, sys



# generate and send packets
megabytes = 0.1
size = 10
discontinuous = 0
nbytes = int(1e3 * megabytes)
n = 0
pktno = 0
pkt_size = int(size)

while n < nbytes:
    print (struct.pack('!H', pktno) + (pkt_size - 2) * chr(pktno & 0xff))
    n += pkt_size
    #sys.stderr.write('.')
    if discontinuous and pktno % 5 == 1:
	time.sleep(1)
    pktno += 1
    
                 # wait for it to finish