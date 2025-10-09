#ifndef CNN_LSTM_MLP_H
#define CNN_LSTM_MLP_H
#include "activations.hpp"
#include "cnn_lstm_mlp_weights.hpp"
#include "custom_types.h"
//
#include "ap_axi_sdata.h"
#include "hls_stream.h"
int test_forward(
		//inputs stream
		hls::stream<ap_axis<32,2,5,6>>& global_input,
		//output stream
		hls::stream<ap_axis<32,2,5,6>>& global_output);

#endif
