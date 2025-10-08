############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
############################################################
open_project cnn_lstm3
set_top forward
add_files top.cpp
add_files -tb cnn_tb.cpp
open_solution "solution1" -flow_target vivado
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
#source "./cnn_lstm3/solution1/directives.tcl"
csim_design
csynth_design
cosim_design
export_design -format ip_catalog
