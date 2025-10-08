#ifndef CNN_LSTM_MLP_HPP
#define CNN_LSTM_MLP_HPP
#include "activations.hpp"
#include "cnn_lstm_mlp_weights.hpp"
#include "custom_types.h"
// Multi-threshold
void init_weights(ThresholdsActivation& th, mt_type mt) {
    for (unsigned pe = 0; pe < 1; pe++) {
        for (unsigned nf = 0; nf < Out_N; nf++) {
            for (unsigned th_idx = 0; th_idx < Act_N_62; th_idx++) {
                th.m_thresholds[pe][nf][th_idx] = mt[nf][th_idx];
            }
        }
    }
}
// ------------------------------------------------------------------------------------
// define
// ------------------------------------------------------------------------------------
void multi_threshold_0(hls::stream<ap_axis<32,2,5,6>>& cnn_input,
					   hls::stream<ap_axis<32,2,5,6>>& cnn_output,
					   int NF,
					   int PE,
					   ){
	// ------------------------------------------------------------------------------------
	// Interfaces
	// ------------------------------------------------------------------------------------
	#pragma HLS INTERFACE mode=axis port=cnn_input
	#pragma HLS INTERFACE mode=axis port=cnn_output
	#pragma HLS INTERFACE s_axilite port=return
	// ------------------------------------------------------------------------------------
	// define
	// ------------------------------------------------------------------------------------
	ThresholdsActivation<
		1, // NF
	 	1, // PE
	  	Act_N_255, // NumTh
	   	nn_f32_t, // InputType
	    nn_int8_t, // OutputType
		-128 // ActVal
	> MultiThreshold_0;
	init_weights(MultiThreshold_0, MultiThreshold_0_param0);
}

#endif
