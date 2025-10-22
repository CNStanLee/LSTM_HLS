#ifndef CNN_LSTM_MLP_HPP
#define CNN_LSTM_MLP_HPP

#include "activations.hpp"
#include "cnn_lstm_mlp_weights.hpp"
#include "custom_types.h"
#include "ap_axi_sdata.h"
#include "hls_stream.h"
#include "cnn_lstm_mlp.h"
#include "convlayer.h"
#include "layers.h"
#include <iostream>

// Stream_block_MultiThreshold_0
void Stream_block_MultiThreshold_0(
    hls::stream<ap_axis<32,2,5,6>>& global_input,
    hls::stream<nn_int8_t>& mt0_output,
    const int input_size)
{
    #pragma HLS INLINE off
    
    for(int i = 0; i < input_size; i++) {
        #pragma HLS PIPELINE II=1
        
        ap_axis<32,2,5,6> input_data = global_input.read();
        nn_f32_t accu_value = *reinterpret_cast<nn_f32_t*>(&input_data.data);
        
        hls::stream<nn_f32_t> mt0_in_temp;
        hls::stream<nn_int8_t> mt0_out_temp;
        #pragma HLS STREAM variable=mt0_in_temp depth=2
        #pragma HLS STREAM variable=mt0_out_temp depth=2
        
        mt0_in_temp.write(accu_value);
        MultiThreshold_0_block(mt0_in_temp, mt0_out_temp);
        nn_int8_t out = mt0_out_temp.read();
        
        mt0_output.write(out);
    }
}


void Stream_block_MultiThreshold_0_to_Im2Col_0(
    hls::stream<nn_int8_t>& mt0_output,
    hls::stream<ap_uint<8>>& conv0_input,
    const int input_size)
{
    #pragma HLS INLINE off
    
    for(int i = 0; i < input_size; i++) {
        #pragma HLS PIPELINE II=1
        
        nn_int8_t mt_result = mt0_output.read();
        ap_uint<8> conv_input = reinterpret_cast<ap_uint<8>&>(mt_result);
        conv0_input.write(conv_input);
    }
}

void Stream_block_Im2Col_0(
    hls::stream<ap_uint<8>>& conv0_input,
    hls::stream<ap_uint<8>>& conv0_output)
{
    #pragma HLS INLINE off
    
    ConvolutionInputGenerator_hls_0(conv0_input, conv0_output);
}

void Stream_block_Im2Col_0_to_MVAU_0(
    hls::stream<ap_uint<8>>& conv_output,
    hls::stream<ap_uint<24>>& mvau_input,
    const int conv_output_size)
{
    #pragma HLS INLINE off
    
    const int SIMD1 = 3;
    const int num_mvau_inputs = conv_output_size / SIMD1;
    
    for(int i = 0; i < num_mvau_inputs; i++) {
        #pragma HLS PIPELINE II=1
        
        ap_uint<24> packed_input = 0;
        for(int j = 0; j < SIMD1; j++) {
            #pragma HLS UNROLL
            ap_uint<8> data = conv_output.read();
            packed_input.range((j+1)*8-1, j*8) = data;
        }
        mvau_input.write(packed_input);
    }
}

void Stream_block_MVAU_0(
    hls::stream<ap_uint<24>>& mvau_input,
    hls::stream<ap_uint<32>>& mvau_output)
{
    #pragma HLS INLINE off
    MVAU_hls_0(mvau_input, mvau_output);
}

template<typename InType, typename OutType, int SliceWidth>
void stream_sum_slices(
    hls::stream<InType>& in,
    hls::stream<OutType>& out,
    const int num_elements,
    bool debug = false)
{
    unsigned int total_sum = 0;

    const int num_slices = (sizeof(InType)*8 + SliceWidth - 1) / SliceWidth;

    for (int i = 0; i < num_elements; i++) {
        #pragma HLS PIPELINE II=1

        InType val = in.read();

        if (debug) {
            std::cout << "Element " << i << ": 0x"
                      << std::hex << (uint32_t)val
                      << " / " << std::dec << (uint32_t)val
                      << " → slices: ";
        }

        for (int j = 0; j < num_slices; j++) {
            int high = (j+1)*SliceWidth - 1;
            int low  = j*SliceWidth;
            if (high >= sizeof(InType)*8) high = sizeof(InType)*8 - 1;

            ap_uint<SliceWidth> slice = val.range(high, low);
            total_sum += slice.to_uint();

            if (debug) {
                std::cout << "["
                          //<< j << ": 0x" << std::hex << (uint32_t)slice
                          //<< " / "
						  << std::dec << (uint32_t)slice
                          << "] ";
            }
        }

        if (debug) std::cout << std::endl;

        out.write((OutType)val);
    }

    if (debug) {
        std::cout << "Total sum of all slices (width=" << SliceWidth
                  << "): " << total_sum << std::endl;
    }
}

int test_forward_with_mvau(
    hls::stream<ap_axis<32,2,5,6>>& global_input,
    hls::stream<ap_axis<8,2,5,6>>& global_output)
{
    #pragma HLS INTERFACE mode=axis port=global_input
    #pragma HLS INTERFACE mode=axis port=global_output
    #pragma HLS INTERFACE s_axilite port=return
    #pragma HLS DATAFLOW
    
    const int INPUT_SIZE = 32;
    const int CONV_OUTPUT_SIZE = 90;
    const int MVAU_INPUT_SIZE = 30;
    const int MVAU_OUTPUT_SIZE = 120;

    
    hls::stream<nn_int8_t> stream_00("stream_00");
    hls::stream<ap_uint<8>> stream_01("stream_01");
    hls::stream<ap_uint<8>> stream_02("stream_02");
    hls::stream<ap_uint<24>> stream_03("stream_03");
    hls::stream<ap_uint<32>> stream_04("stream_04");
    hls::stream<ap_uint<32>> stream_05("stream_05");

    #pragma HLS STREAM variable=stream_00 depth=128
    #pragma HLS STREAM variable=stream_01 depth=128
    #pragma HLS STREAM variable=stream_02 depth=256
    #pragma HLS STREAM variable=stream_03 depth=128
    #pragma HLS STREAM variable=stream_04 depth=256
    #pragma HLS STREAM variable=stream_05 depth=256

    Stream_block_MultiThreshold_0(global_input, stream_00, INPUT_SIZE);
    Stream_block_MultiThreshold_0_to_Im2Col_0(stream_00, stream_01, INPUT_SIZE);
    Stream_block_Im2Col_0(stream_01, stream_02);
    Stream_block_Im2Col_0_to_MVAU_0(stream_02, stream_03, CONV_OUTPUT_SIZE);
    Stream_block_MVAU_0(stream_03, stream_04);
    stream_sum_slices<ap_uint<32>, ap_uint<32>, 4>(stream_04, stream_05, MVAU_OUTPUT_SIZE, true);
    return 0;
}

#endif
