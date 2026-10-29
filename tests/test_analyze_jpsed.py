import tempfile
import unittest
from pathlib import Path

from analyze_jpsed import build_report


class BuildReportTests(unittest.TestCase):
    def test_summarizes_years_and_includes_data_dictionary(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "2020.csv").write_text(
                "年齢,雇用形態,満足度\n20,正社員,1\n30,正社員,2\n,自営業,1\n",
                encoding="utf-8-sig",
            )
            (data_dir / "2021.csv").write_text(
                "職種\n営業\n事務\n営業\n",
                encoding="cp932",
            )
            dictionary = root / "定義書.txt"
            dictionary.write_text("年齢: 満年齢\n雇用形態: 就業形態\n", encoding="cp932")

            report = build_report(
                sorted(data_dir.glob("*.csv")), dictionary, ["満足度"]
            )

            self.assertIn("## 2020.csv", report)
            self.assertIn("- 平均: 25", report)
            self.assertIn("- 欠損値: 1", report)
            self.assertIn("- 正社員: 2", report)
            self.assertIn("### 満足度\n- 欠損値: 0\n- カテゴリ別件数", report)
            self.assertIn("- 1: 2", report)
            self.assertIn("## 2021.csv", report)
            self.assertIn("- 営業: 2", report)
            self.assertIn("## データ定義書（原文）", report)
            self.assertIn("年齢: 満年齢", report)


if __name__ == "__main__":
    unittest.main()
