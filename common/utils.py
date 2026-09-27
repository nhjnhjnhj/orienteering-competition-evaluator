"""
設定ファイルの読み込みやパス取得、
参加者フォルダの探索などの共通処理を提供する。
"""

import json
from pathlib import Path


# プロジェクトルート
BASE_DIR = Path(__file__).resolve().parent.parent


def load_settings():
    """
    config/settings.json を読み込む。
    """

    settings_path = BASE_DIR / "config" / "settings.json"

    with settings_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_path(relative_path):
    """
    プロジェクトルートを基準としたパスを取得する。
    """

    return BASE_DIR / relative_path


def get_participants(submissions_dir):
    """
    submissions直下にある参加者フォルダを取得する。
    """

    submissions_path = get_path(submissions_dir)

    if not submissions_path.exists():
        return []

    # submissions直下のディレクトリだけを参加者として扱う
    participants = [
        path
        for path in submissions_path.iterdir()
        if path.is_dir()
    ]

    # 実行順を一定にするため名前順に並べる
    return sorted(
        participants,
        key=lambda path: path.name,
    )


def ensure_directory(path):
    """
    指定したディレクトリが存在しない場合に作成する。
    """

    Path(path).mkdir(
        parents=True,
        exist_ok=True,
    )