import os
import configparser
import yaml
from pathlib import Path
import shutil
import argparse


def parse_til_to_yaml(file_path, is_replace_inner_rect):
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
                if is_replace_inner_rect and ix == x and iy == y and iwidth == width and iheight == height:
                    insets =  {
                        'top': 40,
                        'bottom': 40,
                        'left': 35,
                        'right': 35
                    }    
                else:
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


def convert_files(src_dir, is_replace_inner_rect):
    """递归遍历目录，将 .til 文件转换为 .yaml 并保存到目标目录"""
    # 自动生成目标目录名并加上后缀
    dst_dir = f"{src_dir}-仓输入法"
    os.makedirs(dst_dir, exist_ok=True)

    print(f"输出目录：{dst_dir}")

    for root, _, files in os.walk(src_dir):
        # 遍历当前目录下所有文件
        for file in files:
            if file.endswith(".til"):
                # 构建输入和输出文件路径
                src_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(src_file_path, src_dir)

                # 修改输出路径，确保 "res" 目录被替换为 "resource"
                dst_file_path = os.path.join(
                    dst_dir, Path(relative_path).with_suffix(".yaml")
                )
                dst_file_path = dst_file_path.replace("\\res", "\\resources")

                # 创建目标文件夹（如果不存在）
                os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)

                # 读取 .til 文件并转换为 YAML
                yaml_content = parse_til_to_yaml(src_file_path, is_replace_inner_rect)

                # 将 YAML 内容写入目标文件
                with open(dst_file_path, "w", encoding="utf-8") as yaml_file:
                    yaml_file.write(yaml_content)

                print(f"转换成功: {src_file_path} -> {dst_file_path}")

                # 复制同名 .png 文件（如果存在）
                png_file_path = src_file_path.replace(".til", ".png")
                dst_png_path = dst_file_path.replace(".yaml", ".png")
                if os.path.exists(png_file_path):
                    os.makedirs(os.path.dirname(dst_png_path), exist_ok=True)
                    shutil.copy2(png_file_path, dst_png_path)
            if file == "demo.png":
                dst_png_path = os.path.join(dst_dir, "demo.png")
                shutil.copy2(os.path.join(root, file), dst_png_path)


if __name__ == "__main__":
    # 初始化 ArgumentParser
    parser = argparse.ArgumentParser(description="处理源目录文件并保存到目标目录")
    parser.add_argument("source", type=Path, help="源目录路径")
    parser.add_argument('--replace', action='store_const', const=1, default=0, help='是否当inner_rect等于source_rect时，替换为默认inner_rect值')
    # parser.add_argument("destination", type=Path, help="目标目录路径")

    # 解析参数
    args = parser.parse_args()

    # 执行文件转换
    convert_files(args.source, args.replace)