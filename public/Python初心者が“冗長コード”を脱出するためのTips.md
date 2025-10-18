---
title: Python初心者が“冗長コード”を脱出するためのTips
tags:
  - 'Python'
  - '初心者'
  - 'Tips' 
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---
# はじめに

Pythonって初学者からでもとっつきやすいですよね！
その反面、雑にコードを書いても動くということでもあります。

仕事で求められるレベルを考えると
**冗長な書き方やバグを埋め込みやすい書き方は避けたい**ものです、、、

ということで、冗長なコードを避けるための
**"Pythonic"な書き方**をまとめていきます！

知ってればすぐに使えるものばかりなので、
保存して見返してみてください。

## 対象者

- Pythonのコードがなんだか冗長になってしまう
- ある程度プログラムは書けるようになったけど、コードの質を上げたい
- スッキリと見やすいコードを書きたい

# 条件分岐をスッキリ書く

if文が多くなっている、ネストが深くなっている時に使えます！

## 三項演算子代入

条件に応じて代入を1行で書ける構文です。
簡単なif-elseを短く書けて、処理の意図がひと目でわかります。

### コード例

条件がシンプルな時に便利です。

```py
# Before
if score >= 60:
    result = "Pass"
else:
    result = "Fail"
```

```py
# After
result = "Pass" if score >= 60 else "Fail"
```

## 早期リターン

条件を満たさないケースを先にreturnしてしまうことで、
ネストを浅くして可読性を高めます。

### コード例

ネストが深くなりがちな時に早くリターンできないか考えてみるといいですね。

```py
# Before
def process(data):
    if data is not None:
        if len(data) > 0:
            return data[0]
    return None
```

```py
# After
def process(data):
    if not data:
        return None
    return data[0]
```


## inで条件をまとめる

複数の値との比較をorでつなぐよりも、
inを使うことでスッキリと書けます。

### コード例

論理構造をわかりやすくかけるので可読性UPです。

```py
# Before
if status == "open" or status == "ready" or status == "pending":
    handle(status)
```

```py
# After
if status in ("open", "ready", "pending"):
    handle(status)
```


## any(), all()

複数条件をまとめて判定できるビルトイン関数です。
any()は「1つでもTrueならOK」、all()は「すべてTrueならOK」。

### コード例

すべて〇〇な時に、一つでも〇〇ならなどの条件ってしばしば使いますよね。

```py
# Before
if x > 10 or y > 10 or z > 10:
    print("10を超える値があります")
```

```py
# After
if any(v > 10 for v in (x, y, z)):
    print("10を超える値があります")
```

```py
# Before
if x > 0 and y > 0 and z > 0:
    print("すべて正の数です")
```


```py
# After
if all(v > 0 for v in (x, y, z)):
    print("すべて正の数です")
```

# 代入や変数操作をスマートに書く

一時変数が多い、代入が繰り返されている時に使えます！

## アンパック代入

リストやタプルなどの複数要素を**まとめて変数に展開（アンパック）**できる構文です。
for文や関数戻り値を受け取る場面でもよく使われます。

### コード例

```py
# Before
point = (10, 20)
x = point[0]
y = point[1]
```

```py
# After
x, y = (10, 20)
```

<!-- 辞書でも同じように使えます。

```py
fruit = {"apple": 1, "banana": 2}

for key, value in fruit.items():
    print(key, value)
``` -->

## 複数代入

複数の変数に同時に値を代入できる構文です。
一行で初期化や値の入れ替えができ、コードを短くできます。

### コード例

```py
# Before
a = 1
b = 2
c = 3
```

```py
# After
a, b, c = 1, 2, 3
```

応用として、値の入れ替えもできます。

```py
# Before
tmp = a
a = b
b = tmp
```

```py
# After
a, b = b, a
```


# ループ処理をPythonicに書く

for文が長い、indexを手動で設定している時に使えます！

## リスト内包表記

リストを生成するためのfor文を1行で書ける構文です。
可読性を保ちながら、簡潔にデータ変換ができます。

### コード例

```py
# Before
squares = []
for x in range(5):
    squares.append(x**2)
```

```py
# After
squares = [x**2 for x in range(5)]
```

条件分岐にも対応できます。
ただ、条件が複雑になってネストが深くなりそうなら普通のfor文を使った方が読みやすいです。

```py
evens = [x for x in range(10) if x % 2 == 0]
```

## 辞書内包表記

リスト内包表記の辞書版です。
key: value のペアを動的に作りたいときに便利です。

### コード例

構造を変えたり、（key, valueの入れ替え）フィルタリングにも使えます。

```py
# Before
data = {"a": 1, "b": 2, "c": 3, "d": 0}
filtered = {}
for k, v in data.items():
    if v > 0:
        filtered[k] = v
```

```py
# After
filtered = {k: v for k, v in data.items() if v > 0}
```



## enumerate()

forループでインデックスと値を同時に扱える関数です。
手動でrange(len(...))を書くよりも明確で安全です。

### コード例

```py
# Before
items = ["apple", "banana", "cherry"]
for i in range(len(items)):
    print(i, items[i])
```

```py
# After
for i, item in enumerate(items):
    print(i, item)
```


# データアクセスや関数呼び出しを安全・簡潔にする

KeyErrorやTypeErrorを防ぎたい、引数の受け渡しが煩雑な時に使えます！

## dict.get()

辞書のキーを安全に取得するためのメソッドです。
存在しないキーを指定してもエラーにならず、デフォルト値を返します。


### コード例

```py
# Before
user = {"name": "Alice"}
if "age" in user:
    age = user["age"]
else:
    age = 0
```

第2引数でデフォルト値を柔軟に設定できます。

```py
# After
user = {"name": "Alice"}
age = user.get("age", 0)
```


## リスト・辞書のアンパック（*args, **kwargs）

関数の引数を柔軟に扱える構文です。
*argsはタプルとして位置引数を受け取り、
**kwargsは辞書としてキーワード引数を受け取ります。

また、引数を展開して渡すときにも使えます。


### コード例

```py
# Before
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
result = add(nums[0], nums[1], nums[2])
```

```py
# After
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
result = add(*nums)  # アンパックして渡せる
```

```py
# Before
def greet(name, age):
    print(f"{name} is {age} years old.")

params = {"name": "Alice", "age": 25}
greet(params["name"], params["age"])
```

```py
# After
def greet(name, age):
    print(f"{name} is {age} years old.")

params = {"name": "Alice", "age": 25}
greet(**params)  # 辞書を展開して渡せる
```

# 参考

- [Python の三項演算子（条件式）で if 文を一行で書く](https://note.nkmk.me/python-if-conditional-expressions)
- [Python における dict.get() の使い方（辞書操作） — PyCamp／コレクション入門教材](https://pycamp.pycon.jp/textbook/4_collections.html)
- [Python 3 ドキュメント：辞書内包表記および辞書アンパック（**演算子）について](https://docs.python.org/ja/3.11/reference/expressions.html)

