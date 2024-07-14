import os
import re
import sys
import shutil
import zipfile
import xml.etree.ElementTree as ET

# 生成封面
generate_cover = True

# 生成的章节名称
zip_name = "Chapter 01.zip"

# 默认值，`Series`, `Writer`, `Penciller`, `Genre` 会自动推测
default_info = {
    "Series": "Unknown",
    "Writer": "Unknown",
    "Penciller": "Unknown",
    "Summary": "Unknown",
    "Genre": "Default Genre1, Default Genre2, Default Genre3",
    "Status": 2,
}

# 状态值对应表
status_values = {
    0: "Unknown",
    1: "Ongoing",
    2: "Completed",
    3: "Licensed",
    4: "Publishing finished",
    5: "Cancelled",
    6: "On hiatus",
}

# 用于 xml 生成
url = {
    "XMLSchema": "http://www.w3.org/2001/XMLSchema",
    "XMLSchema_instance": "http://www.w3.org/2001/XMLSchema-instance",
}


# 根据文件夹名推测信息
def analysis(comic_name):
    # 分析 Comic info，拆分成 `parts`
    raw = re.split(r"(\[[^]]+\]|\([^)]+\)|【[^】]+】)", comic_name)
    parts = [item.strip() for item in raw if item not in ["", " "]]

    # 小括号
    parentheses_bracket = [i[1:-1] for i in parts if i[0] == "("]
    # 中括号
    bracket = [i[1:-1] for i in parts if i[0] == "["]
    # 中文括号
    chinese_bracket = [i[1:-1] for i in parts if i[0] == "【"]
    # 标题
    title = [i for i in parts if i[0] not in ["(", "[", "【"]]

    # 生成 `info`
    info = default_info
    info["Series"] = title[0]
    info["Writer"] = bracket.pop(0)
    info["Penciller"] = info["Writer"]
    lst = parentheses_bracket + bracket + chinese_bracket
    info["Genre"] = ", ".join(lst)
    return info


def zip(folder_path, output_path):
    zip_path = os.path.join(output_path, zip_name)
    with zipfile.ZipFile(zip_path, "a") as z:
        pic_names = []
        for file_name in os.listdir(folder_path):
            # 通过扩展名判断文件是否是图片
            if re.search(r"\.(jpg|jpeg|png)$", file_name):
                pic_names.append(file_name)

        # 生成封面
        if generate_cover:
            pic_names.sort()
            shutil.copy(
                os.path.join(folder_path, pic_names[0]),
                os.path.join(output_path, "cover" + os.path.splitext(pic_names[0])[-1]),
            )

        # 写入压缩包
        for pic_name in pic_names:
            pic_path = os.path.join(folder_path, pic_name)
            z.write(pic_path, pic_name)


def generate_info(comic_name, output_path):
    info = analysis(comic_name)
    info_path = os.path.join(output_path, "ComicInfo.xml")

    # 生成 `root`
    root = ET.Element(
        "ComicInfo",
        attrib={
            "xmlns:xsd": url["XMLSchema"],
            "xmlns:xsi": url["XMLSchema_instance"],
        },
    )

    # 生成 `Series`, `Summary`, `Writer`, `Penciller`, `Genre` 信息
    for key in ["Series", "Summary", "Writer", "Penciller", "Genre"]:
        ET.SubElement(root, key).text = info[key]

    # 生成 `Status` 信息
    Status = ET.SubElement(
        root,
        "ty:PublishingStatusTachiyomi",
        attrib={"xmlns:ty": url["XMLSchema"]},
    )
    Status.text = status_values[info["Status"]]

    # 写入 `ComicInfo.xml`
    tree = ET.ElementTree(root)
    tree.write(info_path, encoding="UTF-8", xml_declaration=True)


# 打包
def pack(comic_name, folder_path, output_path):
    print(f"Packing: {folder_path}...", end="")
    zip(folder_path, output_path)
    generate_info(comic_name, output_path)
    print("Done")


if __name__ == "__main__":
    sys.argv.pop(0)
    for arg in sys.argv:
        # 不存在该路径
        if not os.path.exists(arg):
            print(f"Directory '{arg}' not exist")

        # 路径为文件夹时
        elif os.path.isdir(arg):
            for comic_name in os.listdir(arg):  # 遍历文件夹名
                # 跳过输出文件夹
                if comic_name == "output":
                    continue

                folder_path = os.path.join(arg, comic_name)  # 存储漫画的文件夹

                if os.path.isdir(folder_path):
                    output_path = os.path.join(arg, "output", comic_name)  # 输出路径

                    # 如果已存在文件夹
                    if os.path.exists(output_path):
                        print(f"Warning: {output_path} exist, skip...")
                    else:
                        os.makedirs(output_path)
                        pack(comic_name, folder_path, output_path)

        # 路径为文件时
        else:
            print("Error: Not a folder")
