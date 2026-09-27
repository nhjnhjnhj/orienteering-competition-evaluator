"""
Step 2: 参加者プログラムの実行

各参加者のプログラムを異なる乱数シードで10回実行し、
評価値・処理時間・実行状態をraw_results.csvへ保存する。
"""

import csv

from common.executor import (
    execute_program,
    prepare_runtime,
)
from common.score_evaluator import (
    load_fitness,
)
from common.utils import (
    ensure_directory,
    get_path,
    load_settings,
)


# 全参加者に共通して使用する10種類の乱数シード
SEEDS = [
    101,
    202,
    303,
    404,
    505,
    606,
    707,
    808,
    909,
    1010,
]


def main():
    # 設定と各種パスを取得
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

    runs = settings["execution"]["runs"]

    timeout_seconds = (
        settings["execution"][
            "timeout_seconds"
        ]
    )

    input_files = settings["input_files"]

    ensure_directory(runtime_dir)
    ensure_directory(results_dir)

    # 使用するseed数を超えていないか確認
    if runs > len(SEEDS):
        print(
            "execution.runs が利用可能な"
            "SEEDS数を超えています。"
        )
        return

    # Step 1で生成されたprogramだけを対象にする
    participants = sorted(
        [
            path
            for path in build_dir.iterdir()
            if path.is_dir()
            and (path / "program").exists()
        ],
        key=lambda path: path.name,
    )

    if not participants:
        print(
            "実行可能な参加者プログラムが"
            "見つかりません。"
        )
        print(
            "先に Step 1 を実行してください。"
        )
        return

    total_runs = (
        len(participants) * runs
    )

    overall_run = 0
    raw_results = []

    print(
        "=== Step 2: Execute Programs ==="
    )
    print(
        f"Participants: {len(participants)}"
    )
    print(
        f"Runs per participant: {runs}"
    )
    print(
        f"Total runs: {total_runs}"
    )
    print()

    # 各参加者を順番に実行
    for participant_index, participant_build_dir in enumerate(
        participants,
        start=1,
    ):
        participant_id = (
            participant_build_dir.name
        )

        executable_path = (
            participant_build_dir
            / "program"
        )

        print(
            f"[Participant "
            f"{participant_index}/"
            f"{len(participants)}] "
            f"{participant_id}"
        )

        # program + input + output の実行環境を作る
        try:
            participant_runtime_dir = (
                prepare_runtime(
                    participant_id=participant_id,
                    executable_path=executable_path,
                    input_data_dir=input_data_dir,
                    runtime_root=runtime_dir,
                    input_files=input_files,
                )
            )

        except Exception as e:
            print(
                f"  Runtime setup error: {e}"
            )
            print()
            continue

        # 同じ参加者を異なるseedで複数回実行
        for run_number in range(
            1,
            runs + 1,
        ):
            overall_run += 1

            seed = SEEDS[
                run_number - 1
            ]

            print(
                f"  Run {run_number}/{runs} "
                f"Seed={seed} "
                f"(Overall "
                f"{overall_run}/{total_runs})",
                end=" ... ",
                flush=True,
            )

            # seedを環境変数として渡してprogramを実行
            result = execute_program(
                runtime_dir=participant_runtime_dir,
                timeout_seconds=timeout_seconds,
                seed=seed,
            )

            score = None

            # 正常終了した場合のみfitnessを取得
            if result["status"] == "OK":
                try:
                    score = load_fitness(
                        participant_runtime_dir
                        / "output"
                    )

                except Exception as e:
                    result["status"] = (
                        "SCORE_ERROR"
                    )
                    result["stderr"] = str(e)

            # 成否にかかわらず全実行結果を保存
            raw_results.append(
                {
                    "participant": participant_id,
                    "run": run_number,
                    "seed": seed,
                    "status": result["status"],
                    "score": score,
                    "execution_time": result[
                        "execution_time"
                    ],
                    "return_code": result[
                        "return_code"
                    ],
                }
            )

            # 実行結果をコンソールへ表示
            if result["status"] == "OK":
                print(
                    f"OK "
                    f"Score={score:.6f} "
                    f"Time="
                    f"{result['execution_time']:.6f}s"
                )

            elif (
                result["status"]
                == "SCORE_ERROR"
            ):
                print(
                    "SCORE ERROR "
                    f"Time="
                    f"{result['execution_time']:.6f}s"
                )
                print(
                    f"    {result['stderr']}"
                )

            elif (
                result["status"]
                == "TIMEOUT"
            ):
                print(
                    "TIMEOUT "
                    f"{result['execution_time']:.6f}s"
                )

            else:
                print(
                    "RUNTIME ERROR "
                    f"{result['execution_time']:.6f}s"
                )

                if result["stderr"]:
                    print("    stderr:")
                    print(result["stderr"])

        print()

    # 全実行結果をraw_results.csvへ保存
    raw_results_path = (
        results_dir
        / "raw_results.csv"
    )

    with raw_results_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "participant",
                "run",
                "seed",
                "status",
                "score",
                "execution_time",
                "return_code",
            ],
        )

        writer.writeheader()
        writer.writerows(
            raw_results
        )

    print("=== Step 2 Result ===")
    print(
        f"Results saved: "
        f"{raw_results_path}"
    )


if __name__ == "__main__":
    main()