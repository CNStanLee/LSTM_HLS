import finn.builder.build_dataflow as build
import finn.builder.build_dataflow_config as build_cfg
import os
import shutil
import os

import torch
from torch.nn import BatchNorm1d
from torch.nn import BatchNorm2d
from torch.nn import MaxPool2d, AvgPool2d
from torch.nn import Module
from torch.nn import ModuleList

from brevitas.core.restrict_val import RestrictValueType
from brevitas.nn import QuantConv2d
from brevitas.nn import QuantIdentity
from brevitas.nn import QuantLinear

from brevitas_examples.bnn_pynq.models.common import CommonActQuant
from brevitas_examples.bnn_pynq.models.common import CommonWeightQuant
from brevitas_examples.bnn_pynq.models.tensor_norm import TensorNorm
from finn.transformation.qonnx.convert_qonnx_to_finn import ConvertQONNXtoFINN
from qonnx.transformation.infer_shapes import InferShapes
from qonnx.transformation.fold_constants import FoldConstants
from qonnx.transformation.general import GiveReadableTensorNames, GiveUniqueNodeNames, RemoveStaticGraphInputs
from finn.util.basic import make_build_dir
from finn.util.visualization import showInNetron
import os
import configparser
import brevitas.nn as qnn
from brevitas.core.quant import QuantType
from brevitas.core.restrict_val import RestrictValueType
from brevitas.core.scaling import ScalingImplType
import numpy as np
from brevitas.nn import QuantIdentity
from copy import deepcopy



if __name__ == "__main__":
    pynq_part_map = dict()
    pynq_part_map["Ultra96"] = "xczu3eg-sbva484-1-e"
    pynq_part_map["Ultra96-V2"] = "xczu3eg-sbva484-1-i"
    pynq_part_map["Pynq-Z1"] = "xc7z020clg400-1"
    pynq_part_map["Pynq-Z2"] = "xc7z020clg400-1"
    pynq_part_map["ZCU102"] = "xczu9eg-ffvb1156-2-e"
    pynq_part_map["ZCU104"] = "xczu7ev-ffvc1156-2-e"
    pynq_part_map["ZCU111"] = "xczu28dr-ffvg1517-2-e"
    pynq_part_map["RFSoC2x2"] = "xczu28dr-ffvg1517-2-e"
    pynq_part_map["RFSoC4x2"] = "xczu48dr-ffvg1517-2-e"
    pynq_part_map["KV260_SOM"] = "xck26-sfvc784-2LV-c"
    pynq_part_map["U50"] = "xcu50-fsvh2104-2L-e"
    ready_model_filename = "models/subcnn_finn_streamlined.onnx"
    rtlsim_output_dir = "rtlsim_output/model_generation_test"
    specialize_layers_config_file = 'models/cnn_sp_layers.json'
    cfg_stitched_ip = build.DataflowBuildConfig(
        output_dir          = rtlsim_output_dir,
        mvau_wwidth_max     = 80,
        target_fps          = 1000000,
        synth_clk_period_ns = 10.0,    
        fpga_part           = pynq_part_map["ZCU104"],
        specialize_layers_config_file = specialize_layers_config_file,
        generate_outputs=[
            build_cfg.DataflowOutputType.STITCHED_IP,
            build_cfg.DataflowOutputType.RTLSIM_PERFORMANCE,
            build_cfg.DataflowOutputType.OOC_SYNTH,
        ]
    )

    build.build_dataflow_cfg(ready_model_filename, cfg_stitched_ip)
