#!/usr/bin/env python

import math
from gnuradio import gr, ofdm_packet_utils
import gnuradio.gr.gr_threading as _threading
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from array import array


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
		
                gr.top_block.__init__(self)
                padded_preambles = list()
                known_symb = [-1, -1, 1, -1, 1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1]
                fft_length = 16
                occupied_tones = 4
                zeros_on_left= int(math.ceil((fft_length - occupied_tones)/2.0))
                ksfreq = known_symb[0:occupied_tones]
                preambles = (ksfreq,)
                print zeros_on_left
                for pre in preambles:
                        padded = fft_length*[0,]
                        padded[zeros_on_left : zeros_on_left + occupied_tones] = pre
                        padded_preambles.append(padded)
                self.preambles_2 = gr.ofdm_insert_preamble(fft_length, padded_preambles)
                data1 = 512*[complex(2,3)] #How to generate complex modulated values
                twos = 511*[1]
                twos_arr = array('B',twos)
		data2 = array('B',[1])
		data2.extend(twos_arr)
                #print data
		self.data_src1 = gr.vector_source_c(data1,True,16)
		self.data_src2 = gr.vector_source_b(data2,True,1)
		self.data_src3 = gr.null_source(128)
		self.data_src4 = gr.null_source(1)
		self.sink_n  = gr.vector_sink_c(16)
		
		self.sink_file = gr.file_sink(16*gr.sizeof_gr_complex,'pad')
		v2s = gr.vector_to_stream(128,1)
		
                self.connect(self.data_src1,(self.preambles_2,0))
		self.connect(self.data_src2,(self.preambles_2,1))
		self.connect((self.preambles_2,0),self.sink_n)
		self.connect((self.preambles_2,0),self.sink_file)
	def print_data(self):
		self.result_data = self.sink_n.data()
		print self.result_data
		                
def main():
  
	parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	expert_grp = parser.add_option_group("Expert")
	parser.add_option("-s", "--size", type="eng_float", default=400,
                      help="set packet size [default=%default]")
	parser.add_option("-M", "--megabytes", type="eng_float", default=1.0,
                      help="set megabytes to transmit [default=%default]")
	parser.add_option("","--discontinuous", action="store_true", default=False,
                      help="enable discontinuous mode")
	(options, args) = parser.parse_args ()
	#tb = ofdm_mod(options)
	#tb.start()
	#tb.print_data()
	#tb.wait()
	#tb.stop()
	#tb.run()
if __name__== '__main__':
	#main()	
	tb = ofdm_mod()
	try:
	  tb.start()
	  #tb.print_data()
	except KeyboardInterrupt:
	  tb.stop()
	  #pass


