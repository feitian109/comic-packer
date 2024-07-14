# comic-packer/漫画打包
A comic packer written in Python for [Mihon](https://mihon.app/)/[Tachiyomi](https://tachiyomi.org/)

一个使用 Python 编写，用于 [Mihon](https://mihon.app/)/[Tachiyomi](https://tachiyomi.org/) 的漫画打包脚本

## Feature/特性
1. 脚本会自动根据漫画的**文件夹名称**解析输出 `ComicInfo.xml`，但是需要确保**漫画的作者名称出现在第一个中括号内**
   
   一个正确✔️的示例：`(某些信息)[作者名] 标题名 [其他信息]`

   一个错误❌的示例：`[某些信息][作者名] 标题名 [其他信息]`
2. 脚本默认会生成漫画封面，如果你不需要，可以将脚本的 `generate_cover` 修改为 `false`

## Usage/使用方法
克隆本项目，进入项目文件夹下，在终端中输入并执行：
```
python comic_packer.py "path\to\FOLDER_STORE_COMICS"
```
其中 `path\to\FOLDER_STORE_COMICS` 应该替换为**存储漫画的文件夹**的路径。同时，`FOLDER_STORE_COMICS` 的目录结构应该如下:
```
FOLDER_STORE_COMICS
  ├─comic_1
  │ ├─image_1.ext
  │ └─image_n.ext
  ├─comic_2
  │ ├─image_1.ext
  │ └─image_n.ext
  └─comic_n
    ├─image_1.ext
    └─image_n.ext
```

运行时，脚本会在 `FOLDER_STORE_COMICS` 下创建 `output` 文件夹，并将打包好的漫画输出到该文件夹下，随后你可以参考 [Mihon | Local source](https://mihon.app/docs/guides/local-source/) 来使用打包好的漫画

## License
This project is licensed under the GNU Gerneral Public License V3.0.
