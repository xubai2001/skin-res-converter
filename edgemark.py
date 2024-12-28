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

def process_til_file(til_path, output_directory):
    """
    处理单个 .til 文件，解析配置并在对应的 .png 图片上绘制内容。
    """
    # 获取对应的图片路径
    image_path = os.path.splitext(til_path)[0] + ".png"
    if not os.path.exists(image_path):
        print(f"对应的图片文件不存在: {image_path}")
        return

    # 读取 .til 配置文件
    config = configparser.ConfigParser()
    config.read(til_path, encoding="utf-8-sig")

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

    # 判断路径中是否包含 'dark' 或 'light'
    if "dark" in image_path.lower():
        subdir = "dark"
    elif "light" in image_path.lower():
        subdir = "light"
    else:
        subdir = "other"
    # 创建输出子目录
    output_subdir = os.path.join(output_directory, subdir)
    os.makedirs(output_subdir, exist_ok=True)

    # 保存绘制后的图片到新的路径
    output_path = os.path.join(output_subdir, os.path.basename(image_path))
    image.save(output_path)
    print(f"处理完成，结果保存至: {output_path}")

def process(source_path, destination_path):
    """
    遍历路径下的所有 .til 文件，并调用处理函数。
    """
    for root, _, files in os.walk(source_path):
        for file in files:
            if file.endswith(".til"):
                til_path = os.path.join(root, file)
                process_til_file(til_path, destination_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="处理源目录文件并保存到目标目录")
    parser.add_argument("source", type=Path, help="源目录路径")
    parser.add_argument("target", type=Path, help="目标目录路径")
    # 解析参数
    args = parser.parse_args()

    # 执行文件转换
    process(args.source, args.target)
