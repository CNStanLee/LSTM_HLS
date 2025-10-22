#ifndef LAYERS_H
#define LAYERS_H



void MultiThreshold_0_block(
    hls::stream<nn_f32_t> &in0_V,
    hls::stream<nn_int8_t> &out_V
);
void ConvolutionInputGenerator_hls_0(
    hls::stream<ap_uint<8>> &in0_V,
    hls::stream<ap_uint<8>> &out_V
);
void MVAU_hls_0(hls::stream<ap_uint<24>> &in0_V,
                    hls::stream<ap_uint<32>> &out_V
                    );

#endif
