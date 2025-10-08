#ifndef N_CNN_HPP
#define N_CNN_HPP
// *************************************
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
	// ------------------------------------------------------------------------------------
	// Multi-Thresholding
	// ------------------------------------------------------------------------------------
	ThresholdsActivation<
		1, // NF
	 	1, // PE
	  	Act_N_255, // NumTh
	   	nn_f32_t, // InputType
	    nn_int8_t, // OutputType
		-128 // ActVal
	> MultiThreshold_0;
	// ------------------------------------------------------------------------------------
	ThresholdsActivation<
		32, // NF
	 	1, // PE
	  	Act_N_255, // NumTh
	   	nn_int32_t, // InputType
	    nn_uint4_t, // OutputType
		0 // ActVal
	> MultiThreshold_3;
	// ------------------------------------------------------------------------------------
	ThresholdsActivation<
		64, // NF
		1, // PE
		Act_N_255, // NumTh
		nn_int32_t, // InputType
		nn_uint4_t, // OutputType
		0 // ActVal
	> MultiThreshold_4;
	// ------------------------------------------------------------------------------------
	// Convs
	// ------------------------------------------------------------------------------------
	myConvLayer_Batch<
		3,  // ConvKernelDim (3x1)
		1,  // InuputFeatureMapChannels
		32, // InuputFeatureMapDim(shape)
		32,  // OFMChannels
		30, // OFMDim (32-3+1)
		1,  // SIMD
		1,  // PE
		nn_int8_t,//TSrcI,
		nn_int32_t,//TDstI,
		nn_int4_t, //TWeightI
		8, // Input Stream width
		8, // Output Stream widths
		nn_int4_t,
		PassThroughActivation<nn_int4_t>,
		ap_resource_dsp()
	> Conv_0;
	// ------------------------------------------------------------------------------------
	myConvLayer_Batch<
		3,  // ConvKernelDim (3x1)
		32, // InuputFeatureMapChannels
		30, // InuputFeatureMapDim(shape)
		64,  // OFMChannels
		28, // OFMDim (30-3+1)
		1,  // SIMD
		1,  // PE
		nn_uint4_t,//TSrcI,
		nn_int32_t,//TDstI,
		nn_int4_t,//TWeightI,
		8, // Input Stream width
		8, // Output Stream widths
		nn_int4_t,
		PassThroughActivation<nn_int4_t>,
		ap_resource_dsp()
	> Conv_1;
	// ------------------------------------------------------------------------------------
	// Initializations of weights and thresholds
	// ------------------------------------------------------------------------------------
}
#endif
