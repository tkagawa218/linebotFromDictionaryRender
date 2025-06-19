# 📚 Gemini × LINE 辞書Bot（FastAPI構成）

このBotは、LINEで「〇〇とは？」と送ると、**Google Gemini Flash モデル**を使ってやさしく意味を返す、辞書形式のAIチャットボットです。

FastAPI + Render 無料枠で構築されており、学習用途・プロトタイプにも最適です。

---

## 🔧 使用技術スタック

| 項目         | 使用技術                         |
|--------------|----------------------------------|
| 言語         | Python 3.11                      |
| Webフレーム  | FastAPI                          |
| デプロイ     | Render（無料枠対応）            |
| LINE連携     | LINE Messaging API               |
| AIモデル     | Google Gemini 1.5 Flash          |
| ログ出力     | loguru                           |
| 非同期処理   | `message_queue.py` 簡易Queue構成 |

---

## 📦 機能概要

- ユーザーが LINE に「〇〇とは？」と送信  
- Gemini API（Flashモデル）で定義・意味を生成  
- LINE Botが自動応答  
- 無料API枠で動作、QuotaエラーもLINE返信で通知  
- loguru によるログ記録でエラー追跡可能  

---

## ▶️ 動作イメージ
👤 ユーザー：機械学習とは？
🤖 Bot　　：機械学習とは、データからパターンを学習し…

## 📁 ファイル構成

.
├── app.py # Webhook受信＆LINE返信（FastAPIメイン処理）
├── worker.py # 非同期バックグラウンド処理（オプション）
├── gemini_client.py # Gemini APIとの通信クライアント
├── message_queue.py # 簡易メッセージQueue構成
├── requirements.txt # ライブラリ定義
├── render.yaml # Render用のサービス定義ファイル
├── Procfile # Render実行定義
├── .env.example # 環境変数テンプレート
└── README.md # このファイル

## 🚀 セットアップ手順

### 1. 環境変数を設定（`.env` または Render上）

```env
LINE_CHANNEL_ACCESS_TOKEN=xxxxx
LINE_CHANNEL_SECRET=xxxxx
GOOGLE_API_KEY=xxxxx
MODEL_NAME=gemini-1.5-flash

3. Renderへデプロイ（無料プラン対応）
render.yaml で「Web Service」作成

worker.py は任意で「Background Worker」設定可能

📝 補足・工夫ポイント
Gemini Flashモデル採用で高速×無料な応答実現

LINEの応答タイムアウト対策で非同期設計済み

loguru による強力なログ記録（トラブル追跡に便利）

worker.py による非同期処理も構築可能な設計

💡 将来の拡張案
RedisによるタスクQueue処理（複数Botで分散対応）

AIモデルの切替（OpenAI / Claude など）

ログ/履歴管理によるユーザー対応の拡張

Web UIによるログビューや統計表示ダッシュボード

📮 連絡・著者
制作：Tatsuya Kagawa（フリーランスエンジニア）
