"""
Step 1: 参加者プログラムのコンパイル

提出ソースをbuild_sourcesへコピーし、
乱数シードを実行時指定できる形式へ変更した後、
参加者ごとに1つの実行ファイルを生成する。
"""

import shutil

from common.compiler import (
    compile_cpp_project,
)
from common.seed_patcher import (
    patch_random_seed,
)
from common.utils import (
    ensure_directory,
    get_participants,
    get_path,
    load_settings,
)


def main():
    # システム設定を読み込む
    settings = load_settings()

    submissions_dir = (
        settings["paths"]["submissions"]
    )

    build_dir = get_path(
        settings["paths"]["build"]
    )

    build_sources_root = get_path(
        settings["paths"]["build_sources"]
    )

    source_dir_name = (
        settings["submission"]["source_dir"]
    )

    # 出力用ディレクトリを準備
    ensure_directory(build_dir)
    ensure_directory(build_sources_root)

    # submissionsから参加者一覧を取得
    participants = get_participants(
        submissions_dir
    )

    if not participants:
        print(
            "参加者フォルダが見つかりません。"
        )
        return

    print(
        "=== Step 1: C++ Compile ==="
    )
    print(
        f"Participants: {len(participants)}"
    )
    print()

    success_count = 0
    error_count = 0

    # 参加者を1人ずつコンパイル
    for index, participant_dir in enumerate(
        participants,
        start=1,
    ):
        participant_id = participant_dir.name

        # GitHubから取得した元ソース
        original_source_dir = (
            participant_dir
            / source_dir_name
        )

        # 書き換え・コンパイル用のコピー
        copied_source_dir = (
            build_sources_root
            / participant_id
            / source_dir_name
        )

        # 最終的な実行ファイル
        output_path = (
            build_dir
            / participant_id
            / "program"
        )

        print(
            f"[{index}/{len(participants)}] "
            f"{participant_id}"
        )

        print(
            f"  Original source: "
            f"{original_source_dir}"
        )

        # 前回のコピーがあれば削除
        if copied_source_dir.exists():
            shutil.rmtree(
                copied_source_dir
            )

        # 元ソースをbuild_sourcesへコピー
        shutil.copytree(
            original_source_dir,
            copied_source_dir,
        )

        print(
            f"  Build source: "
            f"{copied_source_dir}"
        )

        # コピー側のconst.hをseed変更対応へ変換
        const_h_path = (
            copied_source_dir
            / "const.h"
        )

        try:
            patch_random_seed(
                const_h_path
            )

        except Exception as e:
            print("  Seed Patch Error")
            print(f"  {e}")
            error_count += 1
            print()
            continue

        print("  Seed Patch OK")

        # 書き換え後のソースをコンパイル
        (
            success,
            error_message,
            cpp_files,
            detection_method,
        ) = compile_cpp_project(
            copied_source_dir,
            output_path,
            settings["compiler"],
        )

        print(
            f"  Source detection: "
            f"{detection_method}"
        )

        # 実際に使用した.cppを表示
        if cpp_files:
            print("  Compile targets:")

            for cpp_file in cpp_files:
                print(
                    f"    - {cpp_file}"
                )

        if success:
            print("  Compile OK")
            print(
                f"  Output: {output_path}"
            )
            success_count += 1

        else:
            print("  Compile Error")
            print(error_message)
            error_count += 1

        print()

    # 全参加者のコンパイル結果を表示
    print("=== Compile Result ===")
    print(
        f"Success: {success_count}"
    )
    print(
        f"Error  : {error_count}"
    )


if __name__ == "__main__":
    main()