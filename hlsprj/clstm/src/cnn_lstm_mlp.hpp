#ifndef CNN_LSTM_MLP_HPP
#define CNN_LSTM_MLP_HPP

#include "activations.hpp"
#include "cnn_lstm_mlp_weights.hpp"
#include "custom_types.h"
//
#include "ap_axi_sdata.h"
#include "hls_stream.h"
//
#include "cnn_lstm_mlp.h"
#include "custom_types.h"
//
#include "convlayer.h"

int test_forward(
    hls::stream<ap_axis<32,2,5,6>>& global_input,
    hls::stream<ap_axis<8,2,5,6>>& global_output){

    #pragma HLS INTERFACE mode=axis port=global_input
    #pragma HLS INTERFACE mode=axis port=global_output
    #pragma HLS INTERFACE s_axilite port=return
    #pragma HLS PIPELINE II=1  // pipeline interval


	// mt_0
	// NF PE NumTh, input_type, output_type, minimum value of output
    ThresholdsActivation<1, 1, 255, nn_f32_t, nn_int8_t, -256> MultiThreshold_0;
    MultiThreshold_0.load_weights_from_array(MultiThreshold_0_param0);
    // conv_0
    const unsigned int CONV_KERNEL_DIM = 3;
    const unsigned int IFM_CHANNELS = 1;
    const unsigned int IFM_DIM = 32;
    const unsigned int OFM_CHANNELS = 32;
    const unsigned int OFM_DIM = 30;
    const unsigned int SIMD_LANES = 1;
    const unsigned int PE_COUNT = 1;
    ap_resource_dsp dsp_resource;
    ConvLayer_Batch<CONV_KERNEL_DIM, IFM_CHANNELS, IFM_DIM, OFM_CHANNELS, OFM_DIM,
                    SIMD_LANES, PE_COUNT, Identity, Identity, Identity,
                    8, 32, nn_int4_t, PassThroughActivation<nn_int4_t>, ap_resource_dsp> conv_layer;
    conv_layer.load_weights_from_4darray_generic<1, 1>(Conv_0_param0);
    while(!global_input.empty()){
        #pragma HLS LOOP_TRIPCOUNT min=32 max=32

        ap_axis<32,2,5,6> input_data;
        nn_f32_t accu_value;
        nn_int8_t out;
        ap_axis<8,2,5,6> data_oup;
//        ap_axis<32,2,5,6> conv_oup;
    	hls::stream<nn_uint8_t> out_mt0("00");
    	hls::stream<nn_uint32_t> out_conv0("01");
		#pragma HLS STREAM variable=out_mt0 depth=128
		#pragma HLS STREAM variable=out_conv0 depth=128
        // read input data
        input_data = global_input.read();
        // mt0
        accu_value = *reinterpret_cast<nn_f32_t*>(&input_data.data);
        out = MultiThreshold_0.activate(0, 0, accu_value);
        out_mt0.write(out);
        printf("%d ", out);

        // output
        data_oup.data = out;

        // conv0
        conv_layer.execute(out_mt0, out_conv0, 1, dsp_resource);
        global_output.write(data_oup);
    }
	printf("\r");
    return 0;
}

#endif
