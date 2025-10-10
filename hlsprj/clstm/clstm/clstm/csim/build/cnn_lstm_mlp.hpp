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

int test_forward(
    hls::stream<ap_axis<32,2,5,6>>& global_input,
    hls::stream<ap_axis<8,2,5,6>>& global_output){

    #pragma HLS INTERFACE mode=axis port=global_input
    #pragma HLS INTERFACE mode=axis port=global_output
    #pragma HLS INTERFACE s_axilite port=return
    #pragma HLS PIPELINE II=1  // pipeline interval

	//NF PE NumTh, input_type, output_type, minimum value of output
    ThresholdsActivation<1, 1, 255, nn_f32_t, nn_int8_t, -256> MultiThreshold_0;
    MultiThreshold_0.load_weights_from_array(MultiThreshold_0_param0);

    while(!global_input.empty()){
        #pragma HLS LOOP_TRIPCOUNT min=32 max=32

        ap_axis<32,2,5,6> input_data;
        nn_f32_t accu_value;
        nn_int8_t out;
        ap_axis<8,2,5,6> data_oup;
        // read input data
        input_data = global_input.read();
        // mt0
        //accu_value = *reinterpret_cast<nn_f32_t*>(&input_data.data);
        accu_value = input_data.data;
        out = MultiThreshold_0.activate(0, 0, accu_value);
        printf("%d ", out);
        // output
        data_oup.data = out;
        global_output.write(data_oup);
    }
	printf("\r");
    return 0;
}

#endif
