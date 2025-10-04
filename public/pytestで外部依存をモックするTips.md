---
title: pytestでモックやパッチを使いたい！｜monkeypatch vs testfixtures.replace
tags:
  - 'Python'
  - 'pytest'
  - 'モック'
  - 'パッチ'
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---
# はじめに

テストコードを書いていると、こんなことありませんか？

- テストしたいけどDBアクセスや外部APIを使う必要がある
- 修正中の関数を使う必要があって、いったん処理できると仮定したい

こういう時に、モックやパッチを使うことで
効率よくテストコードを書いていくことができます！

この記事では`monkeypatch`、`testfixtures.replace`を使った、
すぐに使えるTipsを紹介していきます！

## モックとパッチ

実際に使う時はあまり意識する必要はないかもしれませんが、
言葉の定義として整理しておきます！

| 項目 | モック（Mock） | パッチ（Patch） |
|------|----------------|-----------------|
| 意味 | 本物の代わりに動作する <br>**ダミーオブジェクト** | 既存の関数・メソッド・クラス・変数を<br> **他のものに差し替える行為** |
| 役割 | 「何に置き換えるか」を提供する<br>（偽物の中身） | 「どこを置き換えるか」を操作する<br>（差し替えの仕組み） |
| 対象 | ダミー関数・ダミークラスなど | 関数・クラス・変数・環境変数 など |


# monkeypatch

pytest には標準で **`monkeypatch`** が用意されています。  

これを使うと「関数」「クラス」「環境変数」などを **テスト実行中だけ安全に差し替え** できます。  
テストが終われば自動で元に戻るので、副作用を残さず安心です。

## 基本的な使い方

### 関数や属性の差し替え

`monkeypatch.setattr`を使います。

使い方：`monkeypatch.setattr("モジュール.関数名", 差し替える関数)`

```py
# app.py
def get_data():
    # 本来は外部APIを叩く想定
    raise RuntimeError("外部APIに接続できません")

def process():
    return f"data: {get_data()}"
```

```py
# test_app.py
from app import process

def test_process(monkeypatch):
    # get_data をダミー関数に差し替え
    monkeypatch.setattr("app.get_data", lambda: "dummy-data")

    assert process() == "data: dummy-data"
```

1. `process()`内で`get_data()`を呼んでいます。
2. テストコードではDBや外部APIなどでデータを取ってくる代わりに、 lambda関数を使って`"dummy-data"`を返すようなダミー関数に差し替えています。
3. `process()`がダミーで返された値をassert文でチェックしています。


### 環境変数の差し替え

`monkeypatch.setenv`を使います。

使い方：`monkeypatch.setenv("環境変数名", 差し替える値)`

```py
# config.py
import os

def get_api_key():
    return os.environ["API_KEY"]
```

```py
# test_config.py
from config import get_api_key

def test_get_api_key(monkeypatch):
    # 環境変数を一時的に差し替え
    monkeypatch.setenv("API_KEY", "test-key-123")

    assert get_api_key() == "test-key-123"
```

1. `get_api_key()`を使って環境変数にアクセスしています。
2. テストコードでは環境変数を一時的に指定したものに変更できます。
3. assert文で環境変数をチェックしています。

※ 環境変数の差し替えのやり方の具体例なので、実際にこういうテストはしないと思います。。。

## 実用例

基本的な使い方は理解できたと思うので、実際に使うとしたらを想定してみます！

### DB接続してユーザーを取得したい

```py
# user_service.py
def fetch_user():
    # 本来はDBに接続してユーザーを取得する想定
    raise RuntimeError("DB接続エラー")

def get_username():
    return f"Hello, {fetch_user()}!"
```

```py
# test_user_service.py
from user_service import get_username

def test_get_username(monkeypatch):
    # fetch_user をテスト用の関数に差し替え
    monkeypatch.setattr("user_service.fetch_user", lambda: "TestUser")

    assert get_username() == "Hello, TestUser!"
```

### 環境変数を一時的に変更してテストしたい

```py
# settings.py
import os

def get_env_mode():
    return os.environ.get("APP_MODE", "development")
```

```py
# test_settings.py
from settings import get_env_mode

def test_get_env_mode(monkeypatch):
    monkeypatch.setenv("APP_MODE", "production")
    assert get_env_mode() == "production"

def test_default_env_mode(monkeypatch):
    monkeypatch.delenv("APP_MODE", raising=False)
    assert get_env_mode() == "development"
```

- delenvで環境変数の削除もできます。
- `raising=False`はもともと環境変数が存在しなくてもエラーにならないという設定です。


# testfixtures.replace

`testfixtures` は Python のテスト補助ライブラリで、  
`@replace` デコレーターを使うと **関数やメソッドをテスト実行中だけ差し替え** できます。  
もちろんこちらもテストが終われば自動で元に戻るので、副作用を残さず安心です。

pytest標準ではないため `pip install testfixtures` が必要ですが、  
デコレーターで書けるので「どこを差し替えているか」がテスト関数の冒頭で明示でき、可読性が高いのが特徴です。


デコレーターについてよくわからない〜、、、という方は、
この記事でさらっとどんなことができるのか理解しておくとスムーズです！
→ [Pythonのデコレータについて](https://qiita.com/mtb_beta/items/d257519b018b8cd0cc2e)


## 基本的な使い方

### 関数やメソッドの差し替え

`@replace`デコレーターを使います。

使い方：`@replace("モジュール.関数名", 差し替え関数)`


```py
# app.py
def get_user_name():
    return "RealUser"

def greet():
    return f"Hello, {get_user_name()}!"
```

```py
# test_app.py
from testfixtures import replace
import app

def fake_get_user_name():
    return "TestUser"

@replace("app.get_user_name", fake_get_user_name)
def test_greet():
    assert app.greet() == "Hello, TestUser!"
```

1. app.pyで`RealUser`を使って挨拶を返す関数を定義しています。
2. テストコード内で差し替えたい関数（`fake_get_user_name()`）を定義します。
3. `@replace`デコレーターをテストしたいコードにつけることで、実行中のみ差し替えが可能です。

## 実用例

@replaceの使い方はシンプルなので、実際に使えるような他の例も紹介します！

### 複数パッチを同時に使う

@replaceはデコレーターを重ね書きできます。
複数の依存関数をかんたんに差し替えることもできます。

```py
# service.py
def get_message():
    return "Hi"

def get_user():
    return "Alice"

def greet():
    return f"{get_message()}, {get_user()}!"
```

```py
# test_service.py
from testfixtures import replace
import service

def fake_get_message():
    return "Hello"

def fake_get_user():
    return "Bob"

@replace("service.get_message", fake_get_message)
@replace("service.get_user", fake_get_user)
def test_greet():
    assert service.greet() == "Hello, Bob!"
```

### メソッドを差し替える

関数だけでなく、メソッドにも適用できます。

```py
# service.py
class UserService:
    def fetch(self):
        return "real"

def use_service():
    return UserService().fetch()
```

```py
# test_service.py
from testfixtures import replace
import service

def fake_fetch(self):
    return "fake"

@replace("service.UserService.fetch", fake_fetch)
def test_use_service():
    assert service.use_service() == "fake"
```


## 5. どちらを使えばいいの？

ここまで `pytest` 標準の`monkeypatch`と、外部ライブラリ`testfixturesの@replace`を紹介しました。  

個人的には`@replace`の方が、可読性高いし使いやすいかなと感じてます。

やりたいことは変わらないので、プロジェクトや個人の好みでもいいかなと思いますが、
念の為、特徴を比較して使いやすい場面を見ていきます。

---

### 比較表

| 項目 | `pytest.monkeypatch` | `testfixtures.@replace` |
|------|--------------------|------------------------|
| 導入 | pytestに標準搭載、追加ライブラリ不要 | 外部ライブラリ `pip install testfixtures` が必要 |
| 書き方 | 関数内で `monkeypatch.setattr` / `setenv` を呼ぶ | デコレーター形式で冒頭に明示 |
| 適用範囲 | テスト関数のスコープ内（pytest管理） | テスト関数または with ブロック内 |
| 可読性 | 柔軟だが、テスト関数の中を読まないとどこを差し替えたか分からない | デコレーターで冒頭に差し替え対象を明示できるのでわかりやすい |
| 学習コスト | pytestユーザーならすぐ使える | 新しいライブラリを覚える必要あり |
| 利用シーン | とにかく軽量・標準で済ませたい場合 | 依存関数が多いテストで、差し替え対象を冒頭にまとめたい場合 |

---

### どちらを選ぶべき？

- まずは`monkeypatch`  
  - pytest標準機能なので安心  
  - 小規模テストや一時的な差し替えに十分  


- 大規模 or 可読性重視なら`@replace`  
  - デコレーターで「どの依存をモック化しているか」が一目でわかる  
  - 複数パッチを積み重ねられるのでテストが整理されやすい  



# 参考
- [How to monkeypatch/mock modules and environments](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [Mocking out objects and methods](https://testfixtures.readthedocs.io/en/4.9.0/mocking.html)
