from edgemark import process as edgemark_process
from res import convert_files as res_process
from generate_keyboard_images import process as keyboard_image_process

import argparse
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="处理源目录文件并保存到目标目录")
    parser.add_argument("source", type=Path, help="源目录路径")
    parser.add_argument('--replace', action='store_const', const=1, default=0, help='是否当inner_rect等于source_rect时，替换为默认inner_rect值')
    parser.add_argument("destination", type=Path, help="目标目录路径")
    args = parser.parse_args()

    print("开始处理文件...")
    print("====开始转换图片描述文件并复制图片..====")
    res_process(args.source, args.replace)

    print("====开始标记切片序号...====")
    edgemark_process(args.source, args.destination)

    print("====开始读取百度键盘配置并生成按键使用图片列表...====")
    keyboard_image_process(args.source, args.destination)