#ifndef G_CONFIG_H
#define G_CONFIG_H
// *************************************
#include <iostream>
#include <fstream>
#include <cmath>
using namespace std;
#include "ap_int.h"
#include "ap_fixed.h"
#include "ap_axi_sdata.h"
#include "hls_stream.h"
#include "activations.hpp"
#include "eltwise.hpp"
#include "mvau.hpp"
#include "weights.hpp"
#include "mac.hpp"
#include "utils.hpp"
// *************************************
constexpr unsigned Inp_N = 10; //This factor defines the input length at each time step.
constexpr unsigned Out_N = 20; //This factor defines the number of LSTM cells in the LSTM layer.
constexpr unsigned Act_N_255 = 255;// This factor defines the number of thresholds or quantization level (2 ^^ n - 1)
constexpr unsigned Act_N_63 = 63;
constexpr unsigned Act_N_62 = 62;
constexpr unsigned num_lstm_steps = 2; //Number of iterations in the LSTM loop. *Lookback*
constexpr unsigned num_test_inputs = 3; //Number of test sequences
// *************************************
using nn_f32_t = float;
using nn_uint4_t = ap_uint<4>;
using nn_int4_t = ap_int<4>;
using nn_uint6_t = ap_uint<6>;
using nn_int6_t = ap_int<6>;
using nn_int7_t = ap_int<7>;
using nn_int8_t = ap_int<8>;
using nn_int9_t = ap_int<9>;
using nn_uint8_t = ap_uint<8>;
using nn_uint32_t = ap_uint<32>;
using nn_int32_t = ap_int<32>;
// *************************************
#endif // G_CONFIG_H
