# 予約カレンダーシステム (Django)

これはDjangoフレームワークを使用して構築された、シンプルな予約管理アプリケーションです。FullCalendar.ioと連携し、ウェブブラウザ上で直感的に予約の確認、追加、削除ができます。

## 主な機能

  * **カレンダー表示**: 予約と共有スケジュールを月・週・日単位のカレンダーで視覚的に表示します。
  * **予約機能**: カレンダーの日付をクリックし、空いている時間帯を選択して新しい予約を追加できます。
  * **予約削除機能**: カレンダー上の予約をクリックすると詳細が表示され、その場で予約を削除できます。
  * **共有スケジュール管理**: Djangoの管理画面から、予約とは別に全ユーザーに共有されるスケジュール（例: 休診日、イベントなど）を登録できます。

## 使用技術

  * **バックエンド**: Python, Django
  * **フロントエンド**: HTML, CSS, JavaScript, FullCalendar.io
  * **データベース**: SQLite3 (デフォルト)
  * **本番環境サーバー**: Gunicorn

## セットアップと実行方法

### 1\. 前提条件

  * Python 3.x
  * pip

### 2\. リポジトリのクローン

```bash
git clone <リポジトリのURL>
cd <リポジトリ名>
```

### 3\. 仮想環境の作成と有効化

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4\. 依存ライブラリのインストール

プロジェクトに必要なライブラリを`requirements.txt`からインストールします。

```bash
pip install -r requirements.txt
```

### 5\. データベースのマイグレーション

データベースのテーブルを初期化します。

```bash
python manage.py migrate
```

### 6\. 管理者ユーザーの作成

共有スケジュールを登録するために、管理サイトにログインするための管理者アカウントを作成します。

```bash
python manage.py createsuperuser
```

(画面の指示に従って、ユーザー名、メールアドレス、パスワードを設定してください)

### 7\. 開発サーバーの起動

```bash
python manage.py runserver
```

ブラウザで `http://127.0.0.1:8000/` にアクセスすると、予約カレンダーが表示されます。
また、`http://127.0.0.1:8000/admin/` から管理サイトにログインできます。
