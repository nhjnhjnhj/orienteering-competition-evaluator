"""
Step 5: 評価結果の可視化

final_results.csvを読み込み、
平均評価値・標準偏差・平均処理時間・最終評価値の
グラフをresults/graphsへ出力する。
"""

import csv

import matplotlib.pyplot as plt

from common.utils import (
    ensure_directory,
    get_path,
    load_settings,
)


def load_final_results(
    final_results_path,
):
    """
    final_results.csvを読み込み、
    グラフ作成に必要な値を取得する。
    """

    rows = []

    with final_results_path.open(
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
                    "average_score": float(
                        row["average_score"]
                    ),
                    "sd_score": float(
                        row["sd_score"]
                    ),
                    "average_time": float(
                        row["average_time"]
                    ),
                    "final_score": float(
                        row["final_score"]
                    ),
                }
            )

    return rows


def create_bar_chart(
    participants,
    values,
    title,
    ylabel,
    output_path,
    log_scale=False,
):
    """
    指定された値から棒グラフを1枚生成する。
    """

    plt.figure(
        figsize=(10, 6)
    )

    # 参加者ごとの値を棒グラフとして描画
    plt.bar(
        participants,
        values,
    )

    plt.title(title)
    plt.xlabel("Participant")
    plt.ylabel(ylabel)

    # 桁差が大きい評価値・標準偏差では対数軸を使用
    if log_scale:
        plt.yscale("log")

    # 参加者名が重ならないよう斜め表示
    plt.xticks(
        rotation=45,
        ha="right",
    )

    # ラベルが画像外へ切れないよう調整
    plt.tight_layout()

    # グラフをPNGとして保存
    plt.savefig(
        output_path,
        dpi=200,
    )

    # 次のグラフへ影響しないよう閉じる
    plt.close()


def main():
    # Step 4の最終評価結果を取得
    settings = load_settings()

    results_dir = get_path(
        settings["paths"]["results"]
    )

    final_results_path = (
        results_dir
        / "final_results.csv"
    )

    graphs_dir = (
        results_dir
        / "graphs"
    )

    ensure_directory(
        graphs_dir
    )

    if not final_results_path.exists():
        print(
            "final_results.csv が"
            "見つかりません。"
        )
        print(
            "先に Step 4 を実行してください。"
        )
        return

    rows = load_final_results(
        final_results_path
    )

    if not rows:
        print(
            "final_results.csv に"
            "データがありません。"
        )
        return

    # グラフごとに必要なデータを取り出す
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

    final_scores = [
        row["final_score"]
        for row in rows
    ]

    print(
        "=== Step 5: Visualization ==="
    )
    print()

    # Ave(Pk)：桁差が大きいため対数軸で表示
    create_bar_chart(
        participants=participants,
        values=average_scores,
        title="Average Score",
        ylabel="Ave(Pk)",
        output_path=(
            graphs_dir
            / "average_score.png"
        ),
        log_scale=True,
    )

    print(
        "Created: average_score.png"
    )

    # SD(Pk)：こちらも桁差が大きいため対数軸で表示
    create_bar_chart(
        participants=participants,
        values=sd_scores,
        title="Standard Deviation",
        ylabel="SD(Pk)",
        output_path=(
            graphs_dir
            / "standard_deviation.png"
        ),
        log_scale=True,
    )

    print(
        "Created: standard_deviation.png"
    )

    # T(Pk)：平均処理時間
    create_bar_chart(
        participants=participants,
        values=average_times,
        title="Average Execution Time",
        ylabel="T(Pk) [sec]",
        output_path=(
            graphs_dir
            / "execution_time.png"
        ),
    )

    print(
        "Created: execution_time.png"
    )

    # E(Pk)：コンペの最終評価値
    create_bar_chart(
        participants=participants,
        values=final_scores,
        title="Final Score",
        ylabel="E(Pk)",
        output_path=(
            graphs_dir
            / "final_score.png"
        ),
    )

    print(
        "Created: final_score.png"
    )

    print()
    print(
        "=== Step 5 Result ==="
    )
    print(
        f"Graphs saved: {graphs_dir}"
    )


if __name__ == "__main__":
    main()