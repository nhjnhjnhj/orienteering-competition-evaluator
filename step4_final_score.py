"""
Step 4: 最終評価値の算出

平均評価値・標本標準偏差・平均処理時間を正規化し、
コンペ規定の式に基づいて最終評価値E(Pk)を算出する。
"""

import csv
import math

from common.utils import (
    get_path,
    load_settings,
)


def main():
    # Step 3の集計結果を取得
    settings = load_settings()

    results_dir = get_path(
        settings["paths"]["results"]
    )

    summary_path = (
        results_dir
        / "summary.csv"
    )

    final_results_path = (
        results_dir
        / "final_results.csv"
    )

    if not summary_path.exists():
        print(
            "summary.csv が見つかりません。"
        )
        print(
            "先に Step 3 を実行してください。"
        )
        return

    rows = []

    # CSVの値を計算可能な数値型へ変換
    with summary_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append(
                {
                    "participant": (
                        row["participant"]
                    ),
                    "runs": int(
                        row["runs"]
                    ),
                    "average_score": float(
                        row["average_score"]
                    ),
                    "sd_score": float(
                        row["sd_score"]
                    ),
                    "average_time": float(
                        row["average_time"]
                    ),
                }
            )

    if not rows:
        print(
            "summary.csv に"
            "データがありません。"
        )
        return

    # 式(9)〜(11)で利用する全参加者の最大値
    max_average = max(
        row["average_score"]
        for row in rows
    )

    max_sd = max(
        row["sd_score"]
        for row in rows
    )

    max_time = max(
        row["average_time"]
        for row in rows
    )

    print(
        "=== Step 4: Final Score ==="
    )
    print()

    print(
        f"Max Ave  : {max_average:.6f}"
    )
    print(
        f"Max SD   : {max_sd:.6f}"
    )
    print(
        f"Max Time : {max_time:.6f}s"
    )
    print()

    final_rows = []

    # 各参加者の値を正規化してE(Pk)を算出
    for row in rows:

        # 式(9)：平均評価値を正規化
        normalized_average = (
            row["average_score"]
            / max_average
            if max_average != 0
            else 0.0
        )

        # 式(10)：標準偏差を正規化
        normalized_sd = (
            row["sd_score"]
            / max_sd
            if max_sd != 0
            else 0.0
        )

        # 式(11)：平均処理時間を正規化
        normalized_time = (
            row["average_time"]
            / max_time
            if max_time != 0
            else 0.0
        )

        # 式(12)：3項目から最終評価値E(Pk)を算出
        final_score = math.sqrt(
            normalized_average ** 2
            + normalized_sd ** 2
            + normalized_time ** 2
        )

        final_rows.append(
            {
                "participant": (
                    row["participant"]
                ),
                "runs": row["runs"],
                "average_score": (
                    row["average_score"]
                ),
                "sd_score": (
                    row["sd_score"]
                ),
                "average_time": (
                    row["average_time"]
                ),
                "normalized_average": (
                    normalized_average
                ),
                "normalized_sd": (
                    normalized_sd
                ),
                "normalized_time": (
                    normalized_time
                ),
                "final_score": (
                    final_score
                ),
            }
        )

    # E(Pk)が小さい順に並べる
    final_rows.sort(
        key=lambda row: (
            row["final_score"]
        )
    )

    # 最終結果を順位順に表示
    for rank, row in enumerate(
        final_rows,
        start=1,
    ):
        print(
            f"{rank}. "
            f"{row['participant']}"
        )
        print(
            f"   Ave'  : "
            f"{row['normalized_average']:.6f}"
        )
        print(
            f"   SD'   : "
            f"{row['normalized_sd']:.6f}"
        )
        print(
            f"   Time' : "
            f"{row['normalized_time']:.6f}"
        )
        print(
            f"   E     : "
            f"{row['final_score']:.6f}"
        )
        print()

    # 最終評価結果をCSVへ保存
    with final_results_path.open(
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
                "normalized_average",
                "normalized_sd",
                "normalized_time",
                "final_score",
            ],
        )

        writer.writeheader()
        writer.writerows(
            final_rows
        )

    print(
        "=== Step 4 Result ==="
    )
    print(
        f"Results saved: "
        f"{final_results_path}"
    )


if __name__ == "__main__":
    main()