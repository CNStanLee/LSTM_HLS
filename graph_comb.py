import qonnx
from qonnx.core.modelwrapper import ModelWrapper
from qonnx.transformation.infer_shapes import InferShapes
from qonnx.transformation.fold_constants import FoldConstants
from qonnx.util.basic import qonnx_make_model
import numpy as np
from onnx import helper, numpy_helper, TensorProto
import onnx
from qonnx.transformation.merge_onnx_models import MergeONNXModels
from onnxruntime.transformers.fusion_utils import FusionUtils
import onnx
from onnx import helper, shape_inference

sub_cnn_onnx_path = "models/subcnn_finn_streamlined.onnx"
sub_lstm_onnx_path = "models/sublstm_finn_streamlined.onnx"
sub_mlp_onnx_path = "models/submlp_finn_streamlined.onnx"

# def add_reshape_to_model(model, output_shape):
#     """
#     Add a Reshape operation to convert output to desired shape
#     """
#     original_output = model.graph.output[0]
#     original_output_name = original_output.name
    
#     reshape_output_name = original_output_name + "_reshaped"
#     shape_tensor_name = "reshape_shape_const"
    
#     shape_values = np.array(output_shape, dtype=np.int64)
#     shape_tensor = numpy_helper.from_array(shape_values, name=shape_tensor_name)
    
#     reshape_node = helper.make_node(
#         'Reshape',
#         inputs=[original_output_name, shape_tensor_name],
#         outputs=[reshape_output_name],
#         name='output_reshape'
#     )
    
#     model.graph.initializer.append(shape_tensor)
#     model.graph.node.append(reshape_node)
    
#     new_output = helper.make_tensor_value_info(
#         reshape_output_name,
#         original_output.type.tensor_type.elem_type,
#         output_shape
#     )
    
#     model.graph.output.remove(original_output)
#     model.graph.output.append(new_output)
    
#     model = model.transform(InferShapes())
#     model = model.transform(FoldConstants())
    
#     return model
def add_reshape_to_model(model, output_shape):
    """
    Add a Reshape, Transpose or Gather+Reshape operation to convert output to desired shape
    """
    original_output = model.graph.output[0]
    original_output_name = original_output.name
    
    # Get original output shape
    original_shape = []
    for dim in original_output.type.tensor_type.shape.dim:
        if dim.dim_value > 0:
            original_shape.append(dim.dim_value)
        else:
            # Handle dynamic dimensions (if any)
            original_shape.append(None)
    
    print(f"Original shape: {original_shape}, Target shape: {output_shape}")
    
    # Calculate total elements
    original_elements = np.prod([s for s in original_shape if s is not None])
    target_elements = np.prod([s for s in output_shape if s is not None])
    
    # Case 1: Element count matches - use Reshape or Transpose
    if original_elements == target_elements:
        # Check if the transformation is a transpose case (e.g., 64x1 -> 1x64)
        if (len(original_shape) == 2 and len(output_shape) == 2 and
            original_shape[0] == output_shape[1] and 
            original_shape[1] == output_shape[0]):
            # Use Transpose instead of Reshape
            transpose_output_name = original_output_name + "_transposed"
            
            transpose_node = helper.make_node(
                'Transpose',
                inputs=[original_output_name],
                outputs=[transpose_output_name],
                perm=[1, 0],  # Swap the two dimensions
                name='output_transpose'
            )
            
            model.graph.node.append(transpose_node)
            
            new_output = helper.make_tensor_value_info(
                transpose_output_name,
                original_output.type.tensor_type.elem_type,
                output_shape
            )
        else:
            # Use Reshape for all other cases with matching element count
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
    
    # Case 2: Element count doesn't match - use Gather + Reshape
    else:
        # For your specific case: [1,14,64,1] -> [1,64]
        # We use Gather to select the first element along dimension 1 (the 14 dimension)
        gather_output_name = original_output_name + "_gathered"
        
        # Create constant tensor for indices [0]
        indices_name = "gather_indices"
        indices_tensor = numpy_helper.from_array(np.array([0], dtype=np.int64), name=indices_name)
        
        # Create Gather node
        gather_node = helper.make_node(
            'Gather',
            inputs=[original_output_name, indices_name],
            outputs=[gather_output_name],
            axis=1,  # Gather along the second dimension (size 14)
            name='output_gather'
        )
        
        # Add Gather node and indices tensor to the model
        model.graph.node.append(gather_node)
        model.graph.initializer.append(indices_tensor)
        
        # After Gather: [1,14,64,1] -> [1,1,64,1]
        # Now reshape to final output shape
        reshape_output_name = gather_output_name + "_reshaped"
        shape_tensor_name = "reshape_shape_const"
        
        shape_values = np.array(output_shape, dtype=np.int64)
        shape_tensor = numpy_helper.from_array(shape_values, name=shape_tensor_name)
        
        reshape_node = helper.make_node(
            'Reshape',
            inputs=[gather_output_name, shape_tensor_name],
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
    
    # Update model output
    model.graph.output.remove(original_output)
    model.graph.output.append(new_output)
    
    # Run shape inference and constant folding
    try:
        model = shape_inference.infer_shapes(model)
        print("Shape inference successful")
    except Exception as e:
        print(f"Warning: Shape inference failed: {e}")
        
    try:
        model = FusionUtils.fold_constants(model)
        print("Constant folding successful")
    except Exception as e:
        print(f"Warning: Constant folding failed: {e}")
    
    return model
# backup version
# def add_reshape_to_model(model, output_shape):
#     """
#     Add a Reshape or Transpose operation to convert output to desired shape
#     """
#     original_output = model.graph.output[0]
#     original_output_name = original_output.name
    
#     # Get original output shape
#     original_shape = []
#     for dim in original_output.type.tensor_type.shape.dim:
#         if dim.dim_value > 0:
#             original_shape.append(dim.dim_value)
#         else:
#             # Handle dynamic dimensions (if any)
#             original_shape.append(None)
    
#     # Check if the transformation is a transpose case (e.g., 64x1 -> 1x64)
#     if (len(original_shape) == 2 and len(output_shape) == 2 and
#         original_shape[0] == output_shape[1] and 
#         original_shape[1] == output_shape[0]):
#         # Use Transpose instead of Reshape
#         transpose_output_name = original_output_name + "_transposed"
        
#         transpose_node = helper.make_node(
#             'Transpose',
#             inputs=[original_output_name],
#             outputs=[transpose_output_name],
#             perm=[1, 0],  # Swap the two dimensions
#             name='output_transpose'
#         )
        
#         model.graph.node.append(transpose_node)
        
#         new_output = helper.make_tensor_value_info(
#             transpose_output_name,
#             original_output.type.tensor_type.elem_type,
#             output_shape
#         )
#     else:
#         # Use Reshape for all other cases
#         reshape_output_name = original_output_name + "_reshaped"
#         shape_tensor_name = "reshape_shape_const"
        
#         shape_values = np.array(output_shape, dtype=np.int64)
#         shape_tensor = numpy_helper.from_array(shape_values, name=shape_tensor_name)
        
#         reshape_node = helper.make_node(
#             'Reshape',
#             inputs=[original_output_name, shape_tensor_name],
#             outputs=[reshape_output_name],
#             name='output_reshape'
#         )
        
#         model.graph.initializer.append(shape_tensor)
#         model.graph.node.append(reshape_node)
        
#         new_output = helper.make_tensor_value_info(
#             reshape_output_name,
#             original_output.type.tensor_type.elem_type,
#             output_shape
#         )
    
#     model.graph.output.remove(original_output)
#     model.graph.output.append(new_output)
    
#     model = model.transform(InferShapes())
#     model = model.transform(FoldConstants())
    
#     return model

# def rename_io_by_node(model, node_name, io_num, new_name, io_type, shape):
#     """
#     通过节点名称和输入/输出索引来重命名并设置全局输入/输出
    
#     参数:
#         model: ModelWrapper 模型对象
#         node_name: str 节点名称
#         io_num: int 输入/输出索引（从0开始）
#         new_name: str 新名称
#         io_type: str 类型，可以是 "input" 或 "output"
#         shape: list 形状，例如 [1, 128]
    
#     返回:
#         ModelWrapper: 修改后的模型
#     """
#     # 确保模型是 ModelWrapper 类型
#     if not isinstance(model, ModelWrapper):
#         model = ModelWrapper(model)
    
#     # 查找指定节点
#     target_node = None
#     for node in model.graph.node:
#         if node.name == node_name:
#             target_node = node
#             break
    
#     if target_node is None:
#         raise ValueError(f"未找到名称为 '{node_name}' 的节点")
    
#     # 根据类型获取原始名称
#     if io_type == "input":
#         if io_num >= len(target_node.input):
#             raise ValueError(f"节点 '{node_name}' 只有 {len(target_node.input)} 个输入，无法访问索引 {io_num}")
#         ori_name = target_node.input[io_num]
#     elif io_type == "output":
#         if io_num >= len(target_node.output):
#             raise ValueError(f"节点 '{node_name}' 只有 {len(target_node.output)} 个输出，无法访问索引 {io_num}")
#         ori_name = target_node.output[io_num]
#     else:
#         raise ValueError("io_type 必须是 'input' 或 'output'")
    
#     print(f"找到目标: 节点 '{node_name}' 的 {io_type}[{io_num}] = '{ori_name}'")
    
#     # 重命名所有引用
#     if io_type == "input":
#         # 更新所有使用该名称的节点输入
#         for node in model.graph.node:
#             for i, input_name in enumerate(node.input):
#                 if input_name == ori_name:
#                     node.input[i] = new_name
        
#         # 检查是否已经是全局输入
#         existing_inputs = [inp.name for inp in model.graph.input]
#         if ori_name in existing_inputs:
#             # 更新现有输入
#             for inp in model.graph.input:
#                 if inp.name == ori_name:
#                     inp.name = new_name
#                     # 更新形状
#                     while len(inp.type.tensor_type.shape.dim) < len(shape):
#                         inp.type.tensor_type.shape.dim.add()
#                     for i, dim_value in enumerate(shape):
#                         inp.type.tensor_type.shape.dim[i].dim_value = dim_value
#                     break
#         else:
#             # 创建新的全局输入
#             # 尝试从 value_info 获取数据类型，否则使用默认的 FLOAT
#             elem_type = onnx.TensorProto.FLOAT
#             for value_info in model.graph.value_info:
#                 if value_info.name == ori_name:
#                     elem_type = value_info.type.tensor_type.elem_type
#                     break
            
#             new_input = helper.make_tensor_value_info(
#                 new_name,
#                 elem_type,
#                 shape
#             )
#             model.graph.input.append(new_input)
    
#     elif io_type == "output":
#         # 更新所有产生该名称的节点输出
#         for node in model.graph.node:
#             for i, output_name in enumerate(node.output):
#                 if output_name == ori_name:
#                     node.output[i] = new_name
        
#         # 检查是否已经是全局输出
#         existing_outputs = [out.name for out in model.graph.output]
#         if ori_name in existing_outputs:
#             # 更新现有输出
#             for out in model.graph.output:
#                 if out.name == ori_name:
#                     out.name = new_name
#                     # 更新形状
#                     while len(out.type.tensor_type.shape.dim) < len(shape):
#                         out.type.tensor_type.shape.dim.add()
#                     for i, dim_value in enumerate(shape):
#                         out.type.tensor_type.shape.dim[i].dim_value = dim_value
#                     break
#         else:
#             # 创建新的全局输出
#             # 尝试从 value_info 获取数据类型，否则使用默认的 FLOAT
#             elem_type = onnx.TensorProto.FLOAT
#             for value_info in model.graph.value_info:
#                 if value_info.name == ori_name:
#                     elem_type = value_info.type.tensor_type.elem_type
#                     break
            
#             new_output = helper.make_tensor_value_info(
#                 new_name,
#                 elem_type,
#                 shape
#             )
#             model.graph.output.append(new_output)
    
#     # 更新 value_info 中的名称（如果有）
#     for value_info in model.graph.value_info:
#         if value_info.name == ori_name:
#             value_info.name = new_name
#             # 更新形状
#             while len(value_info.type.tensor_type.shape.dim) < len(shape):
#                 value_info.type.tensor_type.shape.dim.add()
#             for i, dim_value in enumerate(shape):
#                 value_info.type.tensor_type.shape.dim[i].dim_value = dim_value
#             break
    
#     # 重新推断形状
#     model = model.transform(InferShapes())
    
#     print(f"成功将 '{ori_name}' 重命名为 '{new_name}' 并设置为全局{io_type}")
    
#     return model

def rename_io_by_node(model, node_name, io_num, new_name, io_type, shape):
    """
    通过节点名称和输入/输出索引来重命名并设置全局输入/输出
    
    参数:
        model: ModelWrapper 模型对象
        node_name: str 节点名称
        io_num: int 输入/输出索引（从0开始）
        new_name: str 新名称
        io_type: str 类型，可以是 "input" 或 "output"
        shape: list 形状，例如 [1, 128]
    
    返回:
        ModelWrapper: 修改后的模型
    """
    # 确保模型是 ModelWrapper 类型
    if not isinstance(model, ModelWrapper):
        model = ModelWrapper(model)
    
    # 查找指定节点
    target_node = None
    for node in model.graph.node:
        if node.name == node_name:
            target_node = node
            break
    
    if target_node is None:
        raise ValueError(f"未找到名称为 '{node_name}' 的节点")
    
    # 根据类型获取原始名称
    if io_type == "input":
        if io_num >= len(target_node.input):
            raise ValueError(f"节点 '{node_name}' 只有 {len(target_node.input)} 个输入，无法访问索引 {io_num}")
        ori_name = target_node.input[io_num]
    elif io_type == "output":
        if io_num >= len(target_node.output):
            raise ValueError(f"节点 '{node_name}' 只有 {len(target_node.output)} 个输出，无法访问索引 {io_num}")
        ori_name = target_node.output[io_num]
    else:
        raise ValueError("io_type 必须是 'input' 或 'output'")
    
    print(f"找到目标: 节点 '{node_name}' 的 {io_type}[{io_num}] = '{ori_name}'")
    
    # 检查新名称是否已经存在
    if io_type == "input":
        existing_names = [inp.name for inp in model.graph.input]
    else:
        existing_names = [out.name for out in model.graph.output]
    
    if new_name in existing_names:
        # 如果新名称已经存在，添加后缀使其唯一
        counter = 1
        while f"{new_name}_{counter}" in existing_names:
            counter += 1
        new_name = f"{new_name}_{counter}"
        print(f"警告: 名称已存在，使用 '{new_name}' 替代")
    
    # 重命名所有引用
    if io_type == "input":
        # 更新所有使用该名称的节点输入
        for node in model.graph.node:
            for i, input_name in enumerate(node.input):
                if input_name == ori_name:
                    node.input[i] = new_name
        
        # 检查是否已经是全局输入
        existing_inputs = {inp.name: inp for inp in model.graph.input}
        if ori_name in existing_inputs:
            # 更新现有输入
            inp = existing_inputs[ori_name]
            inp.name = new_name
            # 更新形状
            while len(inp.type.tensor_type.shape.dim) < len(shape):
                inp.type.tensor_type.shape.dim.add()
            for i, dim_value in enumerate(shape):
                inp.type.tensor_type.shape.dim[i].dim_value = dim_value
        else:
            # 创建新的全局输入
            # 尝试从 value_info 获取数据类型，否则使用默认的 FLOAT
            elem_type = onnx.TensorProto.FLOAT
            for value_info in model.graph.value_info:
                if value_info.name == ori_name:
                    elem_type = value_info.type.tensor_type.elem_type
                    break
            
            new_input = helper.make_tensor_value_info(
                new_name,
                elem_type,
                shape
            )
            model.graph.input.append(new_input)
    
    elif io_type == "output":
        # 更新所有产生该名称的节点输出
        for node in model.graph.node:
            for i, output_name in enumerate(node.output):
                if output_name == ori_name:
                    node.output[i] = new_name
        
        # 检查是否已经是全局输出
        existing_outputs = {out.name: out for out in model.graph.output}
        if ori_name in existing_outputs:
            # 更新现有输出
            out = existing_outputs[ori_name]
            out.name = new_name
            # 更新形状
            while len(out.type.tensor_type.shape.dim) < len(shape):
                out.type.tensor_type.shape.dim.add()
            for i, dim_value in enumerate(shape):
                out.type.tensor_type.shape.dim[i].dim_value = dim_value
        else:
            # 创建新的全局输出
            # 尝试从 value_info 获取数据类型，否则使用默认的 FLOAT
            elem_type = onnx.TensorProto.FLOAT
            for value_info in model.graph.value_info:
                if value_info.name == ori_name:
                    elem_type = value_info.type.tensor_type.elem_type
                    break
            
            new_output = helper.make_tensor_value_info(
                new_name,
                elem_type,
                shape
            )
            model.graph.output.append(new_output)
    
    # 更新 value_info 中的名称（如果有）
    # 先收集所有需要更新的 value_info
    value_infos_to_update = []
    for value_info in model.graph.value_info:
        if value_info.name == ori_name:
            value_infos_to_update.append(value_info)
    
    # 只更新第一个匹配的 value_info，删除其他的
    if value_infos_to_update:
        # 更新第一个
        value_infos_to_update[0].name = new_name
        # 更新形状
        while len(value_infos_to_update[0].type.tensor_type.shape.dim) < len(shape):
            value_infos_to_update[0].type.tensor_type.shape.dim.add()
        for i, dim_value in enumerate(shape):
            value_infos_to_update[0].type.tensor_type.shape.dim[i].dim_value = dim_value
        
        # 删除其他的重复项
        if len(value_infos_to_update) > 1:
            for dup_value_info in value_infos_to_update[1:]:
                model.graph.value_info.remove(dup_value_info)
            print(f"警告: 删除了 {len(value_infos_to_update)-1} 个重复的 value_info")
    
    # 重新推断形状
    try:
        model = model.transform(InferShapes())
    except Exception as e:
        print(f"形状推断时出错: {e}")
        # 尝试手动清理重复的 value_info
        seen_names = set()
        unique_value_infos = []
        for vi in model.graph.value_info:
            if vi.name not in seen_names:
                unique_value_infos.append(vi)
                seen_names.add(vi.name)
        
        model.graph.ClearField("value_info")
        model.graph.value_info.extend(unique_value_infos)
        
        # 再次尝试形状推断
        model = model.transform(InferShapes())
    
    print(f"成功将 '{ori_name}' 重命名为 '{new_name}' 并设置为全局{io_type}")
    
    return model

def main():
    print("Loading models...")
    cnn_model = ModelWrapper(sub_cnn_onnx_path)
    lstm_model = ModelWrapper(sub_lstm_onnx_path)
    mlp_model = ModelWrapper(sub_mlp_onnx_path)
    
    cnn_model = cnn_model.transform(InferShapes())
    lstm_model = lstm_model.transform(InferShapes())
    mlp_model = mlp_model.transform(InferShapes())




    output_shape = [1, 64]  # Target shape with batch dimension
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

    merged_model = merged_model.transform(InferShapes())


    merged_model2 = mlp_model.transform(MergeONNXModels(merged_model))
    merged_model2 = merged_model2.transform(InferShapes())
    print(f"Final merged model input shape: {merged_model2.graph.input[0].type.tensor_type.shape}")
    print(f"Final merged model output shape: {merged_model2.graph.output[0].type.tensor_type.shape}")
    merged_model2.save("models/cnn_lstm_mlp_merged.onnx")


    # fix the input and output after merging
    merged_model2 = rename_io_by_node(merged_model2, 'MultiThreshold_1', 0, 'h_t_1', 'input', [1, 128])
    merged_model2 = rename_io_by_node(merged_model2, 'MultiThreshold_2', 0, 'c_t_1', 'input', [1, 128])
    #merged_model2 = rename_io_by_node(merged_model2, 'Mul_4', 0, 'Mul_4_out0_new', 'output', [1, 128])
    

    c_t_tensor = helper.make_tensor_value_info(
    name="c_t",  
    elem_type=TensorProto.FLOAT, 
    shape=[1, 128]  
)
    identity_node_ct = helper.make_node(
    "Identity",
    inputs=["Mul_4_out0"],  
    outputs=["c_t"],  
    name="c_t_identity"
)
    merged_model2.graph.node.append(identity_node_ct)
    merged_model2.graph.output.append(c_t_tensor)

    h_t_tensor = helper.make_tensor_value_info(
    name="h_t",  
    elem_type=TensorProto.FLOAT, 
    shape=[1, 128]  
)
    identity_node_ht = helper.make_node(
    "Identity",
    inputs=["Mul_7_out0"],  
    outputs=["h_t"],  
    name="h_t_identity"
)
    merged_model2.graph.node.append(identity_node_ht)
    merged_model2.graph.output.append(h_t_tensor)

    merged_model2.save("models/cnn_lstm_mlp_merged.onnx")
if __name__ == "__main__":
    main()