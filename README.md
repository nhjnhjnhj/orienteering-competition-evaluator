# Orienteering Evaluator

研究室内の進化計算コンペティションにおいて、参加者が提出したC++プログラムを一括でコンパイル・実行し、評価結果を集計するためのツールです。

各参加者のプログラムを複数回実行し、以下の指標を算出します。

- 平均評価値 `Ave(Pk)`
- 評価値の標本標準偏差 `SD(Pk)`
- 平均処理時間 `T(Pk)`
- 最終評価値 `E(Pk)`

最終結果はCSVおよびグラフとして出力されます。

---

## 処理の流れ

本ツールは5つのStepで構成されています。

```text
Step 1
参加者プログラムをコンパイル
        ↓
build/<participant>/program

Step 2
異なる乱数シードで10回実行
        ↓
results/raw_results.csv

Step 3
平均値・標準偏差・平均処理時間を計算
        ↓
results/summary.csv

Step 4
各値を正規化し、最終評価値を計算
        ↓
results/final_results.csv

Step 5
評価結果をグラフ化
        ↓
results/graphs/
```

---

## ディレクトリ構成

```text
ORIENTEERING-EVALUATOR/
├── common/
│   ├── compiler.py
│   ├── executor.py
│   ├── score_evaluator.py
│   ├── seed_patcher.py
│   └── utils.py
│
├── config/
│   └── settings.json
│
├── input_data/
│   ├── edges.csv
│   ├── landmarks.csv
│   ├── nodes.csv
│   └── seimon.csv
│
├── submissions/
│   └── <participant>/
│       └── lab-competition-2026/
│           ├── main.cpp
│           ├── const.h
│           ├── *.cpp
│           ├── *.h
│           └── Makefile
│
├── build_sources/
├── build/
├── runtime/
├── results/
│   └── graphs/
│
├── step1_compile.py
├── step2_execute.py
├── step3_statistics.py
├── step4_final_score.py
├── step5_visualize.py
│
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## 必要環境

- Python
- uv
- C++17対応コンパイラ
- g++

Pythonの依存関係は `pyproject.toml` で管理します。

初回実行時は以下を実行してください。

```bash
uv sync
```

---

## 評価用入力データ

評価に使用するCSVファイルを `input_data/` に配置します。

```text
input_data/
├── edges.csv
├── landmarks.csv
├── nodes.csv
└── seimon.csv
```

これらのファイルはStep 2実行時に、各参加者専用の実行環境へコピーされます。

---

## 参加者プログラムの配置

参加者ごとに `submissions/` の直下へ参加者プログラム保持用フォルダを作成します。
フォルダ名は結果CSVやグラフにも反映されるので、わかりやすい名前にしてください。

---

# Step 1：コンパイル

以下を実行します。

```bash
uv run python step1_compile.py
```

## 処理内容

Step 1では以下の処理を行います。

1. `submissions/` から参加者一覧を取得
2. 各参加者のソースコードを `build_sources/` へコピー
3. コピーした `const.h` の乱数シード定義を変更
4. コンパイル対象となる `.cpp` ファイルを決定
5. C++プログラムをコンパイル
6. `build/<participant>/program` を生成

提出された元ソースコードは変更しません。

---

## 乱数シードの変更

参加者プログラムの `const.h` には、以下のような固定シードが定義されていることを想定しています。

```cpp
constexpr unsigned int RANDOM_SEED = 42;
```

Step 1では `build_sources/` にコピーしたファイルのみを書き換え、実行時に環境変数からシードを取得できる形式へ変更します。

そのため、同じ実行ファイルを使用しながら、Step 2で実行ごとに異なる乱数シードを設定できます。

---

## コンパイル対象の決定

Makefileに `SOURCES` が定義されている場合は、その内容を優先します。

例：

```makefile
SOURCES = csv_loader.cpp graph.cpp evaluate.cpp ga.cpp main.cpp
```

これにより、バックアップ用の `.cpp` ファイルなどを誤ってコンパイルすることを防ぎます。

Makefileに利用可能な `SOURCES` が存在しない場合は、対象ディレクトリ直下の `.cpp` ファイルを自動検出します。

---

# Step 2：プログラム実行

以下を実行します。

```bash
uv run python step2_execute.py
```

Step 1で生成した各参加者の実行ファイルを複数回実行します。

---

## 実行環境

参加者ごとに以下の実行環境を作成します。

```text
runtime/
└── <participant>/
    ├── program
    ├── input/
    │   ├── edges.csv
    │   ├── landmarks.csv
    │   ├── nodes.csv
    │   └── seimon.csv
    └── output/
```

C++プログラムはこのディレクトリをカレントディレクトリとして実行されます。

そのため、参加者プログラム側では以下のような相対パスをそのまま利用できます。

```cpp
inline const std::string DATA_DIR = "input";
inline const std::string OUTPUT_DIR = "output";
```

---

## 乱数シード

各参加者は同じ10種類の乱数シードを使用します。

```text
Run 1  : 101
Run 2  : 202
Run 3  : 303
Run 4  : 404
Run 5  : 505
Run 6  : 606
Run 7  : 707
Run 8  : 808
Run 9  : 909
Run 10 : 1010
```

シードは環境変数

```text
ORIENTEERING_SEED
```

としてC++プログラムへ渡されます。

全参加者に同じシードを使用することで、評価条件を統一します。

---

## 出力結果の取得

各実行終了後、

```text
output/best_course.json
```

を読み込みます。

その中の

```json
"fitness": 0.123456
```

を、その実行回の評価値として取得します。

---

## raw_results.csv

各実行結果は以下へ保存されます。

```text
results/raw_results.csv
```

主な項目は以下です。

```text
participant
run
seed
status
score
execution_time
return_code
```

例：

```csv
participant,run,seed,status,score,execution_time,return_code
H_A,1,101,OK,0.016354,0.298066709,0
H_A,2,202,OK,0.168910,0.297799499,0
```

---

## 実行ステータス

### OK

プログラムが正常終了し、評価値を取得できた状態です。

### TIMEOUT

設定された制限時間内にプログラムが終了しなかった状態です。

### RUNTIME_ERROR

C++プログラムが異常終了した状態です。

### SCORE_ERROR

プログラム自体は正常終了したものの、`best_course.json` から評価値を取得できなかった状態です。

---

# Step 3：統計値の計算

以下を実行します。

```bash
uv run python step3_statistics.py
```

Step 2で生成された `raw_results.csv` から、参加者ごとに以下の3つの値を計算します。

---

## 平均評価値

10回分の評価値の平均を計算します。

```text
Ave(Pk)
```

---

## 標本標準偏差

10回分の評価値のばらつきを計算します。

```text
SD(Pk)
```

標準偏差には標本標準偏差を使用し、Pythonの

```python
statistics.stdev()
```

で計算します。

---

## 平均処理時間

10回分の実行時間の平均を計算します。

```text
T(Pk)
```

---

## summary.csv

計算結果は以下へ保存されます。

```text
results/summary.csv
```

主な項目は以下です。

```text
participant
runs
average_score
sd_score
average_time
```

本番評価時は、全参加者の `runs` が `10` になっていることを確認してください。

---

# Step 4：最終評価値の計算

以下を実行します。

```bash
uv run python step4_final_score.py
```

Step 3で計算した

```text
Ave(Pk)
SD(Pk)
T(Pk)
```

を正規化し、最終評価値 `E(Pk)` を計算します。

---

## 正規化

各値を全参加者の最大値で割ります。

平均評価値：

```text
Ave'(Pk) = Ave(Pk) / max(Ave)
```

標準偏差：

```text
SD'(Pk) = SD(Pk) / max(SD)
```

平均処理時間：

```text
T'(Pk) = T(Pk) / max(T)
```

---

## 最終評価値

正規化した3つの値から、以下の式で最終評価値を算出します。

```text
E(Pk) = √(
    Ave'(Pk)^2
    + SD'(Pk)^2
    + T'(Pk)^2
)
```

`E(Pk)` が小さいほど良い評価となります。

---

## final_results.csv

最終結果は以下へ保存されます。

```text
results/final_results.csv
```

主な項目は以下です。

```text
participant
runs
average_score
sd_score
average_time
normalized_average
normalized_sd
normalized_time
final_score
```

結果は `final_score` の小さい順に並びます。

---

# Step 5：グラフ生成

以下を実行します。

```bash
uv run python step5_visualize.py
```

Step 4で生成された `final_results.csv` を読み込み、評価結果をグラフとして出力します。

---

## 出力グラフ

```text
results/graphs/
├── average_score.png
├── standard_deviation.png
├── execution_time.png
└── final_score.png
```

### average_score.png

平均評価値 `Ave(Pk)` を表示します。

参加者ごとの値の桁差が大きいため、Y軸には対数スケールを使用します。

### standard_deviation.png

標本標準偏差 `SD(Pk)` を表示します。

こちらも値の桁差が大きいため、Y軸には対数スケールを使用します。

### execution_time.png

平均処理時間 `T(Pk)` を表示します。

### final_score.png

最終評価値 `E(Pk)` を表示します。

値が小さいほど良い評価です。

---

# 実行手順まとめ

基本的には以下を順番に実行します。

```bash
uv sync

uv run python step1_compile.py
uv run python step2_execute.py
uv run python step3_statistics.py
uv run python step4_final_score.py
uv run python step5_visualize.py
```

---

# 設定ファイル

実行回数やタイムアウト時間、各ディレクトリのパスなどは

```text
config/settings.json
```

で管理します。

例：

```json
{
  "compiler": {
    "command": "g++",
    "standard": "c++17",
    "optimization": "-O2"
  },
  "execution": {
    "runs": 10,
    "timeout_seconds": 60
  },
  "statistics": {
    "use_sample_sd": true
  },
  "paths": {
    "submissions": "submissions",
    "build_sources": "build_sources",
    "input_data": "input_data",
    "build": "build",
    "runtime": "runtime",
    "results": "results"
  },
  "submission": {
    "source_dir": "lab-competition-2026"
  },
  "input_files": [
    "edges.csv",
    "landmarks.csv",
    "nodes.csv",
    "seimon.csv"
  ]
}
```

---

# Git管理について

参加者の提出プログラムや評価用データはGitHubへアップロードしないよう、`.gitignore` で除外します。

主な除外対象は以下です。

```text
submissions/
input_data/
build_sources/
build/
runtime/
results/
```

特に以下の2つは外部公開しないことを想定しています。

```text
submissions/
input_data/
```

- `submissions/`：参加者の提出プログラム
- `input_data/`：コンペティションの評価用入力データ

---

# 注意事項

- 参加者の元ソースコードは `submissions/` 内では変更しません。
- シード変更処理は `build_sources/` にコピーしたソースのみを対象とします。
- 参加者プログラムを変更した場合は、Step 1から再実行してください。
- 本番評価では `runs = 10` を使用してください。
- Step 3実行後は、全参加者の実行回数が10回になっていることを確認してください。
- Step 2でエラーが発生した場合は、`raw_results.csv` の `status` を確認してください。
- `E(Pk)` は小さいほど良い評価です。