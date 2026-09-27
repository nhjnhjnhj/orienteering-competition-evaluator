"""
参加者プログラムの実行環境を準備し、C++プログラムを実行する。

入力CSVの配置、出力フォルダの初期化、
乱数シードの設定、処理時間の計測を担当する。
"""

import os
import shutil
import subprocess
import time
from pathlib import Path


def prepare_runtime(
    participant_id,
    executable_path,
    input_data_dir,
    runtime_root,
    input_files,
):
    """
    参加者ごとの実行環境を作成する。
    """

    executable_path = Path(executable_path)
    input_data_dir = Path(input_data_dir)
    runtime_root = Path(runtime_root)

    runtime_dir = (
        runtime_root / participant_id
    )

    runtime_input_dir = (
        runtime_dir / "input"
    )

    runtime_output_dir = (
        runtime_dir / "output"
    )

    # programと同じ階層にinput/outputを用意
    runtime_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    runtime_input_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    runtime_output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Step 1で作った実行ファイルをruntimeへコピー
    runtime_program = (
        runtime_dir / "program"
    )

    shutil.copy2(
        executable_path,
        runtime_program,
    )

    # 公式評価用CSVをinputへコピー
    for file_name in input_files:
        source_file = (
            input_data_dir / file_name
        )

        destination_file = (
            runtime_input_dir / file_name
        )

        if not source_file.exists():
            raise FileNotFoundError(
                "入力ファイルが見つかりません: "
                f"{source_file}"
            )

        shutil.copy2(
            source_file,
            destination_file,
        )

    return runtime_dir


def clear_output_directory(runtime_dir):
    """
    実行前にoutputを空にし、
    前回実行時の結果が残らないようにする。
    """

    runtime_dir = Path(runtime_dir)
    output_dir = runtime_dir / "output"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )


def execute_program(
    runtime_dir,
    timeout_seconds,
    seed=None,
):
    """
    C++プログラムを1回実行し、
    実行状態と処理時間を返す。
    """

    runtime_dir = Path(runtime_dir)

    # 前回の出力結果を削除
    clear_output_directory(
        runtime_dir
    )

    # 現在の環境変数を引き継ぐ
    env = os.environ.copy()

    # 今回の実行で使用する乱数シードを設定
    if seed is not None:
        env["ORIENTEERING_SEED"] = str(seed)

    # C++プログラムの処理時間を計測
    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            ["./program"],
            cwd=runtime_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            env=env,
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        # return codeが0以外なら実行エラー
        if result.returncode != 0:
            return {
                "status": "RUNTIME_ERROR",
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        return {
            "status": "OK",
            "execution_time": execution_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
        }

    # 指定時間を超えた場合はTIMEOUTとして扱う
    except subprocess.TimeoutExpired as e:
        execution_time = (
            time.perf_counter()
            - start_time
        )

        return {
            "status": "TIMEOUT",
            "execution_time": execution_time,
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
            "return_code": None,
        }