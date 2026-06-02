# 🔬 Model Lab

**三维模型查看器** - 支持 CAD/STL/STEP/点云等多种三维模型格式

一个基于 Web 的轻量级三维模型查看工具，支持常见的 CAD 和网格格式，提供简洁的交互界面用于模型预览和检查。

---

## ✨ 功能特性

- 📦 **多格式支持**：STL / OBJ / PLY / GLTF / GLB / OFF / STEP
- 🎨 **Web 界面**：基于 NiceGUI 的现代化 UI
- 🔄 **模型转换**：支持将 STEP 格式转换为 STL
- 📐 **自动对齐**：模型自动放置在地面网格上
- 🎯 **相机控制**：交互式 3D 视图，自动适配模型尺寸
- 📤 **拖拽上传**：支持直接拖拽文件到浏览器查看

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

核心依赖：
- `nicegui` - Web UI 框架
- `trimesh` - 三维网格处理
- `numpy` - 数值计算

### 运行

```bash
python model_lab.py
```

打开浏览器访问 `http://localhost:8080`

---

## 📂 项目结构

```
model-lab/
├── model_lab.py          # 主程序
├── requirements.txt      # Python 依赖
├── cad_parts/            # 示例 CAD 文件
│   ├── SLDPRT/          # SolidWorks 零件
│   ├── STEP/            # STEP 格式
│   └── STL/             # STL 网格
└── output/              # 转换输出目录
```

---

## 📝 使用说明

1. **上传模型**：点击上传按钮或拖拽文件到界面
2. **支持格式**：
   - 网格格式：STL, OBJ, PLY, GLB, GLTF, OFF
   - CAD 格式：STEP（需要 `pythonocc-core`）
3. **交互操作**：
   - 鼠标左键拖动：旋转视图
   - 鼠标滚轮：缩放
   - 右键拖动：平移

---

## 🔧 高级功能

### STEP 格式支持

如需支持 STEP 文件，需要安装额外依赖：

```bash
conda install -c conda-forge pythonocc-core
```

> **提示**：从 SolidWorks 导出 STEP 文件：`文件 → 另存为 → STEP`

---

## 📊 更新日志

### v0.1.0 (2026-06-02)
- ✅ 初始版本发布
- ✅ 支持 STL/OBJ/PLY/GLTF/GLB/OFF 格式
- ✅ 基础 STEP 格式转换功能
- ✅ 自动模型对齐和视图适配
- ✅ Web 界面拖拽上传

### Roadmap
- [ ] 点云格式支持 (PCD, XYZ, LAS)
- [ ] 模型测量工具
- [ ] 批量转换功能
- [ ] 模型导出优化

---

## 🛠️ 技术栈

- **前端**：NiceGUI + Three.js
- **后端**：Python 3.10+
- **3D 处理**：Trimesh + NumPy
- **CAD 支持**：PythonOCC (可选)

---

## 📄 开源协议

MIT License

---

## 👨‍💻 作者

[@GGBoyJJZU](https://github.com/GGBoyJJZU)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

如有问题或建议，请在 [Issues](https://github.com/GGBoyJJZU/model-lab/issues) 中反馈。
