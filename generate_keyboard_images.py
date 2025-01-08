import configparser
import json
import os
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

baiduKeyMap = {
    "'": "分词",
    "，": "逗号",
    "。": "semicolon",
    "F1": "symbol",
    "F6": "123",
    "F4": "return",
    "F9": "展开候选",
    "F11": "shift", 
    "F16": "中英切换",   
    "F22": "pageUp",
    "F23": "pageDown",
    "F27": "锁定键",
    "F31": "primaryButton",
    "F36": "backspace",
    "F38": "space",
    "F39": "enter",
    "F40": "清空输入码",
    "F55": "符号键盘符号背景",
    "F62": "切换其他输入法(地球)",
    "F75": "换行"
}


def get_files(root_folder, target_folders, target_files):
    result = {folder: {} for folder in target_folders}
    
    # 查找目标文件夹
    for path in Path(root_folder).rglob('*'):
        if path.is_dir() and path.name in target_folders:
            # 在目标文件夹中查找指定文件
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.name in target_files:
                    # 将找到的文件路径添加到对应键的子字典中
                    result[path.name][file_path.name] = str(file_path)
    
    return result

def save_to_json(hamster_dict, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True) # 创建输出目录
    
    # 写入 JSON 文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hamster_dict, f, indent=4, ensure_ascii=False)

def parse_ini_with_duplicates(file_path):
    # 自定义读取 ini 文件，处理重复键
    data = defaultdict(dict)
    with open(file_path, 'r', encoding='utf-8') as f:
        current_section = None
        for line in f:
            line = line.strip()
            if not line or line.startswith(";") or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]
                data[current_section] = defaultdict(list)
            elif "=" in line and current_section is not None:
                key, value = map(str.strip, line.split("=", 1))
                data[current_section][key].append(value)
            else:
                raise ValueError(f"Invalid line: {line}")
    return data

def parse_style(style: str, type: str, css_dict: Dict[str, Any]) -> Dict[str, str]:
    """解析样式信息"""
    try:
        file, image = css_dict[f"STYLE{style}"][type][0].split(",")
        return {"file": file, "image": "IMG" + image}
    except KeyError:
        print(f"样式 {style} 或类型 {type} 在 css_dict 中未找到")
        return {}
    except Exception as e:
        print(f"解析样式时发生异常: {e}")
        return {}

def parse_config_file(file_path: str) -> configparser.ConfigParser:
    """解析并处理配置文件"""
    config = configparser.ConfigParser()
    # 百度配置中的ini并不标准，这里手动读取处理一下
    valid_lines = []
    
    with open(file_path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                valid_lines.append(line)
            elif "=" in line:
                valid_lines.append(line)
            elif line:
                print(f"忽略无效行: {line}")
    
    config.read_string('\n'.join(valid_lines))
    return config

def parse_keyboard(file_path: str, output_path: str, css_dict: Dict[str, Any]) -> Dict[str, Any]:
    """根据百度皮肤内的default.css文件和百度皮肤键盘的配置文件，解析出各个按键的背景和前景图片，并保存到 hamster_dict 中，最后保存到 JSON 文件

    :param file_path: 百度皮肤键盘配置文件路径
    :param output_path: 输出 JSON 文件路径
    :param css_dict: 解析 default.css 文件得到的字典
    """

    config = parse_config_file(file_path) # 解析百度键盘ini文件
    hamster_dict = {}

    for section in config.sections():
        if not config.has_option(section, "CENTER"):
            continue

        key_name = config.get(section, "CENTER")
        key_name = baiduKeyMap.get(key_name, key_name)

        # 解析背景样式
        backgroundStyle = {}
        if config.has_option(section, "BACK_STYLE"):
            try:
                background_style = config.get(section, "BACK_STYLE")
                backgroundStyle = {
                    "normalImage": parse_style(background_style, "NM_IMG", css_dict),
                    "highlightImage": parse_style(background_style, "HL_IMG", css_dict),
                }
            except Exception as e:
                print(f"背景样式异常: {e}")

        # 解析前景样式
        foregroundStyles = []
        if config.has_option(section, "FORE_STYLE"):
            try:
                foreground_style = config.get(section, "FORE_STYLE")
                foregroundStyles = [
                    {
                        "normalImage": parse_style(style, "NM_IMG", css_dict),
                        "highlightImage": parse_style(style, "HL_IMG", css_dict),
                    }
                    for style in foreground_style.split(",")
                    if "NM_IMG" in css_dict.get(f"STYLE{style}", "")
                ]
            except Exception as e:
                print(f"前景样式异常: {e}")

        hamster_dict[key_name] = {
            "backgroundStyle": backgroundStyle,
            "foregroundStyle": foregroundStyles,
        }

    save_to_json(hamster_dict, output_path)
    return hamster_dict

    
def process(src_dir):
    # 创建目标目录结构：源文件夹名称-仓输入法/dark/resources 和 light/resources
    src_folder_name = os.path.basename(src_dir) #源文件夹名称
    dst_dir = os.path.join(os.path.dirname(src_dir), f"{src_folder_name}-辅助") # 目标文件夹路径
    # 执行文件转换
    target_folders = ['dark', 'light']
    target_files = ['default.css', 'py_26.ini', 'en_26.ini', 'py_9.ini', 'num_9.ini','symbol.ini','sel_ch.ini']

    files = get_files(src_dir, target_folders, target_files)
    for theme, value in files.items():
        default_css = parse_ini_with_duplicates(value['default.css'])
        for name, path in value.items():
            if name.endswith('.ini'):
                new_name = name.replace('.ini', '.json')
                parse_keyboard(path, f"{dst_dir}/{theme}/{new_name}", default_css)
                print(f"{name}处理完成 结果保存至:{dst_dir}/{theme}/{new_name}")
    
if __name__ == "__main__":
    # 初始化 ArgumentParser
    parser = argparse.ArgumentParser(description="处理源目录文件并保存到目标目录")
    parser.add_argument("source", type=Path, help="源目录路径")
    # 解析参数
    args = parser.parse_args()

    # 执行文件转换
    process(args.source)