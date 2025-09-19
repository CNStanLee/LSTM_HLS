############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
############################################################
open_project cnnlstm
set_top main
add_files cnnlstm/src/top.cpp -cflags "-I/inc"
open_solution "solution1" -flow_target vivado
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 10 -name default
#source "./cnnlstm/solution1/directives.tcl"
#csim_design
csynth_design
#cosim_design
export_design -format ip_catalog
