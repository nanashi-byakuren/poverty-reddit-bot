# poverty-reddit-bot

機能が貧弱なRedditのbot

## 機能概要

- サーバ上でバッチ的に動かします

## botを動かす準備

### Redditのcredentialを得る

参考: [OAuth2 Quick Start Example](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example)

- https://www.reddit.com/prefs/apps
  - 上記に行ってアプリを作成(create application)
    - name: 適当
    - type: **script** を選択
    - description: 適当
    - about url: 一応GitHubのリポジトリにしてる
    - redirect url: 一応GitHubのリポジトリにしてる

上記をやると以下のような情報がもらえる

- ユーザー名: `reddit_bot`
- パスワード: `snoo`
- OAuthのclient ID: `p-jcoLKBynTLew`
- OAuthのclient secret: `gko_LXELoV07ZBNUXrvWZfzE3aI`

### Slackのbotを作成する

TODO: 詳しいやり方は各自調査してください

- 必要なこと
  - Slack APIのページからアプリを作成
  - Slack APIのページからbot用のトークンを取得
  - GoogleNewsのRSSを投稿するチャンネルを作成し、RSSをそこに流す
  - `#bot-debug` というチャンネルを作成しておく
  - 各チャンネルにはbotを招待しておく

### ビルドと実行

- Python 3.6以上が必要

```
// ライブラリのインストール
$ pip install -r requirements.txt
```

### GCPへのデプロイ

以下の手順でbotをGCPのCloudFunctionにデプロイする

#### 依存ライブラリのインストール

```shell
$ pip install -r requirements-dev.txt
```

#### GCP周りの準備

- GCPのサービスアカウントを作成する, [事前にgcloudコマンドをインストールしておく](https://cloud.google.com/sdk/docs/install?hl=ja)
```shell
// gcloudのプロファイルのリストを確認
$ gcloud config list

// reddit用のプロファイルを作成する(プロファイル名にはわかりやすい任意の名前を英語で指定)
$ gcloud config configurations create {プロファイル名}
Created [プロファイル名].
Activated [プロファイル名].

// 作成したプロファイルでアクティブ化する場合は以下のコマンド(上記でActivateされるのでここでは不要)
$ gcloud config configurations activate {プロファイル名}

// ログインしていない場合ログインする(ブラウザが起動する)
$ gcloud auth login
```

- 自分のアカウントのGCPが保持するプロジェクトを確認する([事前にGCPコンソールでプロジェクトを作成しておく](https://cloud.google.com/resource-manager/docs/creating-managing-projects?hl=ja))

```shell
$ gcloud projects list
PROJECT_ID         NAME        PROJECT_NUMBER
reddit-bot-114514  reddit-bot  22902838382290

// 追加したプロファイルにプロジェクト等を紐付ける
$ gcloud config set core/project {上記で確認したGCPのプロジェクトID}
$ gcloud config set core/account {GCPのアカウントのメールアドレス}
// リージョンを東京にする、有効化するか聞かれたら全部yで答える
$ gcloud config set compute/region asia-northeast1
$ gcloud config set compute/zone asia-northeast1-a
$ gcloud config set core/disable_usage_reporting False

- botで使用する[サービスアカウントを作成する](https://cloud.google.com/docs/authentication/getting-started?hl=ja)

```shell
// サービスアカウント名にはわかりやすい任意の名前を英語で指定
$ gcloud iam service-accounts create {サービスアカウント名}

// プロジェクトIDとサービスアカウント名を指定して権限設定する
$ gcloud projects add-iam-policy-binding {上で確認したGCPのプロジェクトID} \
  --member="serviceAccount:{サービスアカウント名}@{上で確認したGCPのプロジェクトID}.iam.gserviceaccount.com" \
  --role="roles/owner"

// GCPのサービスアカウントファイル（認証キーみたいなもの）を生成する
$ gcloud iam service-accounts keys create ~/.gcp/reddit-cred.json \
  --iam-account={サービスアカウント名}@{上で確認したGCPのプロジェクトID}.iam.gserviceaccount.com
```

#### Terraformで使用する設定ファイルを作成

`vars.tfvars`ファイルを作成する。

```shell
$ cp vars.tfvars.sample vars.tfvars
```

ファイルを編集し以下のパラメーターを設定する

- Reddit関連
  - `CLIENT_ID="{OAuthのclient ID}"`
  - `CLIENT_SECRET="{OAuthのclient secret}"`
  - `USER_AGENT="{任意のユーザーエージェント}"`
  - `USERNAME="{redditで使用するbotのusername}"`
  - `PASSWORD="{redditで使用するbotのpassword}"`
  - `SUBREDDIT="{POST対象のサブレディット名、「r/」はつけない（例: redditdev）}"`

- GCP関連
  - `GCP_PROJECT_ID="{GCPのプロジェクトID}"`
  - `GCP_SERVICE_ACCOUNT_FILE="~/.gcp/reddit-cred.json"`
  - `GCP_ACCOUNT="{サービスアカウント名}@{GCPのプロジェクトID}.iam.gserviceaccount.com"`

- Slack関連
  - `SLACK_BOT_TOKEN="{Slackのbot用トークン(xoxb-で始まる)}"`
  - `SUBSCRIBE_CHANNEL_IDS="XXXXXXXXX,YYYYYYYYY"` ... 監視したいSlackのチャンネルIDをカンマ区切り
  - `GOOGLE_NEWS_CHANNEL_ID="XXXXXXXXX"` ... GoogleNewsのRSSを投稿するチャンネルID


- terraformを実行し、GCPのCloudFunctionにデプロイする

```shell
$ terraform init
$ terraform plan -var-file=vars.tfvars
$ terraform apply -var-file=vars.tfvars
```

後は投稿されるのを待つ。わざとじゃなくてもやりすぎるとBANされると思うのでいたずらはやめよう。