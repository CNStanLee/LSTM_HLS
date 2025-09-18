import numpy as np
import finn.core.onnx_exec as oxe
from qonnx.core.modelwrapper import ModelWrapper
import onnx
from onnx import helper, numpy_helper
def check_missing_shapes(model_path):
    model = onnx.load(model_path)
    graph = model.graph

    missing_shapes = []
    for vi in list(graph.input) + list(graph.value_info) + list(graph.output):
        t = vi.type.tensor_type
        if not t.HasField("shape") or len(t.shape.dim) == 0:
            missing_shapes.append(vi.name)

    return missing_shapes


# --------------------------------------------------------
model_path = f"models/qcnn_lstm_real_c0.5/combined_submodel_finn_streamlined.onnx"
fix_model_path = "models/fixed.onnx"
hidden_size = 128
batch_size = 1
# --------------------------------------------------------
input_cycle_fraction = 0.5
model_name = f"cnn_lstm_real_c{input_cycle_fraction}"
fmodel_name= f"f{model_name}"
qmodel_name= f"q{model_name}"
input_size = int(input_cycle_fraction * 64)
cnn_input_size = input_size
qlstm_input_size = input_size * 2
submodel_input_size = cnn_input_size
x = np.random.randn(submodel_input_size,1).astype(np.float32).reshape([submodel_input_size,1])
print(x.shape)
x = np.expand_dims(x, axis=1) # shape to (batch, channel, feature)
print(x.shape)
h0 = np.zeros((hidden_size, batch_size), dtype=np.float32)
c0 = np.zeros((hidden_size, batch_size), dtype=np.float32)

input_dict = {}
input_dict["X"] = x
input_dict["h_t-1"] = h0
input_dict["c_t-1"] = c0
input_dict["global_in"] = x.transpose(1,2,0)


def streamline_model_behavior_test(streamlined_model):
    input_dict["global_in"] = np.expand_dims(input_dict["global_in"], axis=-1)   # add batch dim
    output_dict_streamlined = oxe.execute_onnx(streamlined_model, input_dict,return_full_exec_context=True)
    streamlined_output = np.array(output_dict_streamlined.get("global_out")) 
    print("Streamlined output shape:", streamlined_output.shape)
    return streamlined_output


def main():
    missing = check_missing_shapes(model_path)
    print("Tensors with missing shape:", missing)


    # model = onnx.load(model_path)
    # graph = model.graph

    # # 找到所有 initializer 名字
    # init_names = {init.name for init in graph.initializer}

    # # 遍历常数，给没有 shape 的补 shape
    # for init in graph.initializer:
    #     if init.name in ["Mul_2_param0", "Mul_4_param0", "Mul_12_param0",
    #                     "Mul_11_param0", "Mul_10_param0", "Mul_9_param0",
    #                     "Mul_5_param0", "Mul_6_param0", "Mul_7_param0", "Mul_8_param0"]:
    #         np_val = numpy_helper.to_array(init)
    #         vi = helper.make_tensor_value_info(
    #             init.name,
    #             init.data_type,
    #             np_val.shape if np_val.shape != () else []  # 标量用 []
    #         )
    #         graph.value_info.append(vi)

    # onnx.save(model, fix_model_path)

    # missing = check_missing_shapes(fix_model_path)
    # print("Tensors with missing shape:", missing)

    print("load the model")
    model = ModelWrapper(model_path)
    print("streamline model behavior test")
    streamlined_output = streamline_model_behavior_test(model)
    print("streamlined output:", streamlined_output)

if __name__ == "__main__":
    main()