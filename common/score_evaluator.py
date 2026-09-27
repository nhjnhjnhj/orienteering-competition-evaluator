"""
参加者プログラムの出力結果から評価値を取得する。

output/best_course.jsonを読み込み、
fitnessの値を1回の実行における評価値として返す。
"""

import json
from pathlib import Path


def load_fitness(output_dir):
    """
    best_course.jsonからfitnessを取得する。
    """

    output_dir = Path(output_dir)

    result_file = (
        output_dir / "best_course.json"
    )

    # 出力ファイルが生成されているか確認
    if not result_file.exists():
        raise FileNotFoundError(
            "best_course.jsonが見つかりません: "
            f"{result_file}"
        )

    # JSON形式の実行結果を読み込む
    with result_file.open(
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    if "fitness" not in data:
        raise ValueError(
            "fitnessがbest_course.jsonに"
            f"存在しません: {result_file}"
        )

    # CSV集計で利用できるようfloatへ変換
    try:
        return float(
            data["fitness"]
        )

    except (TypeError, ValueError):
        raise ValueError(
            "fitnessが数値ではありません: "
            f"{data['fitness']}"
        )