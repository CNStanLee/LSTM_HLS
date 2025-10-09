#include <stdio.h>
#include "cnn_lstm_mlp.hpp"
#include "custom_types.h"

int main(void){
	printf("------ behavior test begin ------\r");
	// generate input
	hls::stream<ap_axis<32,2,5,6>> global_input;
	hls::stream<ap_axis<8,2,5,6>> global_output;

	float float_inputs[] = {
	    -0.174079, 1.316306, 0.735104, -1.370410, -0.399291, -0.058488, 2.292501, 0.183736,
	    0.294389, 0.048863, -0.258132, -0.999940, -0.729064, -0.032288, 0.137615, -1.036745,
	    -0.285918, 0.471259, -0.254717, -0.102317, -0.775240, -0.133278, -0.083695, 1.317922,
	    -2.877262, 1.705585, 0.888133, 0.444237, 0.115318, 0.432858, 0.093336, 0.363944
	};

	const int INPUT_SIZE = sizeof(float_inputs) / sizeof(float_inputs[0]);

	printf("input size = %d\r", INPUT_SIZE);
	for (int i = 0; i < INPUT_SIZE; i++) {
	    ap_axis<32,2,5,6> data_inp;
	    float f = float_inputs[i];
	    nn_int32_t bits;
	    memcpy(&bits, &f, sizeof(f));
	    data_inp.data = bits;
//	    data_inp.data = static_cast<nn_int32_t>(float_inputs[i]);
//	    data_inp.data = float_inputs[i];
	    global_input.write(data_inp);
	}
	test_forward(global_input,global_output);

	printf("------ behavior test ended ------\r");
	return 0;
}
