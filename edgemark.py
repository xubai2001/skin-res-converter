import os
import configparser
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import argparse

def draw_ruler(draw, x, y, width, height):
    """在矩形框四边绘制朝内的刻度"""
    def draw_tick(start_x, start_y, end_x, end_y, label, color):
        draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=1)

    for i in range(10, 80, 10):
        # 上边和下边 (红色)
        draw_tick(x + i, y, x + i, y + 10, i, "#f00056")
        draw_tick(x + width - i, y, x + width - i, y + 10, i, "#16a951")
        draw_tick(x + i, y + height, x + i, y + height - 10, i, "#f00056")
        draw_tick(x + width - i, y + height, x + width - i, y + height - 10, i, "#16a951")
        
        # 左边 (蓝色)
        draw_tick(x, y + i, x + 10, y + i, i, "#4b5cc4")
        draw_tick(x, y + height - i, x + 10, y + height - i, i, "#4b5cc4")
        
        # 右边 (绿色)
        draw_tick(x + width, y + i, x + width - 10, y + i, i, "#16a951")
        draw_tick(x + width, y + height - i, x + width - 10, y + height - i, i, "#16a951")

def process_til_file(src_dir, dst_dir):
    """
    处理单个 .til 文件，解析配置并在对应的 .png 图片上绘制内容。
    """
    # 获取对应的图片路径
    image_path = os.path.splitext(src_dir)[0] + ".png"
    if not os.path.exists(image_path):
        print(f"对应的图片文件不存在: {image_path}")
        return

    # 读取 .til 配置文件
    config = configparser.ConfigParser()
    config.read(src_dir, encoding="utf-8-sig")

    # 打开对应的图片
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 30)

    # 遍历所有配置节
    for section in config.sections():
        if config.has_option(section, "SOURCE_RECT"):
            # 解析 SOURCE_RECT，格式为 "x,y,width,height"
            source_rect = list(map(int, config.get(section, "SOURCE_RECT").split(",")))
            x, y, width, height = source_rect
            # 绘制矩形边框
            draw.rectangle([x, y, x + width, y + height], outline="red", width=1)
            # 在矩形中心绘制文字
            text_x, text_y = x + width // 2, y + height * 0.8
            draw.text((text_x, text_y), section.replace("IMG", ""), fill="red", anchor="mm", font=font)
            # 绘制刻度标记
            if width >= 100 and height >= 100:
                draw_ruler(draw, x, y, width, height)


    # 保存绘制后的图片到新的路径
    # os.makedirs(dst_dir, exist_ok=True)
    image.save(dst_dir)
    # print(f"处理完成，结果保存至: {dst_dir}")

def process(src_dir):
    """
    遍历路径下的所有 .til 文件，并调用处理函数。
    """
    src_folder_name = os.path.basename(src_dir)
    dst_base_dir = os.path.join(os.path.dirname(src_dir), f"{src_folder_name}-辅助")

    # 
    dst_dark_dir = os.path.join(dst_base_dir, "dark")
    dst_light_dir = os.path.join(dst_base_dir, "light")

    # 创建目录
    os.makedirs(dst_dark_dir, exist_ok=True)
    os.makedirs(dst_light_dir, exist_ok=True)
    # print(f"目标目录: {dst_dark_dir}")

    # 递归处理 dark 和 light 目录
    for mode in ["dark", "light"]:
        src_mode_dir = os.path.join(src_dir, mode)

        if not os.path.exists(src_mode_dir):
            print(f"警告: 源目录中未找到 {mode} 子目录: {src_mode_dir}")
            continue

        # 递归处理 dark 和 light 目录
        for root, _, files in os.walk(src_mode_dir):
            for file in files:
                if file.endswith(".til"):
                    src_file_path = os.path.join(root, file) # 此路径为.til文件路径
                    if "land" in src_file_path:
                        continue # 跳过 land 目录
                    # 确定目标目录
                    dst_mode_dir = dst_dark_dir if mode == "dark" else dst_light_dir
                    dst_png_dir = os.path.join(dst_mode_dir, file.replace(".til", ".png")) # 转换图片的目标目录

                    # 创建目标文件夹（如果不存在）
                    os.makedirs(os.path.dirname(dst_png_dir), exist_ok=True)

                    print(dst_png_dir)
                    # 处理图片
                    process_til_file(src_file_path, dst_png_dir)

                    print(f"图片处理完成: {src_file_path} -> {dst_png_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="处理源目录文件并保存到目标目录")
    parser.add_argument("source", type=Path, help="源目录路径")
    # parser.add_argument("target", type=Path, help="目标目录路径")
    # 解析参数
    args = parser.parse_args()

    # 执行文件转换
    process(args.source)
