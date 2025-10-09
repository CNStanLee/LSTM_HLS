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

    const int NF = 1;
    const int PE = 1;
    const int NumTh = 255;

    ThresholdsActivation<1, 1, NumTh, nn_f32_t, nn_int8_t, -NumTh> MultiThreshold_0;
    MultiThreshold_0.load_weights_from_array(MultiThreshold_0_param0);

    while(!global_input.empty()){
        #pragma HLS LOOP_TRIPCOUNT min=32 max=32

        ap_axis<32,2,5,6> input_data;
        nn_f32_t accu_value;
        nn_int8_t out;
//        ap_axis<32,2,5,6> output_data;

        input_data = global_input.read();
        accu_value = *reinterpret_cast<nn_f32_t*>(&input_data.data);
        out = MultiThreshold_0.activate(0, 0, accu_value);
        printf("output here\r");
//        output_data.data = out;
//        output_data.keep = input_data.keep;
//        output_data.strb = input_data.strb;
//        output_data.user = input_data.user;
//        output_data.last = input_data.last;
//        output_data.id = input_data.id;
//        output_data.dest = input_data.dest;

//        global_output.write(output_data);
    }
    return 0;
}

#endif
