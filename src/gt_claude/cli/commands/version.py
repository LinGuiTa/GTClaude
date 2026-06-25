from gt_claude import __version__


# 打印 gt CLI 当前版本；返回 0 表示命令执行成功
def run_version() -> int:
    print(f"gt {__version__}")
    return 0
