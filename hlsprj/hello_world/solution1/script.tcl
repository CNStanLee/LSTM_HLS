############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
############################################################
open_project hello_world
set_top hello
add_files cnn_instance.hpp
add_files convlayer.h
add_files ../hello_top.cpp
add_files nn_config.h
add_files -tb ../hello_tb.cpp
open_solution "solution1" -flow_target vivado
set_part {xcvu11p-flga2577-1-e}
create_clock -period 10 -name default
#source "./hello_world/solution1/directives.tcl"
csim_design
csynth_design
cosim_design
export_design -format ip_catalog
