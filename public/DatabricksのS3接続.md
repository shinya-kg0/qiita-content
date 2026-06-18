---
title: DatabricksからS3に安全に接続する設定手順まとめ
tags:
  - 'Databricks'
  - 'S3'
  - 'Unity Catalog'
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

# はじめに

DatabricksでAWS S3のデータを読み書きしようとしたとき、
「IAMロール？ストレージクレデンシャル？外部ロケーション？」と
登場人物の多さに戸惑いました。

この記事では、備忘録も兼ねて
Unity Catalogを使ってS3に接続するまでの手順を、
概念の整理から動作確認まで順番にまとめます。

## なぜUnity Catalogで接続するのか

以前はDatabricksからS3に接続する方法として、
クラスターの設定にIAMアクセスキーやインスタンスプロファイルを直接渡す方法が一般的でした。

この方法にはいくつか問題があります。

- **クレデンシャルが分散する**：クラスターごとに設定が必要で、管理が煩雑になる
- **アクセス制御が粗い**：クラスターにアクセスできるユーザーは全員同じS3権限を持つ
- **監査が難しい**：誰がいつどのデータにアクセスしたかを追うのが難しい

Unity Catalogを使うと、ストレージクレデンシャルと外部ロケーションという
オブジェクトを介してS3への接続を一元管理できます。
ユーザー・グループ単位で細かくアクセス制御できるのが大きなメリットです。

## S3への接続方法

現在時点では以下の接続パターンがあります。

| 方法 | 概要 | 向いているケース |
|------|------|----------------|
| **AWS CloudFormation**（Databricks推奨） | テンプレートを実行するだけでIAMロール・ストレージクレデンシャル・外部ロケーションを自動作成 | 初回・手早くつなぎたいとき |
| カタログエクスプローラー | UIでストレージクレデンシャルと外部ロケーションを個別に作成 | GUI操作が好み・設定内容を細かく確認したいとき |
| SQL / Notebook | SQLコマンドでプログラム的にオブジェクトを作成 | 複数ロケーションを一括作成・IaCで管理したいとき |


> 今回はカタログエクスプローラーを使った手動作成で進めます。
> CloudFormationは便利ですが、
> 裏側で何が起きているかがブラックボックスになりがちです。
> 手動でやると各オブジェクトの役割がよくわかるのでおすすめです。

# 全体像を確認

設定を始める前に、登場人物の関係を整理しておきます。
大きく**AWS側**と**Databricks側**の2つに分かれます。


## AWS側

| オブジェクト | 役割 |
|---|---|
| S3バケット | アクセス対象のデータの置き場所 |
| IAMポリシー | S3バケットへの操作権限（読み書き等）を定義する |
| IAMロール | IAMポリシーをアタッチしてDatabricksに引き受けさせる（AssumeRole）|

- AssumeRoleとは
  - 「一時的にロールを借りられる仕組み」
  - このRoleを使うためには、AssumeRoleをしていいよというポリシーとどのアカウントが使っていいかという信頼ポリシーが必要



## Databricks側

| オブジェクト | 役割 |
|---|---|
| ストレージクレデンシャル | IAMロールへの参照を保持するオブジェクト |
| 外部ロケーション | 「S3のこのパス」＋「このクレデンシャルでアクセス」を組み合わせたオブジェクト |

## 2つをつなぐのが「信頼ポリシー＋外部ID」

IAMロールとストレージクレデンシャルは、**信頼ポリシー**によって紐付けられます。
このとき、なりすまし防止のために**外部ID**という識別子を使います。

# 実際に設定してみる

## AWS側

### Step1 S3バケットの作成

まずは接続用のS3バケットを用意します。
AWSコンソールから通常通りバケットを作成すればOKです。

- バケット名（例）: `my-databricks-bucket`
- 後ほど使うので、S3のURI（`s3://my-databricks-bucket`）をメモしておきます。
- 動作確認用のために、いくつかフォルダを作っておきます

### Step2 IAMポリシーの作成

DatabricksがS3バケットを操作するための最小限の権限を定義します。
IAMの画面で「ポリシーの作成」を選び、JSONタブに以下を貼り付けて作成してください。

- ポリシー名（例）: `databricks-s3-access-policy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::my-databricks-bucket",
        "arn:aws:s3:::my-databricks-bucket/*"
      ]
    }
  ]
}
```

### Step3 IAMロールの作成と信頼ポリシーの設定

ここがポイントです。Databricksがこのロールを使えるように**信頼ポリシー**を設定します。

1. IAMの画面から「ロールの作成」をクリック。
2. 信頼されたエンティティタイプで「カスタム信頼ポリシー」を選択。
3. 以下のJSONを貼り付けます。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::742402427301:role/databricks_unity_catalog_role",
          "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL"
        ]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "YOUR_EXTERNAL_ID"
        }
      }
    }
  ]
}
```

- 注意点
  - `Principal`の`AWS`にはDatabricks公式のシステム共通ロールを指定します。
  - `sts:ExternalId`の`YOUR_EXTERNAL_ID`には、仮で値を入れておいて後で正しい外部IDに更新します。

1. Step 2で作成したポリシー（`databricks-s3-access-policy`）をアタッチしてロールを作成します。
2. 作成完了後、ロールのARN（`arn:aws:iam::123456789012:role/...`）をメモしておきます。


### Step5 信頼ポリシーの更新

Step4（後述）で作成された外部IDを使って、信頼ポリシーの
`YOUR_EXTERNAL_ID`部分を更新します。


## Databricks側

### Step4 ストレージクレデンシャルの作成


1. カタログ > 接続 > 資格情報に移動し、「資格情報を作成」ボタンをクリックする。
2. 次のように資格情報を入力する。

|  項目  |  例  |
|  ---  | --- |
|   資格情報のタイプ    |   AWS IAMロール  |
|    資格情報名       |      aws-s3-credential（任意）  |
|       IAMロール         |       先ほど作成したIAMロールのARN         |

![スクリーンショット 2026-06-18 13.13.50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4200201/143f8cf0-974d-4647-8ed4-d5394abc34ac.png)

3. 作成すると外部IDが表示されるのでメモしておく。（信頼ポリシーに使用）

### Step6 外部ロケーションの作成

1. カタログ > 接続 > 外部ロケーションに移動し、「外部ロケーションを作成」ボタンをクリックする。
2. 「AWSクイックスタート」がありますが、ここでは手動を選択する。
3. 次のように資格情報を入力する。

|  項目  |  例  |
|  ---  | --- |
|   外部ロケーション名    |   my-s3-external-location（任意）  |
|    ストレージタイプ       |    S3    |
|     URL         |      `s3://my-databricks-bucket`      |
|   ストレージ資格情報   |      作成したIAMロール      |

![スクリーンショット 2026-06-18 13.28.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4200201/966ad894-5cdb-4c16-aaf1-7d78ac6f9a0c.png)


外部ロケーション作成時点で、接続テストが走ります。
今回は最低限のS3操作のポリシーしか与えていないので全て成功にはなりません。
（必要に応じてポリシーを調整してください。）

![スクリーンショット 2026-06-18 13.36.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4200201/430d9580-e915-41c4-809c-ec51655c7d79.png)


### Step7 動作確認

Databricks側で新規のノートブックを開きます。
Pythonを使って以下のようにS3バケットの中身を見てみます。

作成しておいたS3のフォルダが確認できると思います。

```python
display(dbutils.fs.ls("s3://my-databricks-bucket/"))
```

# おわりに

Unity Catalogの外部ロケーション機能を使うことで、
コードに一切クレデンシャル（アクセスキーなど）を書くことなく、安全にS3と接続することができました。

AWSと接続するなら「クイックスタート」の手法も用意されているので
そちらを使ってもいいと思います。（むしろ推奨されている）

- 参考
  - [AWS S3 外部ロケーションへの接続](https://docs.databricks.com/aws/ja/connect/unity-catalog/cloud-storage/s3/)
