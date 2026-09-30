"""
Step 2b: 参加者ごとの最良実行結果を保存

raw_results.csvから各参加者の最良scoreを記録したrunを取得し、
そのrunと同じ乱数seedでプログラムを再実行する。

生成されたbest_course.jsonなどの出力ファイルを
output/<participant>/へ保存する。
"""

import csv
import shutil

from common.executor import (
    execute_program,
    prepare_runtime,
)
from common.utils import (
    ensure_directory,
    get_path,
    load_settings,
)


def load_best_runs(raw_results_path):
    """
    raw_results.csvから参加者ごとの
    最小scoreとなった実行情報を取得する。
    """

    best_runs = {}

    with raw_results_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:

            # 正常終了したrunだけを対象とする
            if row["status"] != "OK":
                continue

            participant = row["participant"]
            score = float(row["score"])

            # 初回、または現在より良いscoreなら更新
            if (
                participant not in best_runs
                or score < best_runs[participant]["score"]
            ):
                best_runs[participant] = {
                    "run": int(row["run"]),
                    "seed": int(row["seed"]),
                    "score": score,
                }

    return best_runs


def main():

    # 設定ファイルと各種パスを取得
    settings = load_settings()

    build_dir = get_path(
        settings["paths"]["build"]
    )

    input_data_dir = get_path(
        settings["paths"]["input_data"]
    )

    runtime_dir = get_path(
        settings["paths"]["runtime"]
    )

    results_dir = get_path(
        settings["paths"]["results"]
    )

    # 可視化用の結果を保存するoutputフォルダ
    output_dir = get_path("output")

    ensure_directory(output_dir)

    raw_results_path = (
        results_dir
        / "raw_results.csv"
    )

    if not raw_results_path.exists():
        print(
            "raw_results.csv が見つかりません。"
        )
        print(
            "先に Step 2 を実行してください。"
        )
        return

    # 各参加者の最良runを取得
    best_runs = load_best_runs(
        raw_results_path
    )

    if not best_runs:
        print(
            "正常終了した実行結果がありません。"
        )
        return

    print(
        "=== Step 2b: Collect Best Outputs ==="
    )
    print()

    # 各参加者の最良seedでもう一度実行
    for participant, best in sorted(
        best_runs.items()
    ):

        executable_path = (
            build_dir
            / participant
            / "program"
        )

        if not executable_path.exists():
            print(
                f"{participant}: "
                "実行ファイルが見つかりません。"
            )
            continue

        print(participant)
        print(
            f"  Best Run  : {best['run']}"
        )
        print(
            f"  Best Seed : {best['seed']}"
        )
        print(
            f"  Score     : {best['score']:.6f}"
        )

        # program・input・outputからなる実行環境を準備
        participant_runtime_dir = (
            prepare_runtime(
                participant_id=participant,
                executable_path=executable_path,
                input_data_dir=input_data_dir,
                runtime_root=runtime_dir,
                input_files=settings["input_files"],
            )
        )

        # 最良runと同じseedで再実行
        result = execute_program(
            runtime_dir=participant_runtime_dir,
            timeout_seconds=(
                settings["execution"][
                    "timeout_seconds"
                ]
            ),
            seed=best["seed"],
        )

        if result["status"] != "OK":
            print(
                f"  Re-run Error: "
                f"{result['status']}"
            )
            print()
            continue

        runtime_output_dir = (
            participant_runtime_dir
            / "output"
        )

        participant_output_dir = (
            output_dir
            / participant
        )

        # 古い結果があれば削除
        if participant_output_dir.exists():
            shutil.rmtree(
                participant_output_dir
            )

        # C++プログラムが生成したoutputを丸ごと保存
        shutil.copytree(
            runtime_output_dir,
            participant_output_dir,
        )

        print(
            f"  Saved: "
            f"{participant_output_dir}"
        )
        print()

    print(
        "=== Step 2b Result ==="
    )
    print(
        f"Outputs saved: {output_dir}"
    )


if __name__ == "__main__":
    main()