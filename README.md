# 一生一芯 F6 单周期CPU设计
**基于logisim的32位单周期RISC-V CPU，点亮”一生一芯“专属LOGO**
### 作者申明
> 本F6阶段使用CPU模块化设计，并非根据讲义做指令级别的CPU设计，我们强调处理抽象的“共性”，而非仅仅一个
> 简单的**硬编码状态机**，为什么？因为作者在F5阶段解决“以指令形式完成简单的数列求和处理器”时，发现只是单纯的设计指令级别的逻辑电路，虽然见效极快、不用考虑指令的共性、不用绕脑子、所见即所得、无需理解“译码-执行-写回”这种通用
> 流水线的抽象概念，但是这种设计根本不能叫**CPU**，如果在接下来的实验中，我们将测试C语言代码多生成几条额外的指令，这种电路会瞬间崩溃，因为它们没有留下任何拓展余地，要增加一条指令，就只能把整个电路拆了重新飞线，非常麻烦
> 因此，此次我们走最正统，但也最艰难的道路——**CPU模块化设计**
---
## 🏗️ 系统架构设计
### 核心架构：32位单周期 RISC-V 处理器 (RV32I 基础指令集)。
### 存储设计：
- **指令存储器（ROM）**：1M 字容量（20位地址线），负责提供机器码指令。
- **数据存储器（RAM）**：1M 字容量（20位地址线），负责运行时变量与静态数据读取。
### 外设控制（MMIO）：
- 在LSU内部集成地址译码器。
- 拦截[ 0x20000000 , 0x20040000 ]地址区间，将其重定向至外接的RGB视频显存，实现指令画图
---
## 🧩核心子模块架构说明（🌟重点！！！）
> 本CPU采用高度模块化的设计思想，严格按照RISC-V规范将复杂处理器拆分为职责单一的硬件单元。以下是各模块的内部机制与功能说明：
### 🟡1.指令获取与程序计数（PC & Fetch)
- **功能简述**：CPU的“节拍器”和“指针”。负责存储当前正在执行的指令地址，并在每个时钟周期上升沿更新。同时，这个PC模块还集成了跳转地址与PC+4的选择功能，因此接口除了基础的WE、CLK、Reset，还包括Imm、isJALR、PCSrc、ALU_Result(后续将介绍具体功能）
#### 具体功能介绍：
- Imm来自另外一个子模块（ImmGen立即数生成器）。
- isJALR特殊判断这条指令是不是JALR指令。
- PCSrc来自另外一个子模块（Branch_Ctrl），用于生成跳转地址的信号。
- ALU_Result来自另外一个子模块（ALU），是ALU计算的结果。
#### 逻辑如何实现？
- 先处理跳转的结果：JALR指令要求将ALU_Result的低位必须变0，是地址对齐的要求，先生成JALR所需地址，另外一种跳转是PC+Imm，这两个结果的选择通过isJALR和多路选择器实现，将该选择结果记为target_Addr。
- 接着根据PCSrc选择是否需要跳转，若需要跳转，则选择target_Addr，不需要则选择PC+4。
#### 设计图：<img width="1503" height="1347" alt="image" src="https://github.com/user-attachments/assets/93bc932b-55f4-489e-9dda-5bad109c93a3" />
### 🟡2.地址跳转控制器（Branch_Ctrl,PCSrc）
- **功能简介**：CPU的方向盘。专门处理复杂的条件跳转逻辑。
#### 具体功能介绍：
- 废弃了传统的“通过 ALU 减法第 0 位判断大小”的脆弱逻辑。
- 在 ALU 内部集成专业的 双路比较器 (Comparators)，精准输出 LessS (有符号小于)、LessU (无符号小于) 和 Equal (等于) 标志位。
- 模块内部使用 8 选 1 逻辑多路选择器，根据 funct3 动态匹配正确的判断条件，完美覆盖 beq, bne, blt, bge, bltu, bgeu，彻底根绝 C 语言中由于类型强转导致的 panic 死循环。
#### 设计图：<img width="974" height="1221" alt="image" src="https://github.com/user-attachments/assets/9dcb14a1-f351-46da-a76e-5d4d1197d1be" />
### 🟡3.译码器（Decoder)
- **功能简述**：CPU的解剖刀。负责将32位机械码**肢解**成各个部位的功能位段。**同时我自己设计集成了ImmGen子模块进去（ImmGen模块在第三点）**
#### 具体功能介绍：
- 很简单，将32为拆分成7+5+5+3+5+7这6段，分别对应funct7、rs2、rs1、funct3、rd、opcode
- 再接一个ImmGen模块根据这个32位数据生成Imm_Out
#### 设计图：<img width="1932" height="1098" alt="image" src="https://github.com/user-attachments/assets/fb55435f-d6dd-4f68-8270-9f8d052cf1eb" />
### 🟡4.立即数生成器（ImmGen）
- **功能简述**：负责将指令中打乱的短位宽立即数，拼接并符号拓展为完整的32位数据
#### 具体功能介绍：
- 各类指令：I、S、B、U、J这些具体指令的Imm是怎么散落在机械码里的自己先去RTFM一下（RISC-V第一册）
- 然后根据Opcode选择对应型号指令的Imm作为输出，具体实现那必然就是多路选择器咯，但是总共就5种，我们就用一个8-3的就行了，那3位根据Opcode自己定义规则去生成，可以用比较器，也可以按下图（我用ROM，虽然这样在真实电路中会浪费资源，但是logisim中非常清晰又简单呀！）
#### 设计图：<img width="1578" height="1342" alt="image" src="https://github.com/user-attachments/assets/cd5f2bda-0378-44f8-8291-ad6058a38b39" />
### 🟡5.寄存器堆（RegisterFile）
- **功能简述**：CPU的极速工作台。提供32个32位通用寄存器（x0-x31)(注意x0始终为0哦，具体请RTFM《RISC-V第一册》）
#### 具体功能介绍：
- 依旧7个输入：rs1、rs2、rd、WriteData、RegWrite、CLK、Clean
- rs1、rs2理所应当作为两个32-5多路选择器的选择端，选择x0-x31寄存器的输出结果，分别记作ReadData1、ReadData2.
- rd理所应当作为5-32译码器的选择端，32个接口接对应寄存器的写使能。
- 由于我们接的5-32译码器自带使能端，因此RegWrite接这个译码器的使能端控制整个RegisterFile的写使能。
- 剩余的接口是个人都会......
#### 设计图：<img width="1183" height="753" alt="image" src="https://github.com/user-attachments/assets/fed80ae6-472c-4a34-810f-057853ee9d75" />
### 🟡6.算术逻辑单元（ALU）
- **功能简述**：CPU的肌肉。执行所有数学与逻辑相关的运算，至于输出什么结果，利用ALU_Control子模块作多路选择器的选择端实现。
#### 具体功能介绍：
- 输入就是A、B两个输入端口。
- 很简单，就是作10种运算：Add、Sub、AND、OR、XOR、逻辑左移、逻辑右移、算数右移、有符号比较<、无符号比较<，然后选择输出结果。
- 由于后续需要，我们这里再拉三个输出，分别是有符号比较<（LessS）、无符号比较<（LessU）、无符号比较=（Equal）。
#### 设计图：<img width="1201" height="1365" alt="image" src="https://github.com/user-attachments/assets/74f74e83-4a96-4393-b4d8-711cf736c02f" />
### 🟡7.算术逻辑控制单元（ALU_Control）
- 这个不多说，三个输入：ALUOp（后续Main_Control模块根据Opcode生成的控制信号）、funct3、inst_30（32位指令的第30位，其实也就是funct7的区分）
- 然后根据这三个控制信号组合生成ALU内部数据输出（多路选择器）的选择端。
#### 设计图：<img width="1417" height="917" alt="image" src="https://github.com/user-attachments/assets/66f5cf7d-17e6-44f5-884a-8dca06c8a361" />
### 🟡8.主控制器（Main_Control）
- **功能简述**：CPU的中枢神经。负责宏观调控所有数据通路。
#### 具体功能介绍：



