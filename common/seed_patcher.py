"""
const.h内の固定乱数シードを、
環境変数から実行時に指定できる形式へ自動変換する。

提出された元ソースは変更せず、
build_sources側のコピーのみを書き換える。
"""

import re
from pathlib import Path


# 元の固定シード定義を検出する
SEED_PATTERN = re.compile(
    r"constexpr\s+unsigned\s+int\s+"
    r"RANDOM_SEED\s*=\s*\d+\s*;"
)


# 環境変数からシードを取得するコード
SEED_CODE = """inline unsigned int get_random_seed() {
    const char* value = std::getenv("ORIENTEERING_SEED");

    if (value != nullptr) {
        return static_cast<unsigned int>(std::stoul(value));
    }

    return 42;
}

inline const unsigned int RANDOM_SEED = get_random_seed();"""


def patch_random_seed(const_h_path):
    """
    const.hの固定RANDOM_SEEDを、
    実行時に変更できる形式へ置き換える。
    """

    const_h_path = Path(const_h_path)

    if not const_h_path.exists():
        raise FileNotFoundError(
            f"const.hが見つかりません: {const_h_path}"
        )

    # UTF-8 BOM付きファイルにも対応する
    text = const_h_path.read_text(
        encoding="utf-8-sig"
    )

    # RANDOM_SEEDが見つからなければ処理を中止
    if not SEED_PATTERN.search(text):
        raise ValueError(
            "RANDOM_SEEDの定義が見つかりません: "
            f"{const_h_path}"
        )

    # getenvに必要なヘッダを追加
    if "#include <cstdlib>" not in text:
        text = (
            "#include <cstdlib>\n"
            + text
        )

    # stoulに必要なヘッダを追加
    if "#include <string>" not in text:
        text = (
            "#include <string>\n"
            + text
        )

    # 固定シード定義を環境変数対応コードへ置換
    text = SEED_PATTERN.sub(
        SEED_CODE,
        text,
        count=1,
    )

    # build_sources側のconst.hへ保存
    const_h_path.write_text(
        text,
        encoding="utf-8",
    )