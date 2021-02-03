# poverty-reddit-bot

機能が貧弱なRedditのbot

## 機能概要

- サーバ上でバッチ的に動かします

## botを動かす

### credentialを得る

参考: [OAuth2 Quick Start Example](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example)

- https://www.reddit.com/prefs/apps
  - 上記に行ってアプリを作成(create application)
    - name: 適当
    - type: **script** を選択
    - description: 適当
    - about url: 一応GitHubのリポジトリにしてる
    - redirect url: 一応GitHubのリポジトリにしてる

上記をやると以下の情報がもらえる、右は例

- ユーザー名: `reddit_bot`
- パスワード: `snoo`
- OAuthのclient ID: `p-jcoLKBynTLew`
- OAuthのclient secret: `gko_LXELoV07ZBNUXrvWZfzE3aI`



### ビルドと実行

- Python 3.6以上が必要

```
// ライブラリのインストール
$ pip install -r requirements.txt
```

### サーバへのデプロイ

```
// ライブラリのインストール
$ pip install -r requirements-dev.txt

// .envファイルの作成
$ cp .env.sample .env

// ansible-playbook.shの実行
$ chmod +x ./ansible-playbook.sh
$ ./ansible-playbook.sh -i reddit-bot-host.yml reddit-bot-task.yml
```