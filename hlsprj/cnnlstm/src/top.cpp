#include "pipeline-lstm-header.h"
#include "ap_axi_sdata.h"
#include <stdio.h>
#include "hls_stream.h"
#include <algorithm>
#include <functional>
#include <string>
#include <fstream>
#include <sstream>
#include "hls_print.h"


//---------------- MultiThresholding requirements -------------------------------
// Multithreshold object creation
ThresholdsActivation<1, 1, Act_N_255, qlstm_f32_t, qlstm_int8_t,-128> th0;
ThresholdsActivation<1, 1, Act_N_255, qlstm_f32_t, qlstm_int8_t,-128> th1;
ThresholdsActivation<1, 1, Act_N_63, qlstm_f32_t, qlstm_int6_t,-32> th2;
ThresholdsActivation<Out_N, 1, Act_N_62, qlstm_int32_t, qlstm_int6_t,-31> th3;
ThresholdsActivation<Out_N, 1, Act_N_62, qlstm_int32_t, qlstm_int6_t,-31> th4;
ThresholdsActivation<Out_N, 1, Act_N_62, qlstm_int32_t, qlstm_int6_t,-31> th5;
ThresholdsActivation<Out_N, 1, Act_N_62, qlstm_int32_t, qlstm_int6_t,-31> th6;
ThresholdsActivation<1, 1, Act_N_63, qlstm_int8_t, qlstm_uint6_t,0,comp::less_equal<qlstm_int8_t,qlstm_int8_t>> th_act7; //
ThresholdsActivation<1, 1, Act_N_63, qlstm_int8_t, qlstm_int7_t,-31,comp::less_equal<qlstm_int8_t,qlstm_int8_t>> th_act8; //
ThresholdsActivation<1, 1, Act_N_63, qlstm_int8_t, qlstm_uint6_t,0,comp::less_equal<qlstm_int8_t,qlstm_int8_t>> th_act9;
ThresholdsActivation<1, 1, Act_N_63, qlstm_int8_t, qlstm_uint6_t,0,comp::less_equal<qlstm_int8_t,qlstm_int8_t>> th_act10;
ThresholdsActivation<1, 1, Act_N_62, qlstm_int32_t, qlstm_int6_t,-31> th11; //try both 9 and 10 with int6 output type later
ThresholdsActivation<1, 1, Act_N_62, qlstm_int32_t, qlstm_int6_t,-31> th12;
ThresholdsActivation<1, 1, Act_N_62, qlstm_int32_t, qlstm_int6_t,-31,comp::less_equal<qlstm_int32_t,qlstm_int32_t>> th13;
ThresholdsActivation<1, 1, Act_N_62, qlstm_int32_t, qlstm_int6_t,-31,comp::less_equal<qlstm_int32_t,qlstm_int32_t>> th14;
ThresholdsActivation<1, 1, Act_N_63, qlstm_int8_t, qlstm_int7_t, -31 ,comp::less_equal<qlstm_int8_t,qlstm_int8_t>> th15; // ,comp::less_equal<qlstm_f32_t,qlstm_f32_t>
ThresholdsActivation<1, 1, Act_N_255, qlstm_int32_t, qlstm_int8_t,-128> th16;
ThresholdsActivation<1, 1, Act_N_255, qlstm_int32_t, qlstm_int8_t,-128> th17;


void main(){
	print("test");
}
