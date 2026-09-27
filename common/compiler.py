"""
参加者のC++プログラムをコンパイルする。

MakefileにSOURCESが定義されている場合はその指定を優先し、
指定がない場合は.cppファイルを自動検出して実行ファイルを生成する。
"""

import re
import subprocess
from pathlib import Path


def parse_makefile_sources(makefile_path):
    """
    MakefileのSOURCESからコンパイル対象を取得する。
    """

    makefile_path = Path(makefile_path)

    if not makefile_path.exists():
        return []

    text = makefile_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    # "\" を使った複数行のSOURCES定義を1行へまとめる
    text = re.sub(
        r"\\\s*\n",
        " ",
        text,
    )

    # SOURCES = ... の部分を取得
    match = re.search(
        r"^\s*SOURCES\s*[:?+]?=\s*(.+)$",
        text,
        re.MULTILINE,
    )

    if not match:
        return []

    sources_text = match.group(1)

    # 行末コメントはコンパイル対象から除外
    sources_text = sources_text.split("#", 1)[0]

    return [
        source.strip()
        for source in sources_text.split()
        if source.strip()
    ]


def get_cpp_files(source_dir):
    """
    コンパイル対象となる.cppファイルを決定する。

    MakefileにSOURCESが存在する場合はその指定を使用し、
    存在しない場合は直下の.cppを自動検出する。
    """

    source_dir = Path(source_dir)
    makefile_path = source_dir / "Makefile"

    # まずMakefileのSOURCESを確認
    sources = parse_makefile_sources(
        makefile_path
    )

    if sources:
        cpp_files = []

        for source in sources:
            source_path = source_dir / source

            # .cppのみコンパイル対象にする
            if source_path.suffix != ".cpp":
                continue

            if not source_path.exists():
                raise FileNotFoundError(
                    "MakefileのSOURCESに指定された"
                    f"ファイルが見つかりません: {source}"
                )

            cpp_files.append(source_path)

        return cpp_files, "Makefile SOURCES"

    # SOURCESが利用できない場合は.cppを自動検出
    cpp_files = sorted(
        source_dir.glob("*.cpp")
    )

    return cpp_files, "*.cpp auto-detection"


def compile_cpp_project(
    source_dir,
    output_path,
    compiler_settings,
):
    """
    C++ソース群をコンパイルし、
    参加者ごとに1つの実行ファイルを生成する。
    """

    source_dir = Path(source_dir)
    output_path = Path(output_path)

    # ソースディレクトリの存在確認
    if not source_dir.exists():
        return (
            False,
            f"ソースディレクトリが見つかりません: {source_dir}",
            [],
            "",
        )

    # コンパイル対象を決定
    try:
        cpp_files, detection_method = (
            get_cpp_files(source_dir)
        )

    except FileNotFoundError as e:
        return (
            False,
            str(e),
            [],
            "Makefile SOURCES",
        )

    if not cpp_files:
        return (
            False,
            f".cppファイルが見つかりません: {source_dir}",
            [],
            detection_method,
        )

    # エントリーポイントとなるmain.cppを確認
    main_cpp = source_dir / "main.cpp"

    if not main_cpp.exists():
        return (
            False,
            f"main.cppが見つかりません: {source_dir}",
            [file.name for file in cpp_files],
            detection_method,
        )

    # build/<参加者>/ を作成
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 全参加者を同じコンパイル条件でビルドする
    command = [
        compiler_settings["command"],
        *[str(file) for file in cpp_files],
        f'-std={compiler_settings["standard"]}',
        compiler_settings["optimization"],
        "-o",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

    except FileNotFoundError:
        return (
            False,
            f'{compiler_settings["command"]} が見つかりません。',
            [file.name for file in cpp_files],
            detection_method,
        )

    # コンパイルエラーを呼び出し元へ返す
    if result.returncode != 0:
        return (
            False,
            result.stderr,
            [file.name for file in cpp_files],
            detection_method,
        )

    return (
        True,
        "",
        [file.name for file in cpp_files],
        detection_method,
    )