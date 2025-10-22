############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
############################################################
open_project clstm2_prj
add_files cnn_lstm_mlp.hpp
add_files cnn_lstm_mlp_weights.hpp
add_files layer0_mt0.cpp
add_files layer1_Im2Col0.cpp
add_files layer2_MVAU0.cpp
add_files layers.h
add_files top.cpp
add_files -tb e2e.cpp
open_solution "solution1" -flow_target vivado
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
#source "./clstm2_prj/solution1/directives.tcl"
csim_design
csynth_design
cosim_design
export_design -format ip_catalog
