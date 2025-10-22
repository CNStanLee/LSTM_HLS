#ifndef CNN_LSTM_MLP_HPP
#define CNN_LSTM_MLP_HPP

#include "activations.hpp"
#include "cnn_lstm_mlp_weights.hpp"
#include "custom_types.h"
#include "ap_axi_sdata.h"
#include "hls_stream.h"
#include "cnn_lstm_mlp.h"
#include "convlayer.h"

void MultiThreshold_0_block(
    hls::stream<nn_f32_t> &in0_V,
    hls::stream<nn_int8_t> &out_V
);
void ConvolutionInputGenerator_hls_0(
    hls::stream<ap_uint<8>> &in0_V,
    hls::stream<ap_uint<8>> &out_V
);
void MVAU_hls_0(
    hls::stream<ap_uint<24>> &in0_V,
    hls::stream<ap_uint<96>> &weights_V,
    hls::stream<ap_uint<32>> &out_V
);

// 阶段1: 读取输入并进行MultiThreshold处理
void stage1_input_and_threshold(
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

// 阶段2: 转换数据格式并准备卷积输入
void stage2_prepare_conv_input(
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

// 阶段3: 卷积输入生成器
void stage3_conv_input_generator(
    hls::stream<ap_uint<8>>& conv0_input,
    hls::stream<ap_uint<8>>& conv0_output)
{
    #pragma HLS INLINE off
    
    ConvolutionInputGenerator_hls_0(conv0_input, conv0_output);
}

// 阶段4: 准备MVAU输入 - 将ap_uint<8>打包成ap_uint<24> (SIMD1=3)
void stage4_prepare_mvau_input(
    hls::stream<ap_uint<8>>& conv_output,
    hls::stream<ap_uint<24>>& mvau_input,
    const int conv_output_size)
{
    #pragma HLS INLINE off
    
    const int SIMD1 = 3;
    const int num_mvau_inputs = conv_output_size / SIMD1; // 90/3=30
    
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

// 阶段5: 提供权重流 - 修正版本
// void stage5_provide_weights(
//     hls::stream<ap_uint<96>>& weights_stream,
//     const int num_reps)
// {
//     #pragma HLS INLINE off
    
//     // MVAU配置: 输入维度=3, 输出维度=32, PE1=8, SIMD1=3
//     const int MW1 = 3;   // 输入维度
//     const int MH1 = 32;  // 输出维度
//     const int PE1 = 8;   // 并行处理单元数
//     const int SIMD1 = 3;
//     const int WMEM1 = 4; // MH1/PE1 = 32/8 = 4
    
//     // 权重矩阵 (3输入通道 × 32输出通道)
//     static const ap_int<8> weights[MH1][MW1] = {
//         #include "mvau_weights_include.h"
//     };
    
//     for(int rep = 0; rep < num_reps; rep++) {
//         for(int simd = 0; simd < SIMD1; simd++) {
//             for(int pe_block = 0; pe_block < WMEM1; pe_block++) {
//                 #pragma HLS PIPELINE II=1
                
//                 ap_uint<96> weight_pack = 0;
//                 for(int pe = 0; pe < PE1; pe++) {
//                     #pragma HLS UNROLL
//                     int output_channel = pe_block * PE1 + pe;
//                     ap_int<8> weight_val = weights[output_channel][simd];
//                     // 将有符号权重转换为无符号表示
//                     ap_uint<8> weight_uint = *reinterpret_cast<ap_uint<8>*>(&weight_val);
//                     weight_pack.range((pe+1)*8-1, pe*8) = weight_uint;
//                 }
//                 weights_stream.write(weight_pack);
//             }
//         }
//     }
// }

// void stage5_provide_weights(
//     hls::stream<ap_uint<96>>& weights_stream,
//     const int num_reps)
// {
//     #pragma HLS INLINE off
    
//     const int MW1 = 3;
//     const int MH1 = 32;
//     const int PE1 = 8;
//     const int SIMD1 = 3;
//     const int WP1 = 4;
//     const int NF = 4;
//     const int SF = 1;
    
//     static const ap_int<4> weights[MH1][MW1] = {
//         #include "mvau_weights_include.h"
//     };
    
//     for(int rep = 0; rep < num_reps; rep++) {
//         for(int nf = 0; nf < NF; nf++) {
//             for(int sf = 0; sf < SF; sf++) {
//                 #pragma HLS PIPELINE II=1
                
//                 ap_uint<96> weight_pack = 0;
                
//                 for(int pe = 0; pe < PE1; pe++) {
//                     #pragma HLS UNROLL
//                     int out_ch = nf * PE1 + pe;
                    
//                     for(int simd = 0; simd < SIMD1; simd++) {
//                         #pragma HLS UNROLL
                        
//                         // 直接使用 ap_int<4>，让硬件处理符号
//                         ap_int<4> w = weights[out_ch][simd];
                        
//                         // 转换为 ap_uint<4> 保持位模式
//                         ap_uint<4> w_bits = w.range(3, 0);
                        
//                         int bit_pos = pe * 12 + simd * 4;
//                         weight_pack.range(bit_pos + 3, bit_pos) = w_bits;
//                     }
//                 }
                
//                 weights_stream.write(weight_pack);
//             }
//         }
//     }
// }
void stage5_provide_weights(
    hls::stream<ap_uint<96>>& weights_stream,
    const int num_reps)
{
    #pragma HLS INLINE off
    
    const int MW1 = 3;   // 输入维度
    const int MH1 = 32;  // 输出维度
    const int PE1 = 8;
    const int SIMD1 = 3;
    const int WP1 = 4;
    const int NF = 4;    // MH1/PE1 = 32/8
    const int SF = 1;    // MW1/SIMD1 = 3/3
    
    // 权重矩阵: [输入通道][输出通道] = [3][32]
    static const ap_int<4> weights[MW1][MH1] = {
        #include "mvau_weights_include.h"
    };
    
    // 打印原始权重矩阵（转置查看）
    static bool printed = false;
    if (!printed) {
        printf("=== Original Weights [input_ch][output_ch] ===\n");
        printf("First 8 output channels:\n");
        for(int out_ch = 0; out_ch < 8; out_ch++) {
            printf("Output ch %2d: ", out_ch);
            for(int in_ch = 0; in_ch < 3; in_ch++) {
                printf("%3d ", (int)weights[in_ch][out_ch]);
            }
            printf("\n");
        }
        printed = true;
    }
    
    for(int rep = 0; rep < num_reps; rep++) {
        for(int nf = 0; nf < NF; nf++) {
            for(int sf = 0; sf < SF; sf++) {
                #pragma HLS PIPELINE II=1
                
                ap_uint<96> weight_pack = 0;
                
                // 打包: 每个weight_pack包含8个PE，每个PE有3个SIMD权重
                for(int pe = 0; pe < PE1; pe++) {
                    #pragma HLS UNROLL
                    int out_ch = nf * PE1 + pe;  // 输出通道索引
                    
                    // 每个PE的3个SIMD权重
                    for(int simd = 0; simd < SIMD1; simd++) {
                        #pragma HLS UNROLL
                        
                        // 权重访问: weights[输入通道][输出通道]
                        ap_int<4> w = weights[simd][out_ch];
                        ap_uint<4> w_bits = w.range(3, 0);
                        
                        // 打包位置: PE在高位，SIMD在低位
                        int bit_pos = pe * 12 + simd * 4;
                        weight_pack.range(bit_pos + 3, bit_pos) = w_bits;
                    }
                }
                
                // 验证第一个 weight_pack
                if (rep == 0 && nf == 0 && sf == 0) {
                    printf("\n=== First Weight Pack (96 bits) ===\n");
                    printf("Hex: 0x%024llx\n", (unsigned long long)weight_pack.to_uint64());
                    
                    printf("Unpacked weights [PE][SIMD]:\n");
                    for(int pe = 0; pe < PE1; pe++) {
                        int out_ch = nf * PE1 + pe;
                        printf("  PE%d (out_ch=%2d): ", pe, out_ch);
                        for(int simd = 0; simd < SIMD1; simd++) {
                            int bit_pos = pe * 12 + simd * 4;
                            ap_uint<4> w_bits = weight_pack.range(bit_pos + 3, bit_pos);
                            ap_int<4> w_val;
                            w_val.range(3, 0) = w_bits.range(3, 0);
                            printf("%3d ", (int)w_val);
                        }
                        printf("\n");
                    }
                }
                
                weights_stream.write(weight_pack);
            }
        }
    }
}
// 阶段6: MVAU计算
void stage6_mvau_compute(
    hls::stream<ap_uint<24>>& mvau_input,
    hls::stream<ap_uint<96>>& weights_stream,
    hls::stream<ap_uint<32>>& mvau_output)
{
    #pragma HLS INLINE off
    
    MVAU_hls_0(mvau_input, weights_stream, mvau_output);
}

// 阶段7: 处理MVAU输出 (UINT4打包成32位)
void stage7_process_mvau_output(
    hls::stream<ap_uint<32>>& mvau_output,
    hls::stream<ap_axis<8,2,5,6>>& global_output,
    const int num_output_vectors)
{
    #pragma HLS INLINE off
    
    // MVAU输出: 每个32位包含8个UINT4 (PE1=8)
    const int PE1 = 8;
    const int OUTPUT_CHANNELS = 32; // 总输出通道数
    const int VECTORS_PER_OUTPUT = OUTPUT_CHANNELS / PE1; // 32/8=4
    
    for(int vec_idx = 0; vec_idx < num_output_vectors; vec_idx++) {
        for(int output_vec = 0; output_vec < VECTORS_PER_OUTPUT; output_vec++) {
            #pragma HLS PIPELINE II=1
            
            ap_uint<32> packed_output = mvau_output.read();
            
            // 将32位数据拆分为8个4位值并分别输出
            for(int pe = 0; pe < PE1; pe++) {
                #pragma HLS UNROLL
                ap_uint<4> uint4_val = packed_output.range((pe+1)*4-1, pe*4);
                ap_uint<8> output_byte = uint4_val; // 零扩展到8位
                
                ap_axis<8,2,5,6> data_oup;
                data_oup.data = output_byte;
                data_oup.keep = -1;
                
                // 计算全局索引
                int global_idx = vec_idx * VECTORS_PER_OUTPUT * PE1 + output_vec * PE1 + pe;
                int total_outputs = num_output_vectors * OUTPUT_CHANNELS;
                data_oup.last = (global_idx == total_outputs - 1) ? 1 : 0;
                
                global_output.write(data_oup);
            }
        }
    }
}

// 阶段7替代版本: 直接输出32位数据 (用于调试)
void stage7_write_mvau_output_direct(
    hls::stream<ap_uint<32>>& mvau_output,
    hls::stream<ap_axis<32,2,5,6>>& global_output,
    const int output_size)
{
    #pragma HLS INLINE off
    
    for(int i = 0; i < output_size; i++) {
        #pragma HLS PIPELINE II=1
        
        ap_uint<32> out_data = mvau_output.read();
        
        ap_axis<32,2,5,6> data_oup;
        data_oup.data = out_data;
        data_oup.keep = -1;
        data_oup.last = (i == output_size - 1) ? 1 : 0;
        global_output.write(data_oup);
    }
}

// 原始测试函数保持不变
void stage_threshold_output(
    hls::stream<nn_int8_t>& mt0_output,
    hls::stream<ap_axis<8,2,5,6>>& global_output,
    const int output_size)
{
    #pragma HLS INLINE off
    
    for(int i = 0; i < output_size; i++) {
        #pragma HLS PIPELINE II=1
        
        nn_int8_t mt_result = mt0_output.read();
        ap_uint<8> out_data = reinterpret_cast<ap_uint<8>&>(mt_result);
        
        ap_axis<8,2,5,6> data_oup;
        data_oup.data = out_data;
        data_oup.keep = -1;
        data_oup.last = (i == output_size - 1) ? 1 : 0;
        global_output.write(data_oup);
    }
}

void stage4_write_output(
    hls::stream<ap_uint<8>>& conv0_output,
    hls::stream<ap_axis<8,2,5,6>>& global_output,
    const int output_size)
{
    #pragma HLS INLINE off

    for(int i = 0; i < output_size; i++) {
        #pragma HLS PIPELINE II=1

        ap_uint<8> out_conv = conv0_output.read();
        ap_axis<8,2,5,6> data_oup;
        data_oup.data = out_conv;
        data_oup.keep = -1;
        data_oup.last = (i == output_size - 1) ? 1 : 0;
        global_output.write(data_oup);
    }
}

int test_forward2(
    hls::stream<ap_axis<32,2,5,6>>& global_input,
    hls::stream<ap_axis<8,2,5,6>>& global_output)
{
    #pragma HLS INTERFACE mode=axis port=global_input
    #pragma HLS INTERFACE mode=axis port=global_output
    #pragma HLS INTERFACE s_axilite port=return
    #pragma HLS DATAFLOW
    
    const int INPUT_SIZE = 32;
    const int OUTPUT_SIZE = 32;
    
    hls::stream<nn_int8_t> mt0_output("mt0_output");
    #pragma HLS STREAM variable=mt0_output depth=128
    
    stage1_input_and_threshold(global_input, mt0_output, INPUT_SIZE);
    stage_threshold_output(mt0_output, global_output, OUTPUT_SIZE);

    return 0;
}

int test_forward(
    hls::stream<ap_axis<32,2,5,6>>& global_input,
    hls::stream<ap_axis<8,2,5,6>>& global_output)
{
    #pragma HLS INTERFACE mode=axis port=global_input
    #pragma HLS INTERFACE mode=axis port=global_output
    #pragma HLS INTERFACE s_axilite port=return
    #pragma HLS DATAFLOW
    
    const int INPUT_SIZE = 32;
    const int OUTPUT_SIZE = 90;
    
    hls::stream<nn_int8_t> mt0_to_conv("mt0_to_conv");
    hls::stream<ap_uint<8>> conv_input("conv_input");
    hls::stream<ap_uint<8>> conv_output("conv_output");
    #pragma HLS STREAM variable=mt0_to_conv depth=128
    #pragma HLS STREAM variable=conv_input depth=128
    #pragma HLS STREAM variable=conv_output depth=256
    
    stage1_input_and_threshold(global_input, mt0_to_conv, INPUT_SIZE);
    stage2_prepare_conv_input(mt0_to_conv, conv_input, INPUT_SIZE);
    stage3_conv_input_generator(conv_input, conv_output);
    stage4_write_output(conv_output, global_output, OUTPUT_SIZE);

    return 0;
}

// 修正后的完整MVAU前向传播
int test_forward_with_mvau(
    hls::stream<ap_axis<32,2,5,6>>& global_input,
    hls::stream<ap_axis<8,2,5,6>>& global_output)
{
    #pragma HLS INTERFACE mode=axis port=global_input
    #pragma HLS INTERFACE mode=axis port=global_output
    #pragma HLS INTERFACE s_axilite port=return
    #pragma HLS DATAFLOW
    
    // 常量定义
    const int INPUT_SIZE = 32;
    const int CONV_OUTPUT_SIZE = 90;  // 30 * 3
    const int MVAU_INPUT_SIZE = 30;   // numReps
    const int MVAU_OUTPUT_VECTORS = 30 * 4; // 30个位置 × 4个输出向量(32/8=4)
    const int FINAL_OUTPUT_SIZE = 30 * 32;  // 30个位置 × 32个输出通道
    
    // 中间流
    hls::stream<nn_int8_t> mt0_to_conv("mt0_to_conv");
    hls::stream<ap_uint<8>> conv_input("conv_input");
    hls::stream<ap_uint<8>> conv_output("conv_output");
    hls::stream<ap_uint<24>> mvau_input("mvau_input");
    hls::stream<ap_uint<96>> weights_stream("weights_stream");
    hls::stream<ap_uint<32>> mvau_output("mvau_output");
    
    #pragma HLS STREAM variable=mt0_to_conv depth=128
    #pragma HLS STREAM variable=conv_input depth=128
    #pragma HLS STREAM variable=conv_output depth=256
    #pragma HLS STREAM variable=mvau_input depth=128
    #pragma HLS STREAM variable=weights_stream depth=256
    #pragma HLS STREAM variable=mvau_output depth=256
    
    // 执行完整流水线
    stage1_input_and_threshold(global_input, mt0_to_conv, INPUT_SIZE);
    stage2_prepare_conv_input(mt0_to_conv, conv_input, INPUT_SIZE);
    stage3_conv_input_generator(conv_input, conv_output);
    stage4_prepare_mvau_input(conv_output, mvau_input, CONV_OUTPUT_SIZE);
    stage5_provide_weights(weights_stream, MVAU_INPUT_SIZE);
    stage6_mvau_compute(mvau_input, weights_stream, mvau_output);
    stage7_process_mvau_output(mvau_output, global_output, MVAU_INPUT_SIZE);

    return 0;
}

// 用于调试的MVAU版本，输出32位原始数据
int test_forward_with_mvau_debug(
    hls::stream<ap_axis<32,2,5,6>>& global_input,
    hls::stream<ap_axis<32,2,5,6>>& global_output)
{
    #pragma HLS INTERFACE mode=axis port=global_input
    #pragma HLS INTERFACE mode=axis port=global_output
    #pragma HLS INTERFACE s_axilite port=return
    #pragma HLS DATAFLOW
    
    const int INPUT_SIZE = 32;
    const int CONV_OUTPUT_SIZE = 90;
    const int MVAU_INPUT_SIZE = 30;
    const int MVAU_OUTPUT_SIZE = 120; // 30 * 4
    
    hls::stream<nn_int8_t> mt0_to_conv("mt0_to_conv");
    hls::stream<ap_uint<8>> conv_input("conv_input");
    hls::stream<ap_uint<8>> conv_output("conv_output");
    hls::stream<ap_uint<24>> mvau_input("mvau_input");
    hls::stream<ap_uint<96>> weights_stream("weights_stream");
    hls::stream<ap_uint<32>> mvau_output("mvau_output");
    
    #pragma HLS STREAM variable=mt0_to_conv depth=128
    #pragma HLS STREAM variable=conv_input depth=128
    #pragma HLS STREAM variable=conv_output depth=256
    #pragma HLS STREAM variable=mvau_input depth=128
    #pragma HLS STREAM variable=weights_stream depth=256
    #pragma HLS STREAM variable=mvau_output depth=256
    
    stage1_input_and_threshold(global_input, mt0_to_conv, INPUT_SIZE);
    stage2_prepare_conv_input(mt0_to_conv, conv_input, INPUT_SIZE);
    stage3_conv_input_generator(conv_input, conv_output);
    stage4_prepare_mvau_input(conv_output, mvau_input, CONV_OUTPUT_SIZE);
    stage5_provide_weights(weights_stream, MVAU_INPUT_SIZE);
    stage6_mvau_compute(mvau_input, weights_stream, mvau_output);
    stage7_write_mvau_output_direct(mvau_output, global_output, MVAU_OUTPUT_SIZE);

    return 0;
}

#endif