"""
Step 2c: 最良コースの可視化

Step 2bで保存したbest_course.jsonを読み込み、
nodes.csvとedges.csvから道路ネットワークを再構築する。

course_nodes間の最短経路を求め、
参加者ごとのコースをPNG画像として出力する。
"""

import csv
import heapq
import json
import math
import platform

import matplotlib.pyplot as plt

from common.utils import (
    ensure_directory,
    get_path,
    load_settings,
)


# ==========================================
# 日本語フォント設定
# ==========================================

if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "Hiragino Sans"

elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "MS Gothic"

else:
    plt.rcParams["font.family"] = "IPAexGothic"

plt.rcParams["axes.unicode_minus"] = False


def normalize_node_id(value):
    """
    CSVとJSONでnode_idの型が異なっても
    同じIDとして扱えるよう文字列へ統一する。
    """

    value = str(value).strip()

    try:
        number = float(value)

        if number.is_integer():
            return str(int(number))

    except ValueError:
        pass

    return value


def load_nodes(nodes_path):
    """
    nodes.csvから各ノードの緯度・経度を取得する。
    """

    nodes = {}

    with nodes_path.open(
        "r",
        encoding="utf-8-sig",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            node_id = normalize_node_id(
                row["node_id"]
            )

            nodes[node_id] = {
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
            }

    return nodes


def load_edges(edges_path):
    """
    edges.csvから道路ネットワークを構築する。
    """

    graph = {}

    with edges_path.open(
        "r",
        encoding="utf-8-sig",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:

            from_node = normalize_node_id(
                row["from_node"]
            )

            to_node = normalize_node_id(
                row["to_node"]
            )

            length = float(
                row["length_m"]
            )

            graph.setdefault(
                from_node,
                [],
            ).append(
                (
                    to_node,
                    length,
                )
            )

    return graph


def shortest_path(
    graph,
    start,
    goal,
):
    """
    Dijkstra法を用いて、
    startからgoalまでの最短経路を求める。
    """

    start = normalize_node_id(start)
    goal = normalize_node_id(goal)

    queue = [
        (
            0.0,
            start,
        )
    ]

    distances = {
        start: 0.0
    }

    previous = {}

    while queue:

        current_distance, current = (
            heapq.heappop(queue)
        )

        # すでに短い経路が判明している場合は無視
        if (
            current_distance
            > distances.get(
                current,
                math.inf,
            )
        ):
            continue

        # ゴールへ到達
        if current == goal:
            break

        for neighbor, length in graph.get(
            current,
            [],
        ):

            new_distance = (
                current_distance
                + length
            )

            if (
                new_distance
                < distances.get(
                    neighbor,
                    math.inf,
                )
            ):
                distances[neighbor] = (
                    new_distance
                )

                previous[neighbor] = (
                    current
                )

                heapq.heappush(
                    queue,
                    (
                        new_distance,
                        neighbor,
                    ),
                )

    # 経路が存在しない場合
    if goal not in distances:
        return []

    # ゴールから逆順に経路を復元
    path = [goal]

    current = goal

    while current != start:
        current = previous[current]
        path.append(current)

    path.reverse()

    return path


def build_full_route(
    course_nodes,
    graph,
):
    """
    course_nodesの各区間について最短経路を求め、
    1本の完全なルートへ結合する。
    """

    full_route = []

    for index in range(
        len(course_nodes) - 1
    ):

        start = course_nodes[index]
        goal = course_nodes[index + 1]

        segment = shortest_path(
            graph,
            start,
            goal,
        )

        if not segment:
            print(
                "  Warning: "
                f"{start} -> {goal} "
                "の経路が見つかりません。"
            )
            continue

        # 前区間の終点との重複を除いて結合
        if full_route:
            segment = segment[1:]

        full_route.extend(
            segment
        )

    return full_route


def load_best_course(json_path):
    """
    best_course.jsonを読み込む。
    """

    with json_path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def visualize_course(
    participant,
    course,
    nodes,
    graph,
    output_path,
):
    """
    道路ネットワーク・走行ルート・
    コントロール位置を1枚の地図として描画する。
    """

    course_nodes = [
        normalize_node_id(node)
        for node in course["course_nodes"]
    ]

    # 各コントロール間の実際の道路経路を復元
    full_route = build_full_route(
        course_nodes,
        graph,
    )

    fig, ax = plt.subplots(
        figsize=(10, 10)
    )

    # ==========================================
    # 道路ネットワークを背景として描画
    # ==========================================

    for from_node, edges in graph.items():

        if from_node not in nodes:
            continue

        x1 = nodes[from_node]["lon"]
        y1 = nodes[from_node]["lat"]

        for to_node, _ in edges:

            if to_node not in nodes:
                continue

            x2 = nodes[to_node]["lon"]
            y2 = nodes[to_node]["lat"]

            ax.plot(
                [x1, x2],
                [y1, y2],
                linewidth=0.35,
                alpha=0.25,
            )

    # ==========================================
    # 最良コースを描画
    # ==========================================

    route_lons = []
    route_lats = []

    for node_id in full_route:

        if node_id not in nodes:
            continue

        route_lons.append(
            nodes[node_id]["lon"]
        )

        route_lats.append(
            nodes[node_id]["lat"]
        )

    if route_lons:
        ax.plot(
            route_lons,
            route_lats,
            linewidth=2.0,
            label="最良コース",
        )

    # ==========================================
    # スタート・ゴール地点を描画
    # ==========================================

    if course_nodes:

        gate_node = course_nodes[0]

        if gate_node in nodes:

            ax.scatter(
                nodes[gate_node]["lon"],
                nodes[gate_node]["lat"],
                s=100,
                marker="*",
                label="スタート・ゴール",
                zorder=5,
            )

    # ==========================================
    # コントロール地点を描画
    # ==========================================

    controls = course.get(
        "controls",
        [],
    )

    for index, control in enumerate(
        controls,
        start=1,
    ):

        lon = float(
            control["lon"]
        )

        lat = float(
            control["lat"]
        )

        ax.scatter(
            lon,
            lat,
            s=55,
            zorder=5,
        )

        # 訪問順が分かるよう番号を表示
        ax.annotate(
            str(index),
            (lon, lat),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=10,
        )

    # ==========================================
    # グラフ情報
    # ==========================================

    fitness = course.get(
        "fitness",
        "-"
    )

    distance = course.get(
        "total_distance_m",
        "-"
    )

    ax.set_title(
        f"{participant} の最良コース\n"
        f"fitness = {fitness} / "
        f"距離 = {distance} m",
        fontsize=14,
    )

    ax.set_xlabel(
        "経度"
    )

    ax.set_ylabel(
        "緯度"
    )

    ax.legend()

    ax.grid(
        True,
        alpha=0.2,
    )

    # 緯度経度の縦横比が極端にならないよう調整
    ax.set_aspect(
        "equal",
        adjustable="datalim",
    )

    plt.tight_layout()

    # PNGとして保存
    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()


def main():

    settings = load_settings()

    input_data_dir = get_path(
        settings["paths"]["input_data"]
    )

    output_dir = get_path(
        "output"
    )

    maps_dir = (
        output_dir
        / "maps"
    )

    ensure_directory(
        maps_dir
    )

    nodes_path = (
        input_data_dir
        / "nodes.csv"
    )

    edges_path = (
        input_data_dir
        / "edges.csv"
    )

    if not nodes_path.exists():
        print(
            "nodes.csv が見つかりません。"
        )
        return

    if not edges_path.exists():
        print(
            "edges.csv が見つかりません。"
        )
        return

    if not output_dir.exists():
        print(
            "outputフォルダが見つかりません。"
        )
        print(
            "先に Step 2b を実行してください。"
        )
        return

    print(
        "=== Step 2c: Visualize Courses ==="
    )
    print()

    # 道路ネットワークを一度だけ読み込む
    print(
        "道路ネットワークを読み込み中..."
    )

    nodes = load_nodes(
        nodes_path
    )

    graph = load_edges(
        edges_path
    )

    print(
        f"Nodes: {len(nodes)}"
    )

    print()

    # output/<participant>/を順番に処理
    participant_dirs = sorted(
        [
            path
            for path in output_dir.iterdir()
            if path.is_dir()
            and path.name != "maps"
        ],
        key=lambda path: path.name,
    )

    for participant_dir in participant_dirs:

        participant = (
            participant_dir.name
        )

        json_path = (
            participant_dir
            / "best_course.json"
        )

        if not json_path.exists():
            print(
                f"{participant}: "
                "best_course.json "
                "が見つかりません。"
            )
            continue

        print(
            f"{participant}: 描画中..."
        )

        try:
            course = load_best_course(
                json_path
            )

            output_path = (
                maps_dir
                / f"{participant}.png"
            )

            visualize_course(
                participant=participant,
                course=course,
                nodes=nodes,
                graph=graph,
                output_path=output_path,
            )

            print(
                f"  Saved: {output_path}"
            )

        except Exception as e:
            print(
                f"  Error: {e}"
            )

    print()
    print(
        "=== Step 2c Result ==="
    )

    print(
        f"Maps saved: {maps_dir}"
    )


if __name__ == "__main__":
    main()