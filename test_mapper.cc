using namespace std;
#include <iostream>
#include <string>
#include <math.h>
#include <vector>
#include <stdlib.h>


int main()
{
  int d_occupied_carriers = 200;
  int d_fft_length = 400;
  std::string carriers = "FE7F";
  std::vector<int> d_subcarrier_map;
  
  int diff = (d_occupied_carriers - 4*carriers.length()); 
  cout<<diff<<endl;
  while(diff > 7) {
    carriers.insert(0, "f");
    carriers.insert(carriers.length(), "f");
    diff -= 8;
    cout<<diff<<endl;
  }
  
  // if there's extras left to be processed
  // divide remaining to put on either side of current map
  // all of this is done to stick with the concept of a carrier map string that
  // can be later passed by the user, even though it'd be cleaner to just do this
  // on the carrier map itself
  int diff_left=0;
  int diff_right=0;

  // dictionary to convert from integers to ascii hex representation
  char abc[16] = {'0', '1', '2', '3', '4', '5', '6', '7', 
		  '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
  if(diff > 0) {
    char c[2] = {0,0};

    diff_left = (int)ceil((float)diff/2.0f);   // number of carriers to put on the left side
    c[0] = abc[(1 << diff_left) - 1];          // convert to bits and move to ASCI integer
    carriers.insert(0, c);
    
    diff_right = diff - diff_left;	       // number of carriers to put on the right side
    c[0] = abc[0xF^((1 << diff_right) - 1)];   // convert to bits and move to ASCI integer
        carriers.insert(carriers.length(), c);
  }
  cout << carriers<< " len: "<<carriers.length() << endl;
  
  // find out how many zeros to pad on the sides; the difference between the fft length and the subcarrier
  // mapping size in chunks of four. This is the number to pack on the left and this number plus any 
  // residual nulls (if odd) will be packed on the right. 
  diff = (d_fft_length/4 - carriers.length())/2; 

  unsigned int i,j,k;
  for(i = 0; i < carriers.length(); i++) {
    char c = carriers[i];                            // get the current hex character from the string
    for(j = 0; j < 4; j++) {                         // walk through all four bits
      k = (strtol(&c, NULL, 16) >> (3-j)) & 0x1;     // convert to int and extract next bit
      if(k) {                                        // if bit is a 1, 
	d_subcarrier_map.push_back(4*(i+diff) + j);  // use this subcarrier
      }
    }
  }
  for(int ii=0;ii<d_subcarrier_map.size();ii++)
    cout << d_subcarrier_map[ii] << endl;
  cout<<"subcar len: "<<d_subcarrier_map.size()<<endl;
  unsigned long d_nbits = (unsigned long)ceil(log10(2) / log10(2.0));
  cout<<"no of bits: "<<d_nbits<<endl;
}