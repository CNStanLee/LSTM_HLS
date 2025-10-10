############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
############################################################
open_project clstm
set_top top
add_files src/weights.hpp
add_files src/utils.hpp
add_files src/top.cpp
add_files src/tmrcheck.hpp
add_files src/streamtools.h
add_files src/slidingwindow.h
add_files src/mvau.hpp
add_files src/mmv.hpp
add_files src/maxpool.h
add_files src/mac.hpp
add_files src/interpret.hpp
add_files src/eltwise.hpp
add_files src/custom_types.h
add_files src/convlayer.h
add_files src/cnn_lstm_mlp_weights.hpp
add_files src/cnn_lstm_mlp.hpp
add_files src/cnn_lstm_mlp.h
add_files src/activations.hpp
add_files -tb src/top_tb.cpp -cflags "-Wno-unknown-pragmas -Wno-unknown-pragmas -Wno-unknown-pragmas" -csimflags "-Wno-unknown-pragmas"
open_solution "clstm" -flow_target vivado
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
source "./clstm/clstm/directives.tcl"
csim_design
csynth_design
cosim_design
export_design -format ip_catalog
