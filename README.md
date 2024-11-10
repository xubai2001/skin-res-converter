# 百度输入法皮肤res转换
自用小工具，用来将百度输入法皮肤中的.til文件转到仓输入法皮肤格式

## 环境要求
- Python 版本: >= 3.10

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用说明
在终端中运行:

```bash
python res.py "皮肤目录"
```
例:
```
python.exe .\demo.py .\Gboard_anb
```

>[!important]
> powershell中当目录名称中有空格时，最后不要带\
> 即保持这样`python.exe .\demo.py '.\送你一朵小红花_智能深色-26 9键'` 而不能 `python.exe .\demo.py '.\送你一朵小红花_智能深色-26 9键\'`

