# xiaomicamera-cw500 Video Merger Tool README

## 简介

该程序用于批量合并视频文件，并按指定的时间格式（按天或按月）进行分组。程序根据视频文件的前缀对文件进行分组，并在每个组内根据文件的时间戳进行排序，最后使用 `ffmpeg` 合并视频文件。程序支持删除源文件或重命名源文件，并支持自定义输出文件格式（例如 `mp4`、`mkv`）。

## 功能

1. **按时间分组合并视频**：支持按天或按月对视频文件进行分组。
2. **自定义输出文件格式**：支持指定输出文件的格式（如 `.mp4` 或 `.mkv`）。
3. **处理源文件**：可以选择删除源文件或重命名源文件（将源文件后缀改为 `.old`）。
4. **避免重复合并**：如果输出文件已存在，跳过合并操作。
5. **错误处理**：在处理过程中，如果出现错误，程序会打印错误信息并跳过失败的步骤。

## 依赖

- Python 3.10
- `ffmpeg`：用于合并视频文件。请确保系统中已安装 `ffmpeg`，并且 `ffmpeg` 可通过命令行调用。

  安装 `ffmpeg`：
  - **Windows**: 从 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载并安装，确保 `ffmpeg` 可在命令行中调用。
  - **Linux**: 通过包管理器安装：
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```

## 使用方法

### 1. 配置

在代码中设置以下参数：

- **input_folder**：输入文件夹路径，存放待合并的视频文件。
- **output_folder**：输出文件夹路径，合并后的视频文件将保存到此文件夹。
- **time_format**：输出文件的命名格式。支持的格式有：
  - `%Y-%m-%d`：例如 `2025-01-12`
  - `%Y-%m`：例如 `2025-01`
  - `%d`：例如 `12`（按天命名）
- **merge_by**：指定按天或按月合并：
  - `"day"`：按天合并
  - `"month"`：按月合并
- **delete_source**：是否删除源视频文件。默认为 `False`。
- **rename_source**：是否重命名源视频文件。默认为 `False`。重命名后，文件后缀将变为 `.old`。
- **output_format**：输出文件格式，支持的格式包括 `mp4`、`mkv` 等。默认为 `mp4`。

### 2. 执行合并

修改并配置好以上参数后，直接运行脚本即可执行视频合并。

```python
input_folder = "path_to_input_folder"  # 输入文件夹路径
output_folder = "path_to_output_folder"  # 输出文件夹路径
time_format = "%Y-%m-%d"  # 输出文件命名格式
merge_by = "day"  # 按天或按月合并
delete_source = True  # 是否删除源文件
rename_source = False  # 是否重命名源文件
output_format = "mp4"  # 输出文件格式

merge_videos(input_folder, output_folder, time_format, merge_by, delete_source, rename_source, output_format)
```

### 3. 输出示例

假设你有以下视频文件：
- `00_20250101_120000.mp4`
- `00_20250101_121000.mp4`
- `00_20250101_122000.mp4`

运行脚本后，程序将按时间顺序合并这些文件并生成一个新的合并视频文件，命名为：
```
2025-01-01.mp4
```
该文件将存储在指定的输出文件夹中。如果启用了删除源文件的选项，源视频文件将被删除；如果启用了重命名源文件的选项，源文件的后缀将变为 `.old`。

### 4. 处理视频合并

视频合并过程使用 `ffmpeg` 命令行工具，并且不会重新编码视频文件，以保证合并后的输出文件质量和速度。若文件已存在，则跳过该文件，避免覆盖已存在的视频。

## 程序结构

### 1. `merge_videos` 函数

该函数是程序的核心，负责以下任务：
- 按前缀分组视频文件
- 按时间排序视频文件
- 按天或按月分组视频
- 合并视频文件
- 删除或重命名源文件

### 2. `merge_video_files` 函数

此函数使用 `ffmpeg` 合并视频文件，并生成指定格式的输出文件。

### 3. `get_time_from_filename` 函数

从文件名中提取时间戳。假设时间戳位于文件名的第二部分，并且格式为 `YYYYMMDDHHMMSS`。

### 4. `group_videos_by_prefix` 函数

根据文件名前缀将视频文件分组，通常用于处理同一摄像头或同一设备生成的视频。

### 5. `group_videos_by_time` 函数

根据时间（按天或按月）将视频文件分组。该函数将文件按日期或月度分组，以便对相同时间段的视频进行合并。

### 6. `get_output_filename` 函数

根据提供的时间格式生成合并视频的输出文件名。

## 注意事项

- **视频文件命名规范**：确保视频文件的命名规则符合程序的要求，例如使用时间戳作为文件名的一部分。
- **文件格式支持**：默认情况下，程序假设视频文件为 `.mp4` 格式。如果您的文件格式不同（如 `.avi` 或 `.mov`），请确保程序能够正确识别并处理这些文件。

## 示例

### 配置示例

```python
input_folder = "/path/to/input/videos"
output_folder = "/path/to/output/videos"
time_format = "%Y-%m-%d"
merge_by = "month"
delete_source = True
rename_source = False
output_format = "mkv"

merge_videos(input_folder, output_folder, time_format, merge_by, delete_source, rename_source, output_format)
```

### 执行结果

程序将按照每月一组将输入视频合并为一个新的输出文件，并保存在 `/path/to/output/videos` 目录下，文件命名格式为 `YYYY-MM`（如 `2025-01`）。

## 常见问题

### Q1: 如何修改程序以支持其他格式的视频文件？

您可以在 `merge_videos` 函数中添加对其他格式（如 `.avi`、`.mov` 等）的支持，方法是修改视频文件过滤条件，确保程序能识别不同的文件扩展名。

### Q2: 如何避免删除源文件？

将 `delete_source` 参数设置为 `False`，这样程序就不会删除源文件。

### Q3: 输出格式不能正常工作怎么办？

确保 `ffmpeg` 已正确安装，并且支持所需的视频输出格式（如 `.mkv`）。如果需要转换格式，请检查 `ffmpeg` 是否支持所选格式。

## 许可

该项目的代码基于 MIT 许可证进行分发，您可以自由使用、修改和分发。
