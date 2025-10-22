import numpy as np

# 读取npy文件
weights = np.load('MatMul_4_param0.npy')

print(f"权重shape: {weights.shape}")
print(f"权重dtype: {weights.dtype}")
print(f"权重范围: [{weights.min()}, {weights.max()}]")

# MVAU配置
MW1 = 3   # 输入维度
MH1 = 32  # 输出维度
PE1 = 8   # 并行处理单元

# 验证shape - 应该是(3, 32)
assert weights.shape == (MW1, MH1), f"Expected shape ({MW1}, {MH1}), got {weights.shape}"

print(f"\n原始权重矩阵形状: {weights.shape}")
print("这表示: 3个输入通道 × 32个输出通道")

# 不需要转置！权重已经是正确的 [输入通道][输出通道] 格式
# weights 的 shape 是 (3, 32)，即 weights[input_channel][output_channel]

# 转换为int8
weights_int8 = weights.astype(np.int8)

# 生成C++头文件 - 保持原始的3x32形状
with open('mvau_weights_include.h', 'w') as f:
    f.write("// Auto-generated MVAU weights from MatMul_4_param0.npy\n")
    f.write(f"// Shape: [{MW1}][{MH1}] - [input_channels][output_channels]\n")
    f.write("// Format: weights[input_channel][output_channel]\n\n")
    
    for i in range(MW1):  # 输入通道
        f.write("    {")
        for j in range(MH1):  # 输出通道
            value = int(weights_int8[i, j])
            f.write(f"{value}")
            if j < MH1 - 1:
                f.write(", ")
        f.write("}")
        if i < MW1 - 1:
            f.write(",\n")
        else:
            f.write("\n")

print("\n权重已转换并保存到 mvau_weights_include.h")
print("\n数据预览 (3个输入通道，每个有32个输出通道权重):")
for i in range(MW1):
    print(f"输入通道 {i}: {weights_int8[i, :4]} ...")  # 只显示前4个值

# 验证矩阵乘法
print("\n\n=== 矩阵乘法验证 ===")
print(f"输入向量: 1 × {MW1}")
print(f"权重矩阵: {MW1} × {MH1}") 
print(f"输出向量: 1 × {MH1}")

# 示例输入
test_input = np.array([100, 150, 200], dtype=np.int32)
print(f"\n示例输入: {test_input}")

# 手动计算矩阵乘法
output = np.zeros(MH1, dtype=np.int32)
for j in range(MH1):  # 每个输出通道
    for i in range(MW1):  # 每个输入通道
        output[j] += test_input[i] * weights_int8[i, j]

print(f"\n前10个输出通道的结果:")
for j in range(min(10, MH1)):
    print(f"  输出通道 {j}: {test_input} · {weights_int8[:, j]} = {output[j]}")

# 验证PE打包格式
print(f"\n\n=== PE打包验证 ===")
print(f"总共需要 {MH1//PE1} 个PE组 (WMEM1)")
print(f"每个PE组处理 {PE1} 个输出通道")

for pe_block in range(MH1//PE1):
    print(f"\nPE组 {pe_block} (输出通道 {pe_block*PE1} 到 {(pe_block+1)*PE1-1}):")
    for simd_idx in range(MW1):  # 输入通道/SIMD
        print(f"  输入通道 {simd_idx}: ", end="")
        for p in range(PE1):
            output_channel = pe_block * PE1 + p
            weight_val = weights_int8[simd_idx, output_channel]
            print(f"{weight_val:4d} ", end="")
        print()