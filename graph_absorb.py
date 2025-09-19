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
from finn.transformation.streamline.reorder import MoveScalarLinearPastInvariants, MoveTransposePastFork
import finn.transformation.streamline.absorb as absorb
from finn.transformation.streamline import RoundAndClipThresholds
import finn.core.onnx_exec as oxe
from finn.transformation.streamline.absorb import (
    Absorb1BitMulIntoConv,
    Absorb1BitMulIntoMatMul,
    AbsorbAddIntoMultiThreshold,
    AbsorbMulIntoMultiThreshold_shashwat,
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
combined_model_path = "models/cnn_lstm_mlp_merged.onnx"
tidy_up_model_path = "models/combined_tidy.onnx"

submodel_name = "combined_submodel"
input_cycle_fraction = 0.5
model_name = f"cnn_lstm_real_c{input_cycle_fraction}"
fmodel_name= f"f{model_name}"
qmodel_name= f"q{model_name}"
qmodel_pth_path = f"./models/{qmodel_name}/final_model.pth"
model_brevitas_path = f"./models/{qmodel_name}/{submodel_name}.onnx"
model_qcdq_path = model_brevitas_path
model_qonnx_path = f"./models/{qmodel_name}/{submodel_name}_qonnx.onnx"
model_finn_path = f"./models/{qmodel_name}/{submodel_name}_finn.onnx"
model_finn_tidy_up_path = f"./models/{qmodel_name}/{submodel_name}_finn_tidy_up.onnx"
model_finn_streamlined_path = f"./models/{qmodel_name}/{submodel_name}_finn_streamlined.onnx"

# --------------------------------------------------------

def finn_tidyup(model_finn, model_finn_tidy_up_path):
    tidy_finn = model_finn.transform(InferShapes())
    tidy_finn = tidy_finn.transform(FoldConstants())
    tidy_finn = tidy_finn.transform(GiveUniqueNodeNames())
    tidy_finn = tidy_finn.transform(GiveReadableTensorNames())
    tidy_finn = tidy_finn.transform(InferDataTypes())
    tidy_finn = tidy_finn.transform(RemoveStaticGraphInputs())
    tidy_finn.save(model_finn_tidy_up_path)
    print("Tidy up complete")
    return tidy_finn


def finn_streamlining(model_finn, model_finn_streamlined_path):

    model_name = f"cnn_lstm_real_c{input_cycle_fraction}"
    fmodel_name= f"f{model_name}"
    qmodel_name= f"q{model_name}"

    streamline_transformations = [
            absorb.AbsorbSignBiasIntoMultiThreshold(),
            MoveMulPastMaxPool(),
            MoveScalarLinearPastInvariants(),
            AbsorbMulIntoMultiThreshold_shashwat(),
            MoveScalarMulPastMatMul(), # attention, fixed name here
            AbsorbMulIntoMultiThreshold_shashwat(),
            MoveScalarMulPastMatMul(), # attention, fixed name here
            CollapseRepeatedMul(),
            # InferShapes(),
            # InferDataTypes(),
            # MoveTransposePastScalarMul(),
            # MoveTransposePastFork(),
            #Streamline(),
            # Streamline(),
            # CollapseRepeatedMul(),
            # AbsorbMulIntoMultiThreshold(),
            # InferDataLayouts(),
            # RemoveUnusedTensors(),
    ]
    i = 0
    # delete debug folder if exists
    if os.path.exists(f"./models/{qmodel_name}/{submodel_name}_debug"):
        import shutil
        shutil.rmtree(f"./models/{qmodel_name}/{submodel_name}_debug")
    for trn in streamline_transformations:
        print('Transformation = ',trn)
        model_finn = model_finn.transform(trn)
        model_finn = model_finn.transform(RemoveIdentityOps())
        model_finn = model_finn.transform(GiveUniqueNodeNames())
        model_finn = model_finn.transform(GiveReadableTensorNames())
        model_finn = model_finn.transform(InferDataTypes())
        # if path does not exist, create it
        if not os.path.exists(f"./models/{qmodel_name}/{submodel_name}_debug/{submodel_name}_finn_streamlined{i}.onnx"):
            os.makedirs(f"./models/{qmodel_name}/{submodel_name}_debug", exist_ok=True)
        model_finn.save(f"./models/{qmodel_name}/{submodel_name}_debug/{submodel_name}_finn_streamlined{i}.onnx")
        i = i+1
    model_finn.save(model_finn_streamlined_path)
    return model_finn

def main():
    print("absorb the ops")
    # load the model
    model = ModelWrapper(combined_model_path)
    tidy_model = finn_tidyup(model, tidy_up_model_path)
    absorb_model = finn_streamlining(tidy_model, model_finn_streamlined_path)
    absorb_model = finn_tidyup(absorb_model, model_finn_streamlined_path)


if __name__ == "__main__":
    main()