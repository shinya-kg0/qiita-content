---
title: Pythonで継承を最小化する設計：Mixin・委譲・プロトコルの使い分け
tags:
  - 'Python'
  - '継承'
  - 'オブジェクト指向'
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---
# はじめに

[達人プログラマー](https://www.ohmsha.co.jp/book/9784274226298/)という本を読んでいて、
**継承は避けた方がいい**という内容を見つけました。

> オブジェクト指向言語でプログラムを開発しているのでしょうか？そうであれば、インケリタンス（継承）を使っているのでしょうか？
> 答えがイエスなのであれば、今すぐ手を止めてください！これはおそらくあなたがやりたいことと思っていることではありません。
>
> 引用：[達人プログラマー](https://www.ohmsha.co.jp/book/9784274226298/)

私はPythonをメインに使っているので、継承という概念は知っていますが、
落とし穴や代替方法についてはよく知らなかったのでまとめました。

仕事の中で、継承の選択肢が出てきた時に思い返すと、
潜在的なバグを防げるかもしれません、、、

## 対象者

- オブジェクト指向言語を扱っていて、なんとなく継承という概念を知っている。
- 継承関連のバグに遭遇したことがある。

# 継承とは？

ざっくり説明すると、基本的な機能を引き継ぎ、新たな機能を追加したり、
既存の機能を書き換えることができる仕組みです！

具体例についてはこちらの記事がわかりやすかったので、おすすめです。
→ [初学者のためのPython講座　オブジェクト指向編5　クラスの継承](https://qiita.com/kotakahe/items/b678250389af7fa885a5)

コードの再利用ができたり、クラスの柔軟性が上がるというメリットがあって、
便利そうですが、何が問題なのでしょうか？？

## 継承のデメリット

考えられるデメリットを並べてみます。

1. 親クラスの変更が子クラスに思わぬ影響を与える
→ 親クラスに定義していた共通処理を変更する時、それを継承している子クラスに影響を与える可能性がある。

2. 不要な機能も引き継いでしまう
→ 子クラスが親クラスのメソッドを使わないとしても、インターフェースとして残ってしまう。

3. 継承階層が深くなって複雑になる
→ 親の親クラスの定義をみにいく必要があるなど、理解が難しくなる

4. 多重継承のあいまいさ
→ 複数の親クラスを継承していると、どの親クラスのメソッドか分かりづらくなる  
（多重継承については、メソッド解決順序（MRO）の概念の理解が必要です。）
 [「Pythonのメソッド順序解決を理解する」](https://qiita.com/y518gaku/items/7c00afb1e887ed449788)がわかりやすかったです。


具体例で考えてみましょう。
次のように定義してみます。

```py
class Animal:
  def __init__(self, name):
    self.name = name

  def speak(self):
    print(f"{self.name} は鳴きます！")

class Dog(Animal):
  def speak(self):
    print("ワンワン！")
```

出力は以下のようになります。

```py
dog = Dog("ポチ")
dog.speak()
# => ワンワン！
```

ここで、親クラスの定義を変えてみましょう。

```py
class Animal:
  def __init__(self, name):
    self.name = name

  def speak(self, sound):
    # 鳴き声もしていできるようにする
    print(f"{self.name} は{sound}と鳴きます！")

class Dog(Animal):
  def speak(self):
    print("ワンワン！")
```

この呼び出し方だと、親クラスの定義変更が子クラスに伝わってません（期待通り反映されてない）。
想定外の動きになるので、潜在的にバグになっています。

```py
dog = Dog("ポチ")
dog.speak()
# => ワンワン！
```

次に、引数を与えてみるとどうでしょうか？

```py
dog = Dog("ポチ")
dog.speak("ワン")  
# => TypeError: Dog.speak() takes 1 positional argument but 2 were given
```

子クラスのspeakメソッドが呼び出されるため、
引数の数が異なりエラーになります。

これぐらいシンプルな例だと、「さすがにそんなことしないよ、、、」となると思いますが、
コードが大きくなってくると、なかなか気づかない可能性も出てきます。


# 継承を避けるためには？

継承は絶対に使わないほうがいいというわけではなく、
バグを埋め込む可能性があるなら、もっと他のシンプルな方法で代替できる方を選ぶとよいと考えるといいですね。

代替手段として、次の3つがあります。

- Mixin
- 委譲
- プロトコル

書籍ではそれぞれの具体例が少なかったので、
Pythonで書くとどうなるかを考えてみます！

## Mixin

Mixinとは、、、

- ある機能を付け足すための”補助的なクラス”
- それ自体は主役ではなく、他のクラスに「機能を混ぜ込む」ための補助モジュール
- 小さい単位の責務で、一つの機能を提供する
- 単独でインスタンス化されないことを前提とする

→ シンプルな機能をちょっとだけ追加したい時に有効です！

### 具体例

ログを出すためのMixinを考えてみます。

```py
# ログ出力機能を提供する Mixin
class LoggingMixin:
    def log(self, msg: str):
        print(f"[LOG] {msg}")

# 機能を持つクラス（例えば、処理をするクラス）
class Worker:
    def work(self):
        print("作業中…")

# Worker にログ能力を付け加える
class LoggingWorker(LoggingMixin, Worker):
    def work(self):
        self.log("開始")
        super().work()
        self.log("終了")

lw = LoggingWorker()
lw.work()
# 出力例：
# [LOG] 開始
# 作業中…
# [LOG] 終了
```

LoggingMixin は**ログ機能を提供する部品**であり、
主要な機能とは分離して、ログ機能を再利用できる形になっていますね。

よく使うちょっとした処理をMixinとしてまとめておけば、
継承の影響を考えず、シンプルに管理できそうです！

### is-aとhas-a

オブジェクト指向では、クラス関係を表すときに
`is-a（〜は〜である）`と`has-a（〜を持っている）`という関係性があります。

例えば、

- **is-a 関係**：継承を使う典型的なケース。「犬は動物である」「四角形は図形である」など。  
- **has-a 関係**：あるオブジェクトが別のオブジェクトや機能を所有している、またはその能力を備えているという意味合い。

Mixin を使うときは、is-aの関係というより、
**“このクラスはこの能力を持っている（has-X）”** を意識した設計になります。  

この辺りの関係を意識して、クラス設計をしていきたいですね。


## 委譲

委譲とは、、、

- あるオブジェクトが、自分自身で処理を実装するのではなく、別のオブジェクトにその処理を任せる
- 「この機能は別のオブジェクトにやってもらおう」というイメージ
- クラス間の結合をゆるく保ちつつ、機能の分離や入れ替えがしやすい

→ 使いたい機能を別の人（オブジェクト）にお願いしている感じです！
　機能を分離したい時や、挙動の動的切り替えの時に有効です！

### 具体例

Mixinと同じく、ログを出すときの具体例を考えます。

```py
class Logger:
    def log(self, msg: str):
        print(f"[LOG] {msg}")

class Worker:
    def work(self):
        print("仕事中…")

class DelegatingWorker:
    def __init__(self, logger: Logger):
        self._logger = logger  # 委譲先オブジェクトを持つ

    def work(self):
        # 委譲先のメソッドを呼び出す
        self._logger.log("開始")
        print("仕事中…")
        self._logger.log("終了")

logger = Logger()
dw = DelegatingWorker(logger)
dw.work()
# 出力:
# [LOG] 開始
# 仕事中…
# [LOG] 終了
```

Loggerクラスをインスタンス化し、
そのオブジェクトを渡すことでログ出力機能を追加しています。

言い換えると、**ログ出力の処理をLoggerクラスに任せています。**

このような設計にしておくと、いざLoggerクラスを変更する時にも、
結合度が低いので変更しやすくなるというメリットがありますね！


## プロトコル

プロトコルとは、、、

- 継承は不要で、「このメソッドを持っていれば、この型とみなす」という仕組み
- 実装を継承する手段ではなく、型（どういう振る舞いをする？）を表す手段
- 「このクラスを名乗るなら、Aというメソッドは準備しておいてね」という約束

→ これまでは、機能を実際に入れ込む感じでしたが、プロトコルは〇〇メソッドを定義してねという約束なので使いやすいと思います！

### 具体例

具体例として、Protocolを使ったものはこちらがわかりやすいです。
→ [PythonでProtocolを使って静的ダック・タイピング](https://qiita.com/spicy_laichi/items/29ef79eac29d61fcb503)

同じ例を使って、抽象基底クラス（ABC）で書いた時の例を見てみます。

```py
from abc import ABC, abstractmethod

# 抽象基底クラス
class Animal(ABC):
    # sound()が抽象メソッドであることを宣言
    @abstractmethod
    def sound(self) -> str:
        # 抽象メソッドには具体的な実装は書かない
        pass

class Dog(Animal):
    # Animalを継承し、soundが実装されている
    def sound(self) -> str:
        return "Bow-wow"

class Book(Animal): # Animalを継承
    # Animalを継承したが、soundが実装されていない
    def read(self) -> str:
        return "hogeeee"

class Cat(Animal):
    # Animalを継承し、soundは実装されているが、戻り値が違う
    # 抽象クラスの要求(-> str)とは異なる戻り値(-> None)
    def sound(self) -> None: 
        print("Meow")
```

出力を見てみます。

```py
dog = Dog()
dog_sound = dog.sound()
print(dog_sound)

# 出力:
# Bow-wow

book = Book()
book.sound()

# 出力:
# TypeError: Can't instantiate abstract class Book without an implementation for abstract method 'sound'

cat = Cat()
cat.sound()

# 出力:
# Meow
# 本当は静的解析時にエラーが出ます
```

Bookクラスをインスタンス化しようとした時には、
soundメソッドを定義していないため、TypeErrorが発生します。

Catクラスはインスタンス化はできますが、
Mypyなどの型チェッカーに引っ掛かります。

このように、プロトコルを使うことで、継承でオーバーライドしなくても
必要なメソッドを定義し、結合度を下げ、型安全なコードになります！

# まとめ

最後にどういう場面で使った方がいいかも大事なので整理していきます。

| **手法** | **メリット** | **デメリット** | **使うべき場面** |
| --- | --- | --- | --- |
| **継承** | ・親の機能をそのまま使える <br>・共通処理をまとめやすい | ・親の変更で子が壊れやすい <br>・不要機能も引き継ぐ <br>・階層が深くなりすぎる | ・“〜は〜である” の関係が自然なとき <br>・基本インターフェースをまとめたいとき |
| **Mixin** | ・共通の小機能を複数クラスに追加できる <br>・軽い形で機能を拡張できる | ・多重継承の順序や衝突に注意 <br>・どこで定義されているか見にくくなる | ・ログ、キャッシュなど、ほかの機能と分離して使いたいとき |
| **委譲** | ・責務を分けやすくなる <br>・機能差し替えが容易 | ・ラッパーメソッドが増える <br>・委譲チェーンで追いにくくなる | ・機能部分をモジュール化して切り替えたいとき |
| **プロトコル** | ・継承なしで振る舞いの契約を表せる <br>・型チェックでミスを防げる | ・実行時には型情報は無視される <br>・型ヒント／チェックツールがないと恩恵が薄い | ・既存クラスに契約を持たせたいとき <br>・複数クラスに共通の振る舞いを課したいとき |


## 参考

- [What Are Mixin Classes in Python?](https://realpython.com/python-mixin/)
- [Method delegation in Python vs composition or inheritance](https://michaelcho.me/article/method-delegation-in-python/)
- [Inheritance and Composition: A Python OOP Guide](https://realpython.com/inheritance-composition-python/)