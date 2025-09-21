############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
############################################################
open_project cnnlstm
set_top main
add_files cnnlstm/src/convlayer.h
add_files cnnlstm/src/g_config.h
add_files cnnlstm/src/global_nn_def.h
add_files cnnlstm/src/n_cnn.hpp
add_files cnnlstm/src/n_cnn_weights.hpp
add_files cnnlstm/src/test.h
add_files cnnlstm/src/tmrcheck.hpp
add_files cnnlstm/src/top.cpp
add_files -tb cnnlstm/src/test_tb.cpp
open_solution "solution1" -flow_target vivado
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
#source "./cnnlstm/solution1/directives.tcl"
csim_design
csynth_design
cosim_design
export_design -format ip_catalog
