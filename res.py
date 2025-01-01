import os
import configparser
import yaml
from pathlib import Path
import shutil
import argparse


def parse_til_to_yaml(file_path):
    """读取 .til 文件并转换为 YAML 格式"""
    config = configparser.ConfigParser()
    config.read(file_path, encoding="utf-8-sig")

    yaml_data = {}
    for section in config.sections():
        if config.has_option(section, "SOURCE_RECT"):
            # 解析 SOURCE_RECT
            source_rect = list(map(int, config.get(section, "SOURCE_RECT").split(",")))
            x, y, width, height = source_rect
            rect = {"x": x, "y": y, "width": width, "height": height}

            # 解析 INNER_RECT
            try:
                inner_rect = list(
                    map(int, config.get(section, "INNER_RECT").split(","))
                )
                ix, iy, iwidth, iheight = inner_rect
                insets = {
                    "top": iy - y,
                    "bottom": height - (iy - y) - iheight,
                    "left": ix - x,
                    "right": width - (ix - x) - iwidth,
                }
            except configparser.NoOptionError:
                insets = None

            # 构建 YAML 数据
            yaml_data[section] = (
                {"rect": rect, "insets": insets}
                if insets
                else {"rect": rect}
            )

    return yaml.dump(yaml_data, sort_keys=False, allow_unicode=True)


def process(src_dir):
    # 创建目标目录结构：源文件夹名称-仓输入法/dark/resources 和 light/resources
    src_folder_name = os.path.basename(src_dir) #源文件夹名称
    dst_base_dir = os.path.join(os.path.dirname(src_dir), f"{src_folder_name}-仓输入法") # 目标文件夹路径

    # dark和light
    dst_dark_dir = os.path.join(dst_base_dir, "dark", "resources")
    dst_light_dir = os.path.join(dst_base_dir, "light", "resources")

    # 创建目录
    os.makedirs(dst_dark_dir, exist_ok=True)
    os.makedirs(dst_light_dir, exist_ok=True)

    # 递归处理 dark 和 light 目录
    for mode in ["dark", "light"]:
        src_mode_dir = os.path.join(src_dir, mode)
        
        if not os.path.exists(src_mode_dir):
            print(f"警告: 源目录中未找到 {mode} 子目录: {src_mode_dir}")
            continue

        # 遍历 dark 或 light 目录下的所有文件
        for root, _, files in os.walk(src_mode_dir):
            for file in files:
                if file.endswith(".til"):
                    # 构建输入和输出文件路径
                    src_file_path = os.path.join(root, file) # 此路径为.til文件路径
                    if "land" in src_file_path:
                        continue # 跳过 land 目录

                    # 确定目标目录
                    dst_mode_dir = dst_dark_dir if mode == "dark" else dst_light_dir
                    dst_file_path = os.path.join(dst_mode_dir, file)

                    # 创建目标文件夹（如果不存在）
                    os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)

                    # 读取 .til 文件并转换为 YAML
                    yaml_content = parse_til_to_yaml(src_file_path)

                    # 将 YAML 内容写入目标文件
                    with open(dst_file_path.replace(".til", ".yaml"), "w", encoding="utf-8") as yaml_file:
                        yaml_file.write(yaml_content)

                    print(f"转换成功: {src_file_path} -> {dst_file_path}")

                    # 复制同名 .png 文件
                    png_file_path = src_file_path.replace(".til", ".png")
                    dst_png_path = dst_file_path.replace(".til", ".png")
                    if os.path.exists(png_file_path):
                        os.makedirs(os.path.dirname(dst_png_path), exist_ok=True)
                        shutil.copy2(png_file_path, dst_png_path)

if __name__ == "__main__":
    # 初始化 ArgumentParser
    parser = argparse.ArgumentParser(description="处理源目录文件并保存到目标目录")
    parser.add_argument("source", type=Path, help="源目录路径")
    # 解析参数
    args = parser.parse_args()

    # 执行文件转换
    process(args.source)