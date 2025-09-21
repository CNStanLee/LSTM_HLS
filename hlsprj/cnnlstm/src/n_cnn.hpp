#include "ap_axi_sdata.h"
#include <stdio.h>
#include "hls_stream.h"
#include <algorithm>
#include <functional>
#include <string>
#include <fstream>
#include <sstream>
#include "hls_print.h"
// *************************************
#include "g_config.h"
#include "n_cnn_weights.hpp"
// *************************************

void n_cnn_layer_module(
		hls::stream<ap_axis<32,2,5,6>>& cnn_input,
		hls::stream<ap_axis<32,2,5,6>>& cnn_output){
	// ------------------------------------------------------------------------------------
	// Interfaces
	// ------------------------------------------------------------------------------------
	#pragma HLS INTERFACE mode=axis port=cnn_input
	#pragma HLS INTERFACE mode=axis port=cnn_output
	#pragma HLS INTERFACE s_axilite port=return
	// ------------------------------------------------------------------------------------
	// Intermediate stream definitions
	// ------------------------------------------------------------------------------------
	hls::stream<nn_int8_t> MultiThreshold_0_out0("MultiThreshold_0_out0");
	hls::stream<nn_int32_t> Conv_0_out0("Conv_0_out0");
	hls::stream<nn_uint4_t> MultiThreshold_3_out0("MultiThreshold_3_out0");
	hls::stream<nn_int32_t> Conv_1_out0("Conv_1_out0");
	hls::stream<nn_uint4_t> MultiThreshold_4_out0("MultiThreshold_4_out0");
	hls::stream<nn_uint4_t> MaxPool_0_out0("MaxPool_0_out0");
	hls::stream<nn_uint4_t> Transpose_0_out0("Transpose_0_out0");
	hls::stream<nn_uint4_t> Reshape_0_out0("Reshape_0_out0");
	// ------------------------------------------------------------------------------------
	// FIFO depth pragmas
	// ------------------------------------------------------------------------------------
	#pragma HLS STREAM variable=MultiThreshold_0_out0 depth=128
	#pragma HLS STREAM variable=Conv_0_out0 depth=128
	#pragma HLS STREAM variable=MultiThreshold_3_out0 depth=128
	#pragma HLS STREAM variable=Conv_1_out0 depth=128
	#pragma HLS STREAM variable=MultiThreshold_4_out0 depth=128
	#pragma HLS STREAM variable=MaxPool_0_out0 depth=128
	#pragma HLS STREAM variable=Transpose_0_out0 depth=128
	#pragma HLS STREAM variable=Reshape_0_out0 depth=128
	// ------------------------------------------------------------------------------------
	// Initializations of ops
	// ------------------------------------------------------------------------------------
	ThresholdsActivation<1, 1, Act_N_255, nn_f32_t, nn_int8_t,-128> MultiThreshold_0;
	//ThresholdsActivation<1, 1, Act_N_255, nn_int32_t, nn_uint4_t,-128> MultiThreshold_3;
	// ------------------------------------------------------------------------------------
	// Initializations of weights and thresholds
	// ------------------------------------------------------------------------------------
}
