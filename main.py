from edgemark import process as edgemark_process
from res import process as res_process
from generate_keyboard_images import process as keyboard_image_process

import argparse
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="处理源目录文件并保存到目标目录")
    parser.add_argument("source", type=Path, help="源目录路径")
    args = parser.parse_args()

    print("开始处理文件...")
    print("====开始转换图片描述文件并复制图片..====")
    res_process(args.source)

    print("====开始标记切片序号...====")
    edgemark_process(args.source)

    print("====开始读取百度键盘配置并生成按键使用图片列表...====")
    keyboard_image_process(args.source)