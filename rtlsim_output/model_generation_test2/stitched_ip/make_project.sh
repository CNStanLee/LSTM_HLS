#!/bin/bash 
cd /tmp/finn_dev_root/vivado_stitch_proj_65wkfbtk
vivado -mode batch -source make_project.tcl
cd /home/changhong/prj/finn_dev/finn/script/LSTM_HLS
