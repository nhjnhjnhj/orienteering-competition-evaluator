"""
Step 3: 実行結果の統計処理

10回分の結果から参加者ごとの
平均評価値、標本標準偏差、平均処理時間を算出し、
summary.csvへ保存する。
"""

import csv
import statistics
from collections import defaultdict

from common.utils import (
    get_path,
    load_settings,
)


def main():
    # Step 2の結果ファイルを取得
    settings = load_settings()

    results_dir = get_path(
        settings["paths"]["results"]
    )

    raw_results_path = (
        results_dir
        / "raw_results.csv"
    )

    summary_path = (
        results_dir
        / "summary.csv"
    )

    if not raw_results_path.exists():
        print(
            "raw_results.csv が"
            "見つかりません。"
        )
        print(
            "先に Step 2 を実行してください。"
        )
        return

    # 参加者ごとに10回分のデータをまとめる
    participant_results = defaultdict(
        lambda: {
            "scores": [],
            "execution_times": [],
        }
    )

    # 正常終了した結果のみ統計計算の対象にする
    with raw_results_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            participant = (
                row["participant"]
            )

            status = row["status"]

            if status != "OK":
                continue

            score = float(
                row["score"]
            )

            execution_time = float(
                row["execution_time"]
            )

            participant_results[
                participant
            ]["scores"].append(
                score
            )

            participant_results[
                participant
            ]["execution_times"].append(
                execution_time
            )

    summary_rows = []

    print(
        "=== Step 3: Statistics ==="
    )
    print()

    # 参加者ごとにAve・SD・Tを計算
    for participant in sorted(
        participant_results.keys()
    ):
        scores = participant_results[
            participant
        ]["scores"]

        execution_times = (
            participant_results[
                participant
            ]["execution_times"]
        )

        if not scores:
            print(
                f"{participant}: "
                "有効なscoreがありません。"
            )
            continue

        # Ave(Pk)：10回の評価値の平均
        average_score = (
            statistics.mean(scores)
        )

        # SD(Pk)：評価値の標本標準偏差
        if len(scores) >= 2:
            sd_score = (
                statistics.stdev(
                    scores
                )
            )
        else:
            sd_score = 0.0

        # T(Pk)：10回の平均処理時間
        average_time = (
            statistics.mean(
                execution_times
            )
        )

        # summary.csv出力用データ
        summary_rows.append(
            {
                "participant": participant,
                "runs": len(scores),
                "average_score": average_score,
                "sd_score": sd_score,
                "average_time": average_time,
            }
        )

        print(participant)
        print(
            f"  Runs : {len(scores)}"
        )
        print(
            f"  Ave  : {average_score:.6f}"
        )
        print(
            f"  SD   : {sd_score:.6f}"
        )
        print(
            f"  Time : {average_time:.6f}s"
        )
        print()

    # 統計結果をsummary.csvへ保存
    with summary_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "participant",
                "runs",
                "average_score",
                "sd_score",
                "average_time",
            ],
        )

        writer.writeheader()
        writer.writerows(
            summary_rows
        )

    print(
        "=== Step 3 Result ==="
    )
    print(
        f"Results saved: {summary_path}"
    )


if __name__ == "__main__":
    main()