# JPSED 年次データの統計分析

各年のJPSED（Japan Panel Study of Employment Dynamics）CSVファイルを読み込み、データ定義書（TXT）を参照しながら、列ごとの記述統計を作成するためのPythonツールです。個票データはこのリポジトリに含めず、ローカル環境で分析してください。

## 使い方

Python 3.9以降を用意し、年次CSVを `data/` に、データ定義書を任意の場所に置きます。追加パッケージは不要です。

```text
data/
  jpsed_2020.csv
  jpsed_2021.csv
```

```bash
python analyze_jpsed.py --data-dir data --dictionary path/to/data_definition.txt > report.md
```

スクリプトは `data/` 直下のCSVファイルを年ごとに集計し、レポート末尾にデータ定義書の原文を添付します。UTF-8（BOM付き含む）とCP932のファイルを読み込めます。

データ定義書でカテゴリ変数と確認した列は、数値コードの列もカテゴリ別件数として集計するよう指定できます。

```bash
python analyze_jpsed.py --data-dir data --dictionary path/to/data_definition.txt --categorical-columns employment_status sex > report.md
```

数値として解釈できる列は、有効な数値の件数・平均・中央値・最小値・最大値を出力します。それ以外の列および `--categorical-columns` で指定した列は、上位10カテゴリの件数を出力します。空欄は欠損値として数えます。変数の意味や値コードを解釈するときは、レポートに添付されたデータ定義書と照合してください。これは記述統計の出発点であり、調査設計や重み付けを考慮した推測統計を行う場合は、データ定義書および調査資料に従って別途分析してください。

## テスト

```bash
python -m unittest discover -s tests
```
