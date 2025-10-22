
#define AP_INT_MAX_W 128

#include "bnn-library.h"

// includes for network parameters
#include "slidingwindow.h"

// defines for network parameters

            #define ConvKernelDim1_x 3

            #define IFMChannels1 32

            #define Input_precision1 4

            #define IFMDim1_x 30

            #define OFMDim1_x 28

            #define Stride1_x 1

            #define SIMD1 32

            #define numReps 1
            

void ConvolutionInputGenerator_hls_1(hls::stream<ap_uint<SIMD1*Input_precision1>> &in0_V,
                    hls::stream<ap_uint<SIMD1*Input_precision1>> &out_V)
{
#pragma HLS INTERFACE axis port=in0_V
#pragma HLS INTERFACE axis port=out_V
#pragma HLS INTERFACE ap_ctrl_none port=return
ConvolutionInputGenerator_1D<ConvKernelDim1_x, IFMChannels1, Input_precision1,
                IFMDim1_x, OFMDim1_x, Stride1_x, SIMD1>
                (in0_V, out_V, numReps, ap_resource_lutram());
}
