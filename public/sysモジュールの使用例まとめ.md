---
title: 【一つの例で理解】sysモジュールを実務で使いこなす
tags:
  - 'python'
  - 'tips'
  - 'sys'
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---
# はじめに

Pythonの`sys`モジュールは、スクリプト実行環境を制御するための標準モジュールです。  
「なんとなく `import sys` してるけど、実際いつ使うの？」という方も多いと思います。

本記事では、よく使われる次の4つの機能を、**ひとつの実務ケースでまとめて活用**する方法を紹介します。

- `sys.argv` → コマンドライン引数を取得する  
- `sys.exit()` → プログラムを強制終了する  
- `sys.version` → Pythonのバージョン情報を取得する  
- `sys.path` → モジュールの検索パスを操作する  

# 実務ケース：CSV変換スクリプトをCLIツール化する

## 想定シーン

社内でよくある以下のような処理を自動化したいケースです。

- 日次で届くCSVファイルを指定の文字コード（UTF-8 / Shift-JIS）に変換して保存  
- コマンドラインから「入力ファイル」「出力ファイル」「エンコーディング」を指定できる  
- 社内共通ライブラリ（`csv_tools.py`）を読み込む  
- CI/CDやcronで運用し、失敗時はエラーコードで検知できるようにしたい  


```py
# コード例：convert_csv.py
import sys
import os

# 1. Pythonバージョンチェック
if sys.version_info < (3, 9):
    print("このスクリプトは Python 3.9 以上が必要です。")
    sys.exit(1)

# 2. 共通モジュールのパスを追加
sys.path.append("/usr/local/project/utils")

try:
    from csv_tools import convert_encoding  # 社内共通モジュールを仮定
except ImportError:
    print("共通モジュール(csv_tools)を読み込めませんでした。")
    sys.exit(1)

# 3. コマンドライン引数の確認
if len(sys.argv) != 4:
    print("使い方: python convert_csv.py <入力ファイル> <出力ファイル> <変換先エンコーディング>")
    print("例: python convert_csv.py data/input.csv data/output.csv utf-8")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]
target_encoding = sys.argv[3].lower()

# 4. 引数のバリデーション
if not os.path.exists(input_file):
    print(f"エラー: 入力ファイルが存在しません → {input_file}")
    sys.exit(1)

if target_encoding not in ("utf-8", "shift_jis"):
    print(f"エラー: サポートされていないエンコーディングです → {target_encoding}")
    sys.exit(1)

# ファイル変換処理
try:
    convert_encoding(input_file, output_file, target_encoding)
    print(f"変換完了: {output_file}（→ {target_encoding}）")
except Exception as e:
    print(f"変換中にエラーが発生しました: {e}")
    sys.exit(1)

# 正常終了
print("処理が完了しました。")
sys.exit(0)
```

```bash
# 実行例

# UTF-8に変換して保存
python convert_csv.py data/input.csv data/output_utf8.csv utf-8

# Shift_JISに変換
python convert_csv.py data/input.csv data/output_sjis.csv shift_jis
```

## sysモジュールの実務的な使いどころ

| **sys機能** | **役割** | **実務での意味** | **該当箇所** | 
| --- | --- | --- | --- |
| sys.version_info | Pythonバージョンを確認 | 環境互換性をチェックして安全に実行 |  `1` |
| sys.path | モジュール検索パスの追加 | 共通ライブラリを簡単に読み込む | `2` |
| sys.argv | コマンドライン引数を取得 | CLIスクリプトとして柔軟に使えるようにする | `3`  |
| sys.exit() | 正常／異常終了を制御 | CI/CD・cronでのエラーハンドリング | `4` |


# まとめ

Pythonで自動化スクリプトや定期ジョブを作るとき、
sysモジュールは欠かせない機能です。

- CLI引数を扱う (sys.argv)
- 正常・異常終了を制御する (sys.exit)
- 実行環境を保証する (sys.version_info)
- 共通ライブラリを柔軟に使う (sys.path)

# 参考

- [sysモジュールの使い方](https://qiita.com/Keitachan/items/2da6598faa3d7cff2143)