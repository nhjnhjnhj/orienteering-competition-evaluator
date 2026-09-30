"""
Step 6: 散布図の生成

final_results.csv を読み込み、
平均処理時間・平均評価値・評価値の標本標準偏差の関係を
散布図として出力する。
"""

import csv

import matplotlib.pyplot as plt
# 日本語フォントを設定
plt.rcParams["font.family"] = "Hiragino Sans"

from common.utils import (
    ensure_directory,
    get_path,
    load_settings,
)


def load_summary(summary_path):
    """
    final_results.csv を読み込み、
    散布図に必要な値を取得する。
    """

    rows = []

    with summary_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append(
                {
                    "participant": row["participant"],
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

    return rows


def create_scatter_plot(
    x_values,
    y_values,
    labels,
    title,
    xlabel,
    ylabel,
    output_path,
):
    """
    指定された値から散布図を1枚生成する。
    """

    plt.figure(
        figsize=(10, 6)
    )

    # 散布図を描画
    plt.scatter(
        x_values,
        y_values,
    )

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # 各点に参加者名を表示
    for x, y, label in zip(
        x_values,
        y_values,
        labels,
    ):
        plt.annotate(
            label,
            (x, y),
            xytext=(5, 5),
            textcoords="offset points",
        )

    # ラベルが切れないよう調整
    plt.tight_layout()

    # PNGとして保存
    plt.savefig(
        output_path,
        dpi=200,
    )

    # 次のグラフへ影響しないよう閉じる
    plt.close()


def main():
    # Step 3 の集計結果を取得
    settings = load_settings()

    results_dir = get_path(
        settings["paths"]["results"]
    )

    summary_path = (
        results_dir / "final_results.csv"
    )

    scatter_dir = (
        results_dir / "scatter_plots"
    )

    ensure_directory(scatter_dir)

    if not summary_path.exists():
        print("final_results.csv が見つかりません。")
        print("先に Step 3 を実行してください。")
        return

    rows = load_summary(summary_path)

    if not rows:
        print("final_results.csv にデータがありません。")
        return

    # 散布図用に各値を取り出す
    participants = [
        row["participant"]
        for row in rows
    ]

    average_scores = [
        row["average_score"]
        for row in rows
    ]

    sd_scores = [
        row["sd_score"]
        for row in rows
    ]

    average_times = [
        row["average_time"]
        for row in rows
    ]

    print("=== Step 6: Scatter Plots ===")
    print()

    # 平均処理時間 × 平均評価値
    create_scatter_plot(
        x_values=average_times,
        y_values=average_scores,
        labels=participants,
        title="平均処理時間と平均評価値の散布図",
        xlabel="平均処理時間 T(Pk) [秒]",
        ylabel="平均評価値 Ave(Pk)",
        output_path=(
            scatter_dir
            / "time_vs_average_score.png"
        ),
    )

    print(
        "Created: time_vs_average_score.png"
    )

    # 平均処理時間 × 評価値の標本標準偏差
    create_scatter_plot(
        x_values=average_times,
        y_values=sd_scores,
        labels=participants,
        title="平均処理時間と評価値の標準偏差の散布図",
        xlabel="平均処理時間 T(Pk) [秒]",
        ylabel="評価値の標準偏差 SD(Pk)",
        output_path=(
            scatter_dir
            / "time_vs_sd_score.png"
        ),
    )

    print(
        "Created: time_vs_sd_score.png"
    )

    # 評価値の標本標準偏差 × 平均評価値
    create_scatter_plot(
        x_values=sd_scores,
        y_values=average_scores,
        labels=participants,
        title="評価値の標準偏差と平均評価値の散布図",
        xlabel="評価値の標準偏差 SD(Pk)",
        ylabel="平均評価値 Ave(Pk)",
        output_path=(
            scatter_dir
            / "sd_score_vs_average_score.png"
        ),
    )

    print(
        "Created: sd_score_vs_average_score.png"
    )

    print()
    print("=== Step 6 Result ===")
    print(
        f"Scatter plots saved: {scatter_dir}"
    )


if __name__ == "__main__":
    main()