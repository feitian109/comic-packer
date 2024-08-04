import re
import sys
import shutil
import zipfile
from pathlib import Path
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
    "Genre": "Unknown",
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
def analysis(comic_name) -> dict:
    # 分析 Comic info，拆分成 `parts`
    splited = re.split(r"(\[[^]]+\]|\([^)]+\)|【[^】]+】)", comic_name)
    parts = []
    for part in splited:
        striped = part.strip()
        if striped:
            parts.append(striped)

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
    if title:
        info["Series"] = title[0]
    else:
        print("Unknown Series...", end="")

    if bracket:
        info["Writer"] = bracket.pop(0)
        info["Penciller"] = info["Writer"]
    else:
        print("Unknown Writer...", end="")

    lst = parentheses_bracket + bracket + chinese_bracket
    if lst:
        info["Genre"] = ", ".join(lst)
    else:
        print("Unknown Genre...", end="")
    return info


def get_pics(comic_path) -> list:
    pic_paths = []
    for file_path in comic_path.iterdir():
        # 通过扩展名判断文件是否是图片
        if re.search(r"\.(jpg|jpeg|png)$", file_path.name):
            pic_paths.append(file_path)
    return pic_paths


def zip(pic_paths: list, output_path: Path):
    zip_path = output_path / zip_name
    with zipfile.ZipFile(zip_path, "a") as z:
        # 写入压缩包
        for pic_path in pic_paths:
            z.write(pic_path, pic_path.name)


def generate_info(comic_path: Path, output_path: Path):
    info = analysis(comic_path.name)
    info_path = output_path / "ComicInfo.xml"

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
def pack(comic_path: Path, output_path: Path):
    print(f"Packing: {comic_path}...", end="")

    pic_paths = get_pics(comic_path)
    # 如果没有获取到图片
    if not pic_paths:
        print("Warning: No pictures found, skip...")
        return

    # 检查输出路径是否存在
    try:
        output_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Warning: Output directory exist, skip...")
        return

    zip(pic_paths, output_path)

    # 生成封面
    if generate_cover:
        pic_paths.sort(key=lambda path: path.name)
        cover_path = pic_paths[0]
        shutil.copy(cover_path, output_path / ("cover" + cover_path.suffix))

    generate_info(comic_path, output_path)
    print("Done")


def main():
    sys.argv.pop(0)
    for arg in sys.argv:
        work_path = Path(arg)

        # 不存在该路径
        if not work_path.exists():
            print(f"Error: Work path not exist")

        # 路径为文件夹时
        elif work_path.is_dir():
            for comic_path in work_path.iterdir():  # 遍历漫画路径
                if comic_path.is_dir():
                    # 跳过输出文件夹
                    if comic_path.name == "output":
                        continue

                    output_path = work_path / "output" / comic_path.name  # 输出路径
                    pack(comic_path, output_path)

        # 路径为文件或其他情况时
        else:
            print("Error: Work path not a folder")


if __name__ == "__main__":
    main()
