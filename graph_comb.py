import qonnx
from qonnx.core.modelwrapper import ModelWrapper
from qonnx.transformation.infer_shapes import InferShapes
from qonnx.transformation.fold_constants import FoldConstants
from qonnx.util.basic import qonnx_make_model
import numpy as np
from onnx import helper, numpy_helper, TensorProto
import onnx
from qonnx.transformation.merge_onnx_models import MergeONNXModels

import onnx
from onnx import helper, shape_inference

sub_cnn_onnx_path = "models/subcnn_finn_streamlined.onnx"
sub_lstm_onnx_path = "models/sublstm_finn_streamlined.onnx"
sub_mlp_onnx_path = "models/submlp_finn_streamlined.onnx"

def add_reshape_to_model(model, output_shape):
    """
    Add a Reshape operation to convert output to desired shape
    """
    original_output = model.graph.output[0]
    original_output_name = original_output.name
    
    reshape_output_name = original_output_name + "_reshaped"
    shape_tensor_name = "reshape_shape_const"
    
    shape_values = np.array(output_shape, dtype=np.int64)
    shape_tensor = numpy_helper.from_array(shape_values, name=shape_tensor_name)
    
    reshape_node = helper.make_node(
        'Reshape',
        inputs=[original_output_name, shape_tensor_name],
        outputs=[reshape_output_name],
        name='output_reshape'
    )
    
    model.graph.initializer.append(shape_tensor)
    model.graph.node.append(reshape_node)
    
    new_output = helper.make_tensor_value_info(
        reshape_output_name,
        original_output.type.tensor_type.elem_type,
        output_shape
    )
    
    model.graph.output.remove(original_output)
    model.graph.output.append(new_output)
    
    model = model.transform(InferShapes())
    model = model.transform(FoldConstants())
    
    return model


def main():
    print("Loading models...")
    cnn_model = ModelWrapper(sub_cnn_onnx_path)
    lstm_model = ModelWrapper(sub_lstm_onnx_path)
    mlp_model = ModelWrapper(sub_mlp_onnx_path)
    
    cnn_model = cnn_model.transform(InferShapes())
    lstm_model = lstm_model.transform(InferShapes())
    mlp_model = mlp_model.transform(InferShapes())

    output_shape = [64, 1]  # Target shape with batch dimension
    cnn_model = add_reshape_to_model(cnn_model, output_shape)
    cnn_model = cnn_model.transform(InferShapes())
    cnn_output_path = "models/subcnn_finn_streamlined_reshaped.onnx"
    cnn_model.save(cnn_output_path)
    print(f"Modified CNN model saved to: {cnn_output_path}")
    print(f"New CNN output shape: {cnn_model.graph.output[0].type.tensor_type.shape}")


    model_path = "models/sublstm_finn_streamlined.onnx"
    model = onnx.load(model_path)

    inputs = model.graph.input
    input_names = [input.name for input in inputs]
    print(f"Original input order: {input_names}")

    input_to_move = None
    other_inputs = []
    for input in inputs:
        if input.name == "global_in_2":
            input_to_move = input
        else:
            other_inputs.append(input)

    new_inputs = [input_to_move] + other_inputs

    model.graph.ClearField("input")
    model.graph.input.extend(new_inputs)

    for node in model.graph.node:
        for i, input_name in enumerate(node.input):
            if input_name == "global_in_2":
                pass


    new_model_path = "models/lstm_reordered.onnx"
    onnx.save(model, new_model_path)
    print(f"Model with reordered inputs saved to: {new_model_path}")

    reorder_lstm_model = ModelWrapper("models/lstm_reordered.onnx")

    merged_model = reorder_lstm_model.transform(MergeONNXModels(cnn_model))
    merged_model = merged_model.transform(InferShapes())
    print(f"Merged model input shape: {merged_model.graph.input[0].type.tensor_type.shape}")
    print(f"Merged model output shape: {merged_model.graph.output[0].type.tensor_type.shape}")
    merged_model.save("models/cnn_lstm_merged.onnx")

    output_shape = [1, 128]  # Target shape with batch dimension

    merged_model = add_reshape_to_model(merged_model, output_shape)
    merged_model = merged_model.transform(InferShapes())


    merged_model2 = mlp_model.transform(MergeONNXModels(merged_model))
    merged_model2 = merged_model2.transform(InferShapes())
    print(f"Final merged model input shape: {merged_model2.graph.input[0].type.tensor_type.shape}")
    print(f"Final merged model output shape: {merged_model2.graph.output[0].type.tensor_type.shape}")
    merged_model2.save("models/cnn_lstm_mlp_merged.onnx")


if __name__ == "__main__":
    main()