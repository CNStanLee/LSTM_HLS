import numpy as np

def convert_npy_to_c_array(npy_filepath, filename="array_output.txt"):
    """
    从.npy文件读取数据并转换为C语言数组定义形式
    
    Args:
        npy_filepath: .npy文件路径
        filename: 输出txt文件名
    """
    try:
        # 从.npy文件加载数据
        data = np.load(npy_filepath)
        print(f"成功加载文件: {npy_filepath}")
        print(f"数据形状: {data.shape}")
        print(f"数据类型: {data.dtype}")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {npy_filepath}")
        return None
    except Exception as e:
        print(f"错误: 加载文件时出错 - {e}")
        return None
    
    def array_to_c_string(arr, indent_level=0):
        """递归将numpy数组转换为C语言字符串形式"""
        indent = "    " * indent_level
        
        # 如果是标量或一维数组
        if arr.ndim == 0 or (arr.ndim == 1 and arr.size <= 1):
            return f"{arr.item():.6f}"
        
        # 如果是一维数组
        if arr.ndim == 1:
            elements = ", ".join([f"{x:.6f}" for x in arr])
            return f"{{\n{indent}    {elements}\n{indent}}}"
        
        # 多维数组
        lines = ["{"]
        for i in range(arr.shape[0]):
            sub_slice = arr[i] if arr.ndim > 1 else arr
            sub_str = array_to_c_string(sub_slice, indent_level + 1)
            lines.append(f"{indent}    {sub_str}" + ("," if i < arr.shape[0] - 1 else ""))
        lines.append(f"{indent}}}")
        return "\n".join(lines)
    
    # 生成维度字符串
    dim_str = "".join([f"[{dim}]" for dim in data.shape])
    
    # 根据数据类型选择C语言类型
    if data.dtype == np.float32 or data.dtype == np.float64:
        c_type = "float"
    elif data.dtype == np.int32:
        c_type = "int"
    elif data.dtype == np.int16:
        c_type = "short"
    elif data.dtype == np.int8:
        c_type = "char"
    elif data.dtype == np.uint32:
        c_type = "unsigned int"
    else:
        c_type = "float"  # 默认使用float
    
    # 生成C数组定义
    c_array_def = f"{c_type} array{dim_str} = {array_to_c_string(data)};"
    
    # 保存到文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"// 从 {npy_filepath} 自动生成的C语言数组定义\n")
        f.write(f"// 数组形状: {data.shape}\n")
        f.write(f"// 数据类型: {data.dtype}\n")
        f.write(f"// 数组大小: {data.size} 元素\n\n")
        f.write(c_array_def)
        f.write("\n")
    
    print(f"转换完成! 结果保存到 {filename}")
    print(f"数组形状: {data.shape}")
    print(f"数据类型: {data.dtype}")
    
    return c_array_def

def convert_npy_to_c_array_simple(npy_filepath, filename="array_simple.txt"):
    """
    简化版本 - 适用于常规的多维数组
    """
    try:
        data = np.load(npy_filepath)
        print(f"成功加载: {npy_filepath}, 形状: {data.shape}")
        
    except Exception as e:
        print(f"错误: {e}")
        return None
    
    def simple_array_to_string(arr):
        """简化版数组转换"""
        if arr.ndim == 1:
            return "{" + ", ".join(f"{x:.6f}" for x in arr) + "}"
        
        inner = ",\n".join(["    " + simple_array_to_string(sub) for sub in arr])
        return "{\n" + inner + "\n}"
    
    # 生成维度
    dims = "".join(f"[{size}]" for size in data.shape)
    c_type = "float" if data.dtype in [np.float32, np.float64] else "int"
    
    c_code = f"{c_type} array{dims} = {simple_array_to_string(data)};"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"// 从 {npy_filepath} 生成\n")
        f.write(f"// 形状: {data.shape}\n\n")
        f.write(c_code)
    
    print(f"简化版保存到: {filename}")
    return c_code

def batch_convert_npy_files(npy_files, output_dir=""):
    """
    批量转换多个.npy文件
    
    Args:
        npy_files: .npy文件路径列表
        output_dir: 输出目录
    """
    for npy_file in npy_files:
        try:
            # 生成输出文件名
            base_name = npy_file.replace('.npy', '').split('/')[-1].split('\\')[-1]
            output_file = f"{output_dir}{base_name}_c_array.txt"
            
            print(f"\n处理文件: {npy_file}")
            convert_npy_to_c_array(npy_file, output_file)
            
        except Exception as e:
            print(f"处理文件 {npy_file} 时出错: {e}")

# 使用示例
if __name__ == "__main__":
    # 单个文件转换
    npy_file_path = "Conv_1_param0.npy"  # 替换为您的.npy文件路径
    
    # 方法1: 完整版本
    result = convert_npy_to_c_array(npy_file_path, "c_array_output.txt")
    
    # 方法2: 简化版本
    # result = convert_npy_to_c_array_simple(npy_file_path, "c_array_simple.txt")
    
    # 批量转换示例
    # npy_files = ["array1.npy", "array2.npy", "array3.npy"]
    # batch_convert_npy_files(npy_files)
    
    if result:
        print("\n转换成功! 前100个字符预览:")
        print(result[:100] + "...")