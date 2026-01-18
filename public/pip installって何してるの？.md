---
title: pip installって何してるの？
tags:
  - 'Python'
  - '初心者'
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: true
---
# はじめに

Pythonでプログラミングをしていると、当たり前のように使っている`pip install`コマンド。
このコマンド一つで、便利なライブラリがすぐに使えるようになります。

しかし、**結局、pipは何をどこにダウンロードして、どうやってPythonがそれを見つけているのか？**を詳しく知っている人は意外と少ないかもしれません。

普段は意識しなくても開発は進められますが、
以下のような場面では内部の仕組みを理解していると役立ちます。

- ライブラリをインストールしたはずなのに`ModuleNotFoundError`が出るというトラブルの解決
- 特定のプロジェクトだけで自作ライブラリを使い回したいときの構成
- 複数のライブラリのバージョン競合（依存関係）で詰まったときの原因究明


この記事では、pip installが内部でどのような処理を行っているのかを、できるだけシンプルに解説します。


```py
# PATHがどこに通っているか確認できる
python -m site

# 仮想環境だと例えば
# apps/.venv/lib/python3.12/site-packages

# $ ls .venv/lib/python3.12/site-packages
numpy			pip
numpy-2.4.1.dist-info	pip-24.0.dist-info
```