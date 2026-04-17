# 🖥️ ysyx-F6 单周期 RISC-V CPU (基于 Logisim)
## ✨ 核心特性

* **完整的数据通路**：支持 RV32I 基础指令集，包含纯手工连线的 PC、ALU、Register File、ImmGen 和 LSU 模块。
* **哈佛/冯·诺依曼混合架构**：支持指令和数据的精准内存映射，完美处理字/字节寻址对齐。
* **VGA 外设驱动**：实现了地址为 `0x20000000` 的 MMIO，CPU 可直接向显存写入像素数据。
* **配套工具链 (Custom Toolchain)**：提供专属 Python 脚本，支持将任意照片转化为 CPU 可读的十六进制数据，并进行“外科手术式”的内存镜像注入。

---
## 📂 仓库结构

```text
📦 ysyx-F6-Project
 ┣ 📂 Logisim实验/        
    ┗ 📜 minirv.circ                   # CPU 核心电路文件 (.circ)
 ┣ 📂 softwareExample/                 # 项目展示截图和说明文档配图
    ┣ 📜 vga.hex                       # 一生一芯LOGO
    ┗ 📜 my_full_color_vga_hex         # 作者头像
 ┣ 📂 tools/                           # 自动化构建工具链 (如 Python 转换脚本)
    ┣ 📜 importImage.py                # 自动转化图片至256*256再转成hex文件
    ┗ 📜 requirements.md               # 小小的配置的环境
 ┗ 📜 README.md                        # 项目说明文档
