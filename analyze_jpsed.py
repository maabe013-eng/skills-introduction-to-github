#!/usr/bin/env python3
"""Create descriptive summaries for yearly JPSED CSV files."""

import argparse
import csv
import math
import statistics
import sys
from collections import Counter
from pathlib import Path


def read_text(path):
    for encoding in ("utf-8-sig", "cp932"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"{path}: UTF-8 or CP932 text could not be decoded")


def summarize_csv(path, categorical_columns=()):
    for encoding in ("utf-8-sig", "cp932"):
        try:
            with path.open(encoding=encoding, newline="") as file:
                return _summarize_reader(path, csv.DictReader(file), categorical_columns)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"{path}: UTF-8 or CP932 CSV could not be decoded")


def _summarize_reader(path, reader, categorical_columns):
    if not reader.fieldnames:
        raise ValueError(f"{path}: CSV has no header row")
    categorical_columns = set(categorical_columns)
    columns = {
        name: {
            "values": None if name in categorical_columns else [],
            "categories": Counter(),
            "missing": 0,
        }
        for name in reader.fieldnames
    }
    row_count = 0
    for row in reader:
        row_count += 1
        for name, summary in columns.items():
            value = (row.get(name) or "").strip()
            if not value:
                summary["missing"] += 1
                continue
            summary["categories"][value] += 1
            try:
                number = float(value)
            except ValueError:
                summary["values"] = None
            else:
                if not math.isfinite(number):
                    summary["values"] = None
                elif summary["values"] is not None:
                    summary["values"].append(number)
    return _format_csv_summary(path, row_count, columns)


def _format_csv_summary(path, row_count, columns):
    lines = [f"## {path.name}", "", f"- 行数: {row_count}", ""]
    for name, summary in columns.items():
        lines.extend((f"### {name}", f"- 欠損値: {summary['missing']}"))
        values = summary["values"]
        if values:
            lines.extend(
                (
                    f"- 数値データ数: {len(values)}",
                    f"- 平均: {statistics.mean(values):.4g}",
                    f"- 中央値: {statistics.median(values):.4g}",
                    f"- 最小値: {min(values):.4g}",
                    f"- 最大値: {max(values):.4g}",
                )
            )
        elif values == []:
            lines.append("- 有効な数値データなし")
        else:
            lines.append("- カテゴリ別件数（上位10件）:")
            categories = summary["categories"].most_common()
            categories.sort(key=lambda item: (-item[1], item[0]))
            lines.extend(f"  - {value}: {count}" for value, count in categories[:10])
        lines.append("")
    return lines


def build_report(csv_paths, dictionary_path, categorical_columns=()):
    dictionary_text = read_text(dictionary_path)
    lines = [
        "# JPSED 年次データの記述統計",
        "",
        "数値列は平均・中央値・最小値・最大値を、その他の列はカテゴリ別件数を示します。",
        "カテゴリ変数として指定した列は、数値コードであってもカテゴリ別件数を示します。",
        "変数名や値コードの解釈には、末尾に添付したデータ定義書を参照してください。",
        "",
    ]
    for path in csv_paths:
        lines.extend(summarize_csv(path, categorical_columns))
    lines.extend(
        (
            "## データ定義書（原文）",
            "",
            f"ファイル: {dictionary_path.name}",
            "",
            dictionary_text.rstrip(),
            "",
        )
    )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="年次JPSED CSVを集計し、データ定義書と一緒にレポートします。"
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument(
        "--categorical-columns",
        nargs="*",
        default=(),
        help="データ定義書を参照してカテゴリ変数の列名を指定",
    )
    args = parser.parse_args(argv)

    csv_paths = sorted(args.data_dir.glob("*.csv"))
    if not csv_paths:
        parser.error(f"{args.data_dir} にCSVファイルがありません")
    if not args.dictionary.is_file():
        parser.error(f"データ定義書が見つかりません: {args.dictionary}")

    try:
        print(build_report(csv_paths, args.dictionary, args.categorical_columns))
    except (OSError, ValueError, csv.Error) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
