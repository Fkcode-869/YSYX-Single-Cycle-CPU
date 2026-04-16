from PIL import Image
import os


def build_full_color_vga(original_hex, image_path, output_hex):
    print("🚀 启动 32位全彩模式合成 (解决16宫格问题)...")

    # 1. 准备图片：256*256
    img = Image.open(image_path).convert('RGB')
    img = img.resize((256, 256))

    # 2. 生成像素数组：每个像素直接占 32 位 (0x00RRGGBB)
    pixel_words = []
    for r, g, b in img.getdata():
        # RGB888 格式
        pixel_hex = (r << 16) | (g << 8) | b
        pixel_words.append(f"{pixel_hex:08x}")

    # 3. 读取并修改原始 hex
    with open(original_hex, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    target_word_addr = 0x12bc0  # 字节地址 0x4af00 对应的字地址
    end_word_addr = target_word_addr + (256 * 256)  # 连续占用 65536 个字

    found_target = False
    is_replacing = False

    for line in lines:
        line_str = line.strip()
        if not line_str: continue

        if 'v3.0' in line_str:
            new_lines.append(line_str + "\n")
            continue

        if ':' in line_str:
            addr_part = line_str.split(':')[0]
            try:
                current_addr = int(addr_part, 16)
            except:
                new_lines.append(line_str + "\n")
                continue

            # 定位并开始替换
            if current_addr == target_word_addr:
                print(f"✅ 已定位到图片区，正在注入 65536 个全彩像素...")
                found_target = True
                is_replacing = True
                # 写入所有像素，每行 8 个
                for j in range(0, len(pixel_words), 8):
                    addr = target_word_addr + j
                    chunk = pixel_words[j:j + 8]
                    new_lines.append(f"{addr:05x}: {' '.join(chunk)}\n")

            # 如果到达了图片结束地址，停止替换（保留 hex 后面可能存在的其它数据）
            if is_replacing and current_addr >= end_word_addr:
                is_replacing = False

        if not is_replacing:
            new_lines.append(line_str + "\n")

    if not found_target:
        print("❌ 错误：未能在 hex 中定位到 12bc0 处的数据！")
        return

    with open(output_hex, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✨ 镜像合成大功告成！新文件：{output_hex}")


# 执行
build_full_color_vga('vga.hex', 'NewImage.jpg', 'my_full_color_vga.hex')