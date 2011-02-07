#!/usr/bin/env python

import time, struct, sys
sys.path.append('/usr/local/lib/python2.6/dist-packages/gnuradio/gr_ofdm')
sys.path.append('/usr/local/lib/python2.6/dist-packages/gnuradio/howto')
import math
from gnuradio import gr, ofdm_packet_utils
import gnuradio.gr.gr_threading as _threading
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from array import array
from gnuradio.blks2impl import psk, qam
import gr_ofdm
#import howto




class ofdm_mod(gr.top_block):
        def __init__(self):
		parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
		expert_grp = parser.add_option_group("Expert")
		parser.add_option("-s", "--size", type="eng_float", default=400,
			  help="set packet size [default=%default]")
		parser.add_option("-M", "--megabytes", type="eng_float", default=1.0,
			  help="set megabytes to transmit [default=%default]")
		parser.add_option("","--discontinuous", action="store_true", default=False,
			  help="enable discontinuous mode")
		(options, args) = parser.parse_args ()
		msgq_limit=2
		
                gr.top_block.__init__(self)
                padded_preambles = list()
                
                # Set of pre-defined parameters. In actual code this is passed as parameter in options
                #known_symb = [-1, -1, 1, -1, 1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1]
                known_symb = 1000 *[1,-1]
                fft_length = 512
                occupied_tones = 200
                cp_length = 128
                pad_for_usrp = True
                modulation = "qpsk"
                
                zeros_on_left= int(math.ceil((fft_length - occupied_tones)/2.0))
                ksfreq = known_symb[0:occupied_tones]
                preambles = (ksfreq,)
                #print zeros_on_left
                for pre in preambles:
                        padded = fft_length*[0,]
                        padded[zeros_on_left : zeros_on_left + occupied_tones] = pre
                        padded_preambles.append(padded)
                        
                        
                symbol_length = fft_length + cp_length
		
		#mods returns the number of points in the constellation given the index as the mod type "bpsk" etc
		mods = {"bpsk": 2, "qpsk": 4, "8psk": 8, "qam8": 8, "qam16": 16, "qam64": 64, "qam256": 256}
		arity = mods[modulation]
		
		rot = 1
		if modulation == "qpsk":
		    rot = (0.707+0.707j)
		    
		if(modulation.find("psk") >= 0):#check if it is psk or qpsk, returns the position of string "psk"
		    rotated_const = map(lambda pt: pt * rot, psk.gray_constellation[arity])
		elif(modulation.find("qam") >= 0):
		    rotated_const = map(lambda pt: pt * rot, qam.constellation[arity])
		#print rotated_const
		
		self._pkt_input = gr_ofdm.ofdm_mapper_bcv(rotated_const, msgq_limit,
						    occupied_tones,fft_length)
                self.preambles_2 = gr.ofdm_insert_preamble(fft_length,padded_preambles)
                
                #Setting up the user defined data to test the working of the blocks
                data1 = 512*[complex(2,3)] #How to generate complex modulated values
                twos = 511*[1]
                twos_arr = array('B',twos)
		data2 = array('B',[1])
		data2.extend(twos_arr)
                #print data
                
                
		self.data_src1 = gr.vector_source_c(data1,True,16)
		self.data_src2 = gr.vector_source_b(data2,True,1)
		self.sink_n  = gr.vector_sink_c(512)
		
		# End of data setting
		
		self.sink_file = gr.file_sink(512*gr.sizeof_gr_complex,'pad')
		v2s = gr.vector_to_stream(4096,1)
		
                self.connect((self._pkt_input,0),(self.preambles_2,0))
		self.connect((self._pkt_input,1),(self.preambles_2,1))
		self.connect((self.preambles_2,0),self.sink_n)
		self.connect((self.preambles_2,0),self.sink_file)
	def print_data(self):
		self.result_data = self.sink_n.data()
		print self.result_data
	
	def send_pkt(self, payload='', eof=False):
		pad_for_usrp = True
		if eof:
		    msg = gr.message(1) # tell self._pkt_input we're not sending any more packets
		else:
		    # print "original_payload =", string_to_hex_list(payload)
		    pkt = ofdm_packet_utils.make_packet(payload, 1, 1, pad_for_usrp, whitening=True)
		    
		    #print "pkt =", string_to_hex_list(pkt)
		    msg = gr.message_from_string(pkt)
		self._pkt_input.msgq().insert_tail(msg)
		                
def main():
	tb = ofdm_mod()
	
	tb.start()
	megabytes = 1
	size = 400
	discontinuous = 0
	# generate and send packets
	nbytes = int(1e4 * megabytes)
	n = 0
	pktno = 0
	pkt_size = int(size)

	while n < nbytes:
	    tb.send_pkt(struct.pack('!H', pktno) + (pkt_size - 2) * chr(pktno & 0xff))
	    n += pkt_size
	    sys.stderr.write('.')
	    if discontinuous and pktno % 5 == 1:
		time.sleep(1)
	    pktno += 1
	    #gr_ofdm.set_new_carriermap('CFE7FC',occupied_tones)
	    
	tb.send_pkt(eof=True)
	tb.wait()                       # wait for it to finish
	#tb.print_data()
	#tb.wait()
	#tb.stop()
	#tb.run()
if __name__== '__main__':
	#main()	
	#tb = ofdm_mod()
	try:
	  #tb.start()
	  #tb.print_data()
	  main()
	except KeyboardInterrupt:
	  #tb.stop()
	  pass


