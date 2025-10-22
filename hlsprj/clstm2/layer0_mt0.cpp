#include "bnn-library.h"
#include "cnn_lstm_mlp_weights.hpp"
#include "activations.hpp"
#include "layers.h"

void MultiThreshold_0_block(
    hls::stream<nn_f32_t> &in0_V,
    hls::stream<nn_int8_t> &out_V
){
    #pragma HLS INTERFACE axis port=in0_V
    #pragma HLS INTERFACE axis port=out_V
    #pragma HLS INTERFACE ap_ctrl_none port=return

    ThresholdsActivation<1, 1, 255, nn_f32_t, nn_int8_t, -256> MultiThreshold_0; 
    MultiThreshold_0.load_weights_from_array(MultiThreshold_0_param0);

    nn_f32_t accu_value = in0_V.read();          // 直接读取 float
    nn_int8_t out = MultiThreshold_0.activate(0, 0, accu_value); // 激活计算
    out_V.write(out);                            // 输出结果
}

