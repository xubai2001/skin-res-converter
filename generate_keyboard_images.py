import yaml
import configparser
import json
import os
import argparse
from pathlib import Path
from collections import defaultdict

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
    # 初始化字典，键为 target_folders 中的文件夹名称，值为空字典
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
    # 检查 output_path 是否存在，如果不存在则创建文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
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


def parse_keyboard(file_path, output_path,css_dict: dict):
    config = configparser.ConfigParser()
    config.read(file_path, encoding="utf-8-sig")

    # 解析default.css中对应的文件和切片
    def parse_style(style, type):
        return {
            "file": css_dict[f"STYLE{style}"][type][0].split(",")[0],
            "image": "IMG" + css_dict[f"STYLE{style}"][type][0].split(",")[1],
        }

    hamster_dict = {}
    for section in config.sections():
        if config.has_option(section, "CENTER"):
            key_name = config.get(section, "CENTER")
            if key_name in baiduKeyMap:
                key_name = baiduKeyMap[key_name]
            # 读取百度键盘配置 按键背景+前景
            # 背景处理
            try:
                backgroundStyle = config.get(section, "BACK_STYLE")
                backgroundStyle = {
                "normalImage": parse_style(backgroundStyle, "NM_IMG"),
                "highlightImage": parse_style(backgroundStyle, "HL_IMG"),
            }
            except:
                backgroundStyle = {}

            # 前景处理
            try:
                foregroundStyle = config.get(section, "FORE_STYLE")
                # 前景有多个 需遍历转换
                foregroundStyles = []  # 创建一个空数组来存储符合条件的 foregroundStyle
                for style in foregroundStyle.split(","):
                    if "NM_IMG" not in css_dict.get(f"STYLE{style}", ""):
                        continue
                    foregroundStyle_dict = {
                        "normalImage": parse_style(style, "NM_IMG"),
                        "highlightImage": parse_style(style, "HL_IMG"),
                    }
                    foregroundStyles.append(foregroundStyle_dict)  # 将符合条件的 foregroundStyle 添加到数组中
            except:
                foregroundStyles = []
            hamster_dict[key_name] = {
                "backgroundStyle": backgroundStyle,
                "foregroundStyle": foregroundStyles  # 将 foregroundStyle 设为数组
            }
    

    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(hamster_dict, f, indent=4, ensure_ascii=False)
    save_to_json(hamster_dict, output_path)
    return hamster_dict



def parse_py_26(file_path, hamster_dict):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    # 替换字母键背景 前景
    for i in "qwertyuiopasdfghjklzxcvbnm":
        data[f"{i}ButtonBackgroundStyle"] = hamster_dict[i]["backgroundStyle"]
        data[f"{i}Button"]["backgroundStyle"] = f"{i}ButtonBackgroundStyle"

        data[f"{i}ButtonForegroundStyle"]["normalImage"] = hamster_dict[i]["foregroundStyle"]["normalImage"]
        data[f"{i}ButtonForegroundStyle"]["highlightImage"] = hamster_dict[i]["foregroundStyle"]["highlightImage"]

    # 替换功能键
    for i in ["shift", "backspace", "symbol", "123", "space", "enter"]:
        data[f"{i}ButtonBackgroundStyle"]["normalImage"] = hamster_dict[i]["backgroundStyle"]["normalImage"]
        data[f"{i}ButtonBackgroundStyle"]["highlightImage"] = hamster_dict[i]["backgroundStyle"]["highlightImage"]

        data[f"{i}ButtonForegroundStyle"]["normalImage"] = hamster_dict[i]["foregroundStyle"]["normalImage"]
        data[f"{i}ButtonForegroundStyle"]["highlightImage"] = hamster_dict[i]["foregroundStyle"]["highlightImage"]
    with open("./百度转仓输入法/hamster_skin_com.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    
def process(source_path, destination_path):
    # 执行文件转换
    target_folders = ['dark', 'light']
    target_files = ['default.css', 'py_26.ini', 'py_9.ini', 'num_9.ini','symbol.ini','sel_ch.ini']

    files = get_files(source_path, target_folders, target_files)
    for theme, value in files.items():
        default_css = parse_ini_with_duplicates(value['default.css'])
        for name, path in value.items():
            if name.endswith('.ini'):
                new_name = name.replace('.ini', '.json')
                parse_keyboard(path, f"{destination_path}/{theme}/{new_name}", default_css)
                print(f"{name}处理完成 结果保存至:{destination_path}/{theme}/{new_name}")
    
