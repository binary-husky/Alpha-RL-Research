---
name: rednote-cover
description: Generate Xiaohongshu (RedNote) cover images in 3:4 format.
---

# 小红书封面图生成详细指南

## 封面图比例（3:4）竖屏

# 生成流程

1. 查看以下参考图片，转化成html格式。如果有背景，则暂时使用纯色背景

参考图片：`https://serve.gptacademic.cn/publish/auto/rednote/图片3.png`
html输出路径：`./rednote_cover_html_and_sceenshot/main.html`


2. 使用playwright-cli截图，playwright-cli 需要使用 tmux 运行 （如果你不使用tmux，会遇到GPU错误、网络错误等各种错误），放置到路径：`./rednote_cover_html_and_sceenshot/main.v1.png`


3. 对比 参考图片 和 playwright截图，修改 html 弥合二者的差距，生成 main.v2.png，重复该步骤，生成 main.v3.png、main.v4.png，
  直到不再有除了背景图像以外的其他区别，尤其是：
    - 界面布局的区别
    - 元素位置的区别
    - 字体的区别
    - 如果图片右下角有皇冠图案水印，移除它


4. 使用nano-banana生成与当前文章主题相关的背景图像，色调图参考图片需要基本一致


5. 将生成的图像应用到 html 中，最后生成 main.final.png



# nano-banana 生成图像的方法

见skill
alpha_auto_research/skills/banana_image/SKILL.md






# playwright-cli 截图指南

### 重要：必须在 tmux 中运行

playwright-cli 必须在 tmux 会话中启动浏览器，否则会遇到 GPU 错误、网络错误等问题。

### 步骤

1. **启动 HTTP 服务器**（file:// 协议被阻止）：
```bash
cd ./rednote_cover_html_and_sceenshot && python3 -m http.server 18888 &
```

2. **在 tmux 中打开浏览器**：
```bash
tmux new-session -d -s pw "playwright-cli open 'http://localhost:18888/main.html' && sleep 999999"
```

3. **等待浏览器启动后，导航并截图**：
```bash
# 检查浏览器是否就绪
playwright-cli list

# 导航到页面（如果需要）
playwright-cli goto "http://localhost:18888/main.html"

# 设置视口大小（3:4 比例，如 900x1200）
playwright-cli resize 900 1200

# 截图
playwright-cli screenshot --filename="./rednote_cover_html_and_sceenshot/main.v1.png"
```

4. **迭代修改时，重新加载页面并截图**：
```bash
playwright-cli reload && playwright-cli screenshot --filename="./rednote_cover_html_and_sceenshot/main.v2.png"
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `playwright-cli list` | 列出所有浏览器会话 |
| `playwright-cli open <url>` | 打开浏览器并导航到 URL |
| `playwright-cli goto <url>` | 导航到 URL |
| `playwright-cli resize <w> <h>` | 设置视口大小 |
| `playwright-cli reload` | 重新加载页面 |
| `playwright-cli screenshot --filename=<path>` | 截图保存到指定路径 |
| `playwright-cli -s=<session> <cmd>` | 指定会话执行命令 |

### 注意事项

- 如果遇到 "browser not open" 错误，检查 tmux 会话是否正常运行
- 截图前确保 HTTP 服务器在运行
- 完成后记得关闭 HTTP 服务器：`pkill -f "python3 -m http.server 18888"`

