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
    # Get original output information
    original_output = model.graph.output[0]
    original_output_name = original_output.name
    
    # Create new names for intermediate tensors
    reshape_output_name = original_output_name + "_reshaped"
    shape_tensor_name = "reshape_shape_const"
    
    # Create constant tensor for target shape
    shape_values = np.array(output_shape, dtype=np.int64)
    shape_tensor = numpy_helper.from_array(shape_values, name=shape_tensor_name)
    
    # Create Reshape node
    reshape_node = helper.make_node(
        'Reshape',
        inputs=[original_output_name, shape_tensor_name],
        outputs=[reshape_output_name],
        name='output_reshape'
    )
    
    # Add constant tensor to model initializers
    model.graph.initializer.append(shape_tensor)
    
    # Add Reshape node to graph
    model.graph.node.append(reshape_node)
    
    # Create new output value info with correct shape
    new_output = helper.make_tensor_value_info(
        reshape_output_name,
        original_output.type.tensor_type.elem_type,
        output_shape
    )
    
    # Remove old output and add new one
    model.graph.output.remove(original_output)
    model.graph.output.append(new_output)
    
    # Apply shape inference and constant folding
    model = model.transform(InferShapes())
    model = model.transform(FoldConstants())
    
    return model

def combine_models(cnn_model, lstm_model, mlp_model):
    """
    Combine the three sub-models into a single model
    """
    # Create a new graph that will contain all nodes from the three models
    combined_graph = helper.make_graph(
        nodes=[],
        name="combined_model",
        inputs=[],
        outputs=[],
        initializer=[]
    )
    
    # Add all nodes and initializers from each model
    for model in [cnn_model, lstm_model, mlp_model]:
        combined_graph.node.extend(model.graph.node)
        combined_graph.initializer.extend(model.graph.initializer)
    
    # Set the input of the combined model to be the input of the CNN
    combined_graph.input.append(cnn_model.graph.input[0])
    
    # Set the output of the combined model to be the output of the MLP
    combined_graph.output.append(mlp_model.graph.output[0])
    
    # Create the combined model
    combined_model = qonnx_make_model(
        combined_graph,
        producer_name="qonnx",
        doc_string="Combined CNN-LSTM-MLP model"
    )
    
    # Apply shape inference to the combined model
    combined_model = ModelWrapper(combined_model)
    combined_model = combined_model.transform(InferShapes())
    
    return combined_model

def main():
    print("Loading models...")
    cnn_model = ModelWrapper(sub_cnn_onnx_path)
    lstm_model = ModelWrapper(sub_lstm_onnx_path)
    mlp_model = ModelWrapper(sub_mlp_onnx_path)
    
    # Add Reshape operation to convert from 1x64x1x1 to 1x64x1
    print("Adding reshape operation to CNN model...")

    cnn_model = cnn_model.transform(InferShapes())
    lstm_model = lstm_model.transform(InferShapes())
    mlp_model = mlp_model.transform(InferShapes())

    output_shape = [64, 1]  # Target shape with batch dimension
    
    cnn_model = add_reshape_to_model(cnn_model, output_shape)
    cnn_model = cnn_model.transform(InferShapes())
    # Save modified CNN model
    cnn_output_path = "models/subcnn_finn_streamlined_reshaped.onnx"
    cnn_model.save(cnn_output_path)
    print(f"Modified CNN model saved to: {cnn_output_path}")
    
    # Verify the CNN output shape
    print(f"New CNN output shape: {cnn_model.graph.output[0].type.tensor_type.shape}")


    # change the input order of the LSTM model and make 64x1 as the first dimension
    print("Merging CNN and LSTM models...")



    model_path = "models/sublstm_finn_streamlined.onnx"
    model = onnx.load(model_path)

    # 获取当前输入信息
    inputs = model.graph.input
    input_names = [input.name for input in inputs]
    print(f"Original input order: {input_names}")

    # 找到要调整的输入
    input_to_move = None
    other_inputs = []
    for input in inputs:
        if input.name == "global_in_2":
            input_to_move = input
        else:
            other_inputs.append(input)

    # 重新排列输入顺序
    new_inputs = [input_to_move] + other_inputs

    # 更新模型图
    model.graph.ClearField("input")
    model.graph.input.extend(new_inputs)

    # 更新节点输入引用（如果需要）
    for node in model.graph.node:
        for i, input_name in enumerate(node.input):
            if input_name == "global_in_2":
                # 可能需要更新节点输入引用
                pass

    # 运行形状推断以确保模型有效
    #model = shape_inference.infer_shapes(model)

    # 保存修改后的模型
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
    # # Combine all models
    # print("Combining models...")
    # combined_model = combine_models(cnn_model, lstm_model, mlp_model)
    
    # # Apply shape inference to the combined model
    # print("Applying shape inference to combined model...")
    # combined_model = combined_model.transform(InferShapes())
    
    # # Save the combined model
    # combined_output_path = "models/combined_model.onnx"
    # combined_model.save(combined_output_path)
    # print(f"Combined model saved to: {combined_output_path}")
    
    # # Print input and output shapes of the combined model
    # print(f"Combined model input shape: {combined_model.graph.input[0].type.tensor_type.shape}")
    # print(f"Combined model output shape: {combined_model.graph.output[0].type.tensor_type.shape}")
    
    # print("All done!")

if __name__ == "__main__":
    main()