// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.2 (64-bit)
// Tool Version Limit: 2019.12
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
# 1 "/home/changhong/prj/finn/script/LSTM_HLS/hello_top.cpp"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "/home/changhong/prj/finn/script/LSTM_HLS/hello_top.cpp"

int hello(){
 return 1;
}
#ifndef HLS_FASTSIM
#ifdef __cplusplus
extern "C"
#endif
int apatb_hello_ir();
#ifdef __cplusplus
extern "C"
#endif
int hello_hw_stub(){
int _ret = hello();
return _ret;
}
#ifdef __cplusplus
extern "C"
#endif
int apatb_hello_sw(){
int _ret = apatb_hello_ir();
return _ret;
}
#endif
# 4 "/home/changhong/prj/finn/script/LSTM_HLS/hello_top.cpp"

