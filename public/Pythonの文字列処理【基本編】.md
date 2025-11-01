---
title: Pythonの文字列処理【基本編】
tags:
  - 'Python'
  - 'Tips'
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---
# はじめに

Pythonでは文字列処理が柔軟にできます。
データ分析だけでなく、CSVなどを扱う効率化業務でも文字列処理は活躍すると思います。

というわけで、まずは基本的な文字列の扱いについてまとめていきます。

# 基本編

このパートでは、知っておけば簡単に使える処理をまとめます。

## 文字列の連結 `.join()`

```py
words = ["Hello", "World", "Python"]
result = " ".join(words)
print(result)  # Hello World Python
```

## 大文字・小文字変換 `.upper()`, `.lower()`

```py
text = "Hello World"
print(text.upper())  # HELLO WORLD
print(text.lower())  # hello world
```


## 文字列のトリム `.strip()`

両端の空白を削除する。

```py
text = "  Hello World  "
print(text.strip())   # "Hello World"
```

## 文字列の分割 `.split()`

```py
text = "apple,banana,grape"
items = text.split(",")
print(items)  # ['apple', 'banana', 'grape']
```

## 文字列の検索 `in`, `startswith()`, `endswith()`

```py
text = "Hello World"
print("World" in text)  # True
```

```py
obj = "2025-11-hogehoge.txt"
print(obj.startswith("2025"))  # True
```

```py
obj = "2025-11-hogehoge.txt"
print(obj.endswith(".txt"))  # True
```

## 文字列の置換 `.replace()`

```py
text = "Hello World"
print(text.replace("World", "Python"))  # Hello Python
```

```py
# 空白削除
text = "Hello World"
print(text.replace(" ", ""))  # HelloWorld
```


# 応用編

正規表現を組み合わせるとより柔軟に扱えます。
ここでは、とっつきやすくて使いやすい処理に注目します。

## 文字列の検索 `re.match()`, `re.search()`



```py
import re

text = "Order ID: 12345"
print(re.match(r"Order", text))   # 先頭が一致
print(re.search(r"\d+", text))    # 最初の数字にマッチ
```

- match: 文字列の先頭にマッチするか
- search: 文字列を検索して最初にマッチするか


`<re.Match object; span=(21, 26), match='target'>`のようなオブジェクトが返ってきます。

その文字列が入っているかどうかは、次のように確認できます。
```py
# マッチオブジェクト自体をチェック
if match_obj:  # または if match_obj is not None:
    print(match_obj.group())
```


### 補足

- `r"..."`は正規表現を使う時の文字列パターンに使われる。
- `\d`は数字一文字を表す。
- `+`をつけることで、数字が1回以上続くパターンとして認識する。

基本的な正規表現も表でまとめます。

| パターン | 意味 | 例 |
|---------|------|-----|
| `\d` | 数字（0-9） | `\d+` → "123"にマッチ |
| `\w` | 英数字とアンダースコア | `\w+` → "hello_123"にマッチ |
| `\s` | 空白文字（スペース、タブ、改行） | `\s+` → "   "にマッチ |
| `.` | 任意の1文字 | `a.c` → "abc", "a1c"にマッチ |
| `*` | 0回以上の繰り返し | `ab*c` → "ac", "abc", "abbc"にマッチ |
| `+` | 1回以上の繰り返し | `ab+c` → "abc", "abbc"にマッチ（"ac"は不可） |
| `{n}` | ちょうどn回 | `\d{3}` → "123"にマッチ |
| `{n,m}` | n回以上m回以下 | `\d{2,4}` → "12", "123", "1234"にマッチ |


### `re.match()`と`startswith()`との違い

処理的には似ているのですが、使い所が違うのでまとめます。

| **特徴** | **startswith()** | **re.match()** |
| --- | --- | --- |
| **機能** | **固定文字列**との一致確認 | **正規表現パターン**との一致確認 |
| **柔軟性** | 低い（厳密な文字列の一致） | 高い（ワイルドカード、繰り返しなど） |
| **速度** | **速い**（シンプルで最適化されている） | 遅い（複雑なパターン処理が必要） |
| **モジュール** | Pythonの**組み込み**文字列メソッド | `re`モジュールを**インポート**する必要がある |
| **戻り値** | `True`または`False`（ブール値） | 一致した情報を含む**マッチオブジェクト**（または`None`） |


## 文字列の置換 `re.sub()`

```py
text = "My phone is 090-1234-5678"
masked = re.sub(r"\d", "*", text)
print(masked)  # My phone is ***-****-****
```

## パターンの使い回し

定期的に使うようなパターンを先に用意しておくこともできる。

```py
pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
text_list = ["2024-10-01", "invalid", "2025-01-15"]

for t in text_list:
    if pattern.match(t):
        print("日付形式:", t)
```
