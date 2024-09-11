import sys
import shutil
import zipfile
from pathlib import Path
import xml.etree.ElementTree as et

# 生成封面
GENERATE_COVER = True

# 生成的章节名称
ZIP_NAME = "Chapter01.zip"

# 默认值，`Series`, `Writer`, `Penciller`, `Genre` 会自动推测
DEFAULT_INFO = {
    "Series": "Unknown",
    "Writer": "Unknown",
    "Penciller": "Unknown",
    "Summary": "Unknown",
    "Genre": "Unknown",
    "Status": 2,
}

# 状态值对应表
STATUS_VALUES = {
    0: "Unknown",
    1: "Ongoing",
    2: "Completed",
    3: "Licensed",
    4: "Publishing finished",
    5: "Cancelled",
    6: "On hiatus",
}

# 漫画图片扩展名，扩展名不在列表中的文件将会被过滤掉
PIC_SUFFIXS = [".jpg", ".jpeg", ".png"]

# 用于 info 生成
XML_URLS = {
    "XMLSchema": "http://www.w3.org/2001/XMLSchema",
    "XMLSchema_instance": "http://www.w3.org/2001/XMLSchema-instance",
}


def parse(comic_name: str) -> dict:
    """Guess comic's info based on the comic_name."""

    part = ""
    previous_char = None

    parentheses_bracket = []
    bracket = []
    chinese_bracket = []
    title = []

    bracket_contents = {"(": parentheses_bracket, "[": bracket, "【": chinese_bracket}
    bracket_pair = {"(": ")", "[": "]", "【": "】"}

    for c in comic_name:
        if previous_char is None and c in bracket_pair.keys():
            # 开始一个新括号对
            if part.strip():
                title.append(part.strip())
            part = ""
            previous_char = c

        elif previous_char is not None and c == bracket_pair[previous_char]:
            # 结束当前的括号对
            if part.strip():
                bracket_contents[previous_char].append(part.strip())
            part = ""
            previous_char = None

        else:
            part += c

    if part.strip():
        title.append(part.strip())

    # 生成 `info`
    info = DEFAULT_INFO
    # 如果找到标题
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


def get_pics(comic_path: Path) -> list:
    """Get comic picture's paths."""

    pic_paths = []
    for file_path in comic_path.iterdir():
        # 通过扩展名判断文件是否是图片
        if file_path.suffix in PIC_SUFFIXS:
            pic_paths.append(file_path)
    return pic_paths


def compress_pics(pic_paths: list, output_path: Path):
    """Compress pictures into a zip file according to a list containing picture paths."""

    zip_path = output_path / ZIP_NAME
    with zipfile.ZipFile(zip_path, "a") as z:
        # 写入压缩包
        for pic_path in pic_paths:
            z.write(pic_path, pic_path.name)


def generate_info(comic_path: Path, output_path: Path):
    """Generate `ComicInfo.xml`."""

    info = parse(comic_path.name)
    info_path = output_path / "ComicInfo.xml"

    # 生成 `root`
    root = et.Element(
        "ComicInfo",
        attrib={
            "xmlns:xsd": XML_URLS["XMLSchema"],
            "xmlns:xsi": XML_URLS["XMLSchema_instance"],
        },
    )

    # 生成 `Series`, `Summary`, `Writer`, `Penciller`, `Genre` 信息
    for key in ["Series", "Summary", "Writer", "Penciller", "Genre"]:
        et.SubElement(root, key).text = info[key]

    # 生成 `Status` 信息
    status = et.SubElement(
        root,
        "ty:PublishingStatusTachiyomi",
        attrib={"xmlns:ty": XML_URLS["XMLSchema"]},
    )
    status.text = STATUS_VALUES[info["Status"]]

    # 写入 `ComicInfo.xml`
    tree = et.ElementTree(root)
    tree.write(info_path, encoding="UTF-8", xml_declaration=True)


# 打包
def pack(comic_path: Path, output_path: Path) -> bool:
    """Call a series of functions to pack comic."""

    print(f"Packing: {comic_path}...", end="")

    # 检查输出路径是否存在
    try:
        output_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Warning: Output directory exist, skip")
        return False

    pic_paths = get_pics(comic_path)
    # 如果没有获取到图片
    if not pic_paths:
        print("Warning: No pictures found, skip")
        return False

    compress_pics(pic_paths, output_path)

    # 生成封面
    if GENERATE_COVER:
        pic_paths.sort(key=lambda path: path.name)
        cover_path = pic_paths[0]
        shutil.copy(cover_path, output_path / ("cover" + cover_path.suffix))

    generate_info(comic_path, output_path)
    print("Done")
    return True


def main():
    """Main entrance of this script. Resolve args passed in."""

    sys.argv.pop(0)
    for arg in sys.argv:
        work_path = Path(arg)

        # 不存在该路径
        if not work_path.exists():
            print("Error: Work path not exist")

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
