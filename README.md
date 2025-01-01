# 百度输入法皮肤res转换
自用小工具，用来将百度输入法皮肤中的.til文件转到仓输入法皮肤格式

## 环境要求
- Python 版本: >= 3.10

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用说明
转换til文件+复制图片+生成切片序号标记+生成百度键盘键位前景背景图片列表
```bash
python main.py "皮肤目录"
```
生成的文件夹中：
- 后缀为**仓输入法**的为转换的til文件和复制的图片文件夹
- 辅助文件夹则是对切片标了序号以及对切片的边缘加了标尺(一格为10像素)，设置insets需要用到。里面的.json文件为对应键盘中所有按键的前景背景使用的切片文件和序号

## 单独使用转换til文件功能
在终端中运行:

```bash
python res.py "皮肤目录"
```

## 单独使用在图片上绘制IMG序号功能
在终端中运行:

```
python edgemark.py "皮肤目录"
```
例:

```
python .\edgemark.py .\星河百度\
```

## 单独使用转换按键前景背景使用切换功能
在终端中运行:

```
python generate_keyboard_images.py "皮肤目录"
```
例:

```
python .\generate_keyboard_images.py .\星河百度\
```

>[!important]
> powershell中当目录名称中有空格时，最后不要带 "\\"
> 即保持这样`python.exe .\demo.py '.\送你一朵小红花_智能深色-26 9键'` 而不能 `python.exe .\demo.py '.\送你一朵小红花_智能深色-26 9键\'`

