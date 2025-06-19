📚 Gemini × LINE 辞書Bot（FastAPI構成）
LINEメッセージで「用語」を送ると、Gemini Flashモデルを使って自動で意味を返す辞書Botです。
FastAPI + Render構成で無料デプロイできるように設計されています。

🔧 使用技術スタック
項目	使用技術
言語	Python 3.11
Webフレームワーク	FastAPI
デプロイ環境	Render（無料枠）
LINE連携	LINE Messaging API
AIモデル	Google Gemini 1.5 Flash
ログ出力	loguru
非同期処理	message_queue モジュールで簡易Queue構成

📦 機能概要
ユーザーがLINEで「〇〇とは？」とメッセージを送信

Gemini Flashモデルで定義・意味を生成

LINE Botが自動で応答

Google Generative AI API の 無料枠内で動作するよう調整

APIエラー・Quota超過時もログに記録・LINE返信で通知

▶️ 動作イメージ
コピーする
編集する
👤 ユーザー：機械学習とは？
🤖 Bot　　：機械学習とは、データからパターンを学習し…
📁 ファイル構成
bash
コピーする
編集する
.
├── app.py               # FastAPIメイン処理（Webhook受信＆返信）
├── worker.py            # 将来用: 非同期Queue用バックグラウンド処理
├── gemini_client.py     # Gemini APIとのやりとりを行うクラス
├── message_queue.py     # メッセージキュー（簡易実装）
├── requirements.txt     # 使用ライブラリ
├── render.yaml          # Render用サービス定義
├── Procfile             # Renderの起動定義
└── .env（Renderで設定）# APIキー類（ローカルではdotenvで）
🚀 セットアップ手順
1. 環境変数を設定 .env（またはRenderダッシュボード上）
env
コピーする
編集する
LINE_CHANNEL_ACCESS_TOKEN=xxxxx
LINE_CHANNEL_SECRET=xxxxx
GOOGLE_API_KEY=xxxxx
MODEL_NAME=gemini-1.5-flash
2. ローカルで起動
bash
コピーする
編集する
pip install -r requirements.txt
python app.py
3. デプロイ（Render）
render.yamlを使って「Web Service」として作成

worker.py用のバックグラウンドJobも登録可能（必要に応じて）

📝 補足・工夫ポイント
Gemini 1.5 Flashモデルを利用することで無料プランでも高速動作

将来的に worker.py を非同期タスク処理に使えるよう構成済み

loguru でログ出力を強化。トラブルシュートしやすい

LINE応答遅延を防ぐため、Bot応答部分を非同期で設計

💡 将来の拡張案
Redisなどを使ったQueueによる負荷分散

Gemini以外（OpenAI・Claude等）モデルの切替

ユーザー別ログ・履歴管理

Web UI（ログビューワ・キーワード統計など）

📮 連絡・著者
制作：Tatsuya Kagawa（フリーランスエンジニア）

ご相談・カスタマイズのご依頼などはお気軽に。
生成AI × Bot の実装に関する相談も承ります。

