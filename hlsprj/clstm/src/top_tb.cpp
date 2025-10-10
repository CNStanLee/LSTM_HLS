#include <stdio.h>
#include "cnn_lstm_mlp.hpp"
#include "custom_types.h"

int main(void){
	printf("------ behavior test begin ------\r");
	// generate input
	hls::stream<ap_axis<32,2,5,6>> global_input;
	hls::stream<ap_axis<8,2,5,6>> global_output;

	float float_inputs[] = {
	    -0.234664, 0.417880, -0.191400, -0.139787, 0.220556, 0.027209, -0.426979, 0.250457,
	    -0.074330, 0.242246, -0.447144, -0.460665, -0.429546, 0.219645, -0.481580, -0.334149,
	    0.076268, -0.093793, 0.108359, 0.081015, 0.478529, -0.134894, -0.009770, 0.476819,
	    0.092038, -0.305413, 0.199973, 0.285488, 0.412750, -0.458805, 0.301407, 0.494747
	};


	const int INPUT_SIZE = sizeof(float_inputs) / sizeof(float_inputs[0]);

	printf("input size = %d\r", INPUT_SIZE);
	for (int i = 0; i < INPUT_SIZE; i++) {
	    ap_axis<32,2,5,6> data_inp;
	    float f = float_inputs[i];
	    nn_int32_t bits;
	    memcpy(&bits, &f, sizeof(f));
	    data_inp.data = bits;
	    global_input.write(data_inp);
	}
	printf("------ forward  ------\r");
	test_forward(global_input,global_output);
	printf("------ reading results  ------\r");
	while(!global_output.empty()){
		ap_axis<8,2,5,6> data_oup;
		nn_uint8_t result;
		data_oup = global_output.read();
		result = *reinterpret_cast<nn_uint8_t*>(&data_oup.data);
		printf("%d ", result);
	}
	printf("\r");
	printf("------ behavior test ended ------\r");
	return 0;
}
