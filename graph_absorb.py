import numpy as np
import torch
import os
# --------------------------------------------------------
import onnxruntime as rt
import onnx
from onnx.helper import make_tensor_value_info, make_node, make_graph, make_model, make_tensor
from onnx import numpy_helper
# --------------------------------------------------------
from brevitas.nn import QuantReLU, QuantIdentity
from brevitas.export import export_qonnx
# --------------------------------------------------------
from finn.util.visualization import showInNetron,showSrc
from finn.transformation.streamline import Streamline
from finn.transformation.streamline.reorder import MoveScalarLinearPastInvariants
import finn.transformation.streamline.absorb as absorb
from finn.transformation.streamline import RoundAndClipThresholds
import finn.core.onnx_exec as oxe
from finn.transformation.streamline.absorb import (
    Absorb1BitMulIntoConv,
    Absorb1BitMulIntoMatMul,
    AbsorbAddIntoMultiThreshold,
    AbsorbMulIntoMultiThreshold,
    AbsorbSignBiasIntoMultiThreshold,
    FactorOutMulSignMagnitude,
    AbsorbTransposeIntoMultiThreshold
)
from finn.transformation.streamline.collapse_repeated import (
    CollapseRepeatedAdd,
    CollapseRepeatedMul,
)
from finn.transformation.streamline.reorder import (
    MoveAddPastConv,
    MoveAddPastMul,
    MoveMulPastMaxPool,
    MoveScalarAddPastMatMul,
    MoveScalarLinearPastInvariants,
    MoveScalarMulPastConv,
    MoveScalarMulPastMatMul,
    MoveLinearPastEltwiseAdd,
    MoveLinearPastEltwiseMul,
    MoveTransposePastScalarMul,
    MoveTransposePastJoinAdd
)
from finn.transformation.streamline.round_thresholds import RoundAndClipThresholds
from finn.transformation.streamline.sign_to_thres import ConvertSignToThres
from finn.transformation.qonnx.convert_qonnx_to_finn import ConvertQONNXtoFINN
# --------------------------------------------------------
from qonnx.transformation.general import GiveReadableTensorNames, GiveUniqueNodeNames, RemoveStaticGraphInputs
from qonnx.transformation.infer_shapes import InferShapes
from qonnx.transformation.infer_datatypes import InferDataTypes
from qonnx.transformation.fold_constants import FoldConstants
from qonnx.transformation.base import Transformation
from qonnx.transformation.batchnorm_to_affine import BatchNormToAffine
from qonnx.core.datatype import DataType
from qonnx.transformation.qcdq_to_qonnx import QCDQToQuant
from qonnx.util.basic import qonnx_make_model
from qonnx.transformation.general import (
    ConvertDivToMul,
    ConvertSubToAdd,
    GiveReadableTensorNames,
    GiveUniqueNodeNames,
)
from qonnx.transformation.infer_datatypes import InferDataTypes
from qonnx.transformation.remove import RemoveIdentityOps
from qonnx.core.modelwrapper import ModelWrapper
from qonnx.util.basic import qonnx_make_model
from qonnx.util.cleanup import cleanup as qonnx_cleanup

from qonnx.transformation.change_3d_tensors_to_4d import Change3DTo4DTensors
from qonnx.transformation.infer_data_layouts import InferDataLayouts
from qonnx.transformation.general import RemoveUnusedTensors
# --------------------------------------------------------

def finn_tidyup(model_finn, model_finn_tidy_up_path):
    tidy_finn = model_finn.transform(InferShapes())
    tidy_finn = tidy_finn.transform(FoldConstants())
    tidy_finn = tidy_finn.transform(GiveUniqueNodeNames())
    tidy_finn = tidy_finn.transform(GiveReadableTensorNames())
    tidy_finn = tidy_finn.transform(InferDataTypes())
    tidy_finn = tidy_finn.transform(RemoveStaticGraphInputs())
    tidy_finn.save(model_finn_tidy_up_path)
    return tidy_finn
