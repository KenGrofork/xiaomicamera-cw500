import os
from pathlib import Path
from datetime import datetime
import subprocess

def merge_videos(input_folder, output_folder, time_format="%Y-%m-%d", merge_by="day", delete_source=False, rename_source=False, output_format="mp4"):
    """
    合并视频文件，先按前缀分组，再按天或月分组，并处理源文件（删除或重命名）。
    
    :param input_folder: 输入文件夹路径
    :param output_folder: 输出文件夹路径
    :param time_format: 输出文件命名格式（例如："%Y-%m-%d"）
    :param merge_by: 按天或月分组（"day" 或 "month"）
    :param delete_source: 是否删除源文件，默认为 False
    :param rename_source: 是否重命名源文件，默认为 False
    :param output_format: 输出文件格式（例如："mp4" 或 "mkv"），默认为 "mp4"
    """
    # 创建输出文件夹
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # 获取所有视频文件
    input_path = Path(input_folder)
    video_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() == '.mp4']
    
    # 排除当天的视频文件
    today = datetime.now().date()
    video_files = [f for f in video_files if get_time_from_filename(f.stem).date() != today]

    print(f"排除当天视频后的文件数量: {len(video_files)}")
	
    if not video_files:
        print("没有找到任何非当天的视频文件，退出。")
        return

    print(f"找到的视频文件数量: {len(video_files)}")
    if not video_files:
        print("没有找到任何视频文件，退出。")
        return

    # 按时间排序
    try:
        video_files.sort(key=lambda f: get_time_from_filename(f.stem))
        print("视频文件已按时间排序。")
    except Exception as e:
        print(f"排序视频文件时发生错误: {e}")
        raise

    # 将视频按前缀分组
    groups = group_videos_by_prefix(video_files, input_path)
    print(f"根据前缀分组后的文件数量: {[len(files) for prefix, files in groups.items()]}")

    # 合并每个分组的文件
    for prefix, group_files in groups.items():
        # 生成分组输出文件夹
        group_folder = Path(output_folder) / prefix
        group_folder.mkdir(parents=True, exist_ok=True)

        # 按时间分组
        time_group = group_videos_by_time(group_files, merge_by)

        # 合并每个时间组的视频
        for group_time, files in time_group.items():
            # 创建基于年和月的文件夹
            year_folder = group_time.strftime("%Y")
            month_folder = group_time.strftime("%m")
            output_subpath = group_folder / year_folder / month_folder
            output_subpath.mkdir(parents=True, exist_ok=True)  # 创建年和月的文件夹

            output_filename = get_output_filename(group_time, time_format)
            output_filepath = output_subpath / (output_filename + f".{output_format}")  # 根据输出格式修改扩展名

            # 确保输出路径是有效的文件
            if not output_filepath.exists():  # 确保文件不存在，避免覆盖
                print(f"准备合并的视频文件数量: {len(files)}")
                for file in files:
                    print(f"准备合并的视频文件: {file}")
                print(f"输出文件路径: {output_filepath}")

                merge_video_files(files, output_filepath, output_format)
                print(f"视频文件合并完成: {output_filepath}")
            else:
                print(f"文件已存在，跳过合并: {output_filepath}")

            # 删除源文件或重命名源文件
            if delete_source or rename_source:
                for file in files:
                    try:
                        if delete_source:
                            os.remove(str(file))
                            print(f"已删除源文件: {file}")
                        elif rename_source:
                            new_name = file.with_suffix(file.suffix + ".old")  # 保留原有后缀并添加 .old
                            file.rename(new_name)
                            print(f"源文件后缀已更改为 .old: {file} -> {new_name}")
                    except Exception as e:
                        print(f"处理源文件失败: {file}, 错误: {str(e)}")


def merge_video_files(input_files, output_filepath, output_format):
    """
    使用ffmpeg合并视频文件，尽可能避免重新编码，并指定输出格式
    """
    try:
        # 创建一个临时文件列表，用于ffmpeg合并
        file_list_path = Path('file_list.txt').absolute()
        with open(file_list_path, 'w') as file:
            for input_file in input_files:
                absolute_path = input_file.resolve()  # 获取绝对路径
                file.write(f"file '{absolute_path}'\n")

        # 构建 ffmpeg 命令
        command = [
            'ffmpeg',
            '-y',  # 覆盖输出文件而不询问，放在命令前面
            '-f', 'concat',
            '-safe', '0',
            '-i', str(file_list_path),
            '-c', 'copy',
            str(output_filepath)
        ]

        # 执行 ffmpeg 命令并捕获输出
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("ffmpeg 命令执行成功")
        print("标准输出:", result.stdout.decode())
        print("标准错误:", result.stderr.decode())
        
        # 检查输出文件是否存在，作为成功的额外验证
        if output_filepath.exists():
            print(f"输出文件已成功创建: {output_filepath}")
        else:
            print(f"警告: 输出文件未找到: {output_filepath}")

    except subprocess.CalledProcessError as e:
        print(f"视频合并失败: {e}")
        print("标准输出:", e.stdout.decode())
        print("标准错误:", e.stderr.decode())
        raise
    finally:
        if file_list_path.exists():
            os.remove(file_list_path)  # 删除临时文件


def get_time_from_filename(filename):
    """
    从文件名中提取时间戳（假设时间戳在文件名的第一个和第二个部分之间）
    """
    parts = filename.split('_')
    start_time_str = parts[1] if len(parts) > 1 else None
    if start_time_str is None or len(start_time_str) != 14:
        raise ValueError(f"无法从文件名 {filename} 中解析时间戳")
    return datetime.strptime(start_time_str, "%Y%m%d%H%M%S")


def group_videos_by_prefix(video_files, input_folder):
    """
    根据文件名前缀将视频文件分组
    """
    groups = {}

    for file_path in video_files:
        prefix = file_path.stem.split('_')[0]  # 获取文件名前缀（例如 "00" 或 "10"）
        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(file_path)

    return groups


def group_videos_by_time(video_files, merge_by):
    """
    按天或月将视频文件分组
    """
    groups = {}

    for file_path in video_files:
        timestamp = get_time_from_filename(file_path.stem)
        if merge_by == "day":
            group_key = timestamp.date()  # 使用日期对象作为键，表示每天一组
        elif merge_by == "month":
            group_key = timestamp.replace(day=1).date()  # 将日期设置为每月的第一天，便于按月分组
        else:
            raise ValueError("merge_by must be 'day' or 'month'")

        # 将文件分组
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(file_path)

    return groups


def get_output_filename(group_time, time_format):
    """
    获取合并后的输出文件名
    """
    return group_time.strftime(time_format)


# 用户自定义部分
input_folder = "E4AAECAD635E"  # 输入文件夹
output_folder = "xiaomicamera"  # 输出文件夹
time_format = "%Y-%m-%d"  # 输出文件命名格式（可选：%Y-%m-%d 或 %Y-%m 或 %d）
merge_by = "day"  # "day" 或 "month"，按天或按月合并
delete_source = True  # 是否删除源文件
rename_source = False  # 是否重命名源文件
output_format = "mkv"  # 输出文件格式，默认为 "mp4"，可以设置为 "mkv"

# 调用合并函数
merge_videos(input_folder, output_folder, time_format, merge_by, delete_source, rename_source, output_format)
