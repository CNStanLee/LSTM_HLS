#ifndef CNN_LSTM_MLP_HPP
#define CNN_LSTM_MLP_HPP
#include "activations.hpp"
#include "cnn_lstm_mlp_weights.hpp"
#include ""
// Multi-threshold
void multi_threshold_0(hls::stream<ap_axis<32,2,5,6>>& cnn_input,
					   hls::stream<ap_axis<32,2,5,6>>& cnn_output){
	// ------------------------------------------------------------------------------------
	// Interfaces
	// ------------------------------------------------------------------------------------
	#pragma HLS INTERFACE mode=axis port=cnn_input
	#pragma HLS INTERFACE mode=axis port=cnn_output
	#pragma HLS INTERFACE s_axilite port=return
	ThresholdsActivation<
		1, // NF
	 	1, // PE
	  	Act_N_255, // NumTh
	   	nn_f32_t, // InputType
	    nn_int8_t, // OutputType
		-128 // ActVal
	> MultiThreshold_0;
}


#endif
