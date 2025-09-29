#!/bin/bash

# 91_notebook_client セットアップスクリプト
# Google Colab環境で自動採点システムクライアントを初期化

echo "🚀 91_notebook_client セットアップ開始"

# デフォルト設定（本番環境）
DEFAULT_GITHUB_BASE_URL="https://raw.githubusercontent.com/YasuharuSuzuki/25_programing1/main/91_notebook_client/src"

# 環境設定ファイルから読み込み（.env のみ対応、より確実）
if [ -f ".env" ]; then
    echo "🔧 .env ファイルを検出、設定を読み込み中..."
    # .envファイルをsource（export付きの変数のみ読み込み）
    set -a && source .env && set +a
fi

# 環境変数が設定されていない場合はデフォルト値を使用
GITHUB_BASE_URL="${GITHUB_BASE_URL:-$DEFAULT_GITHUB_BASE_URL}"

# 作業ディレクトリ作成
CLIENT_DIR=".client"
echo "📁 作業ディレクトリ作成: ${CLIENT_DIR}"
mkdir -p "${CLIENT_DIR}/python"

echo "📡 ダウンロード元: ${GITHUB_BASE_URL}"

# Pythonモジュールのダウンロード
echo "🐍 Pythonモジュールダウンロード中..."

# 各Pythonファイルの配列
python_files=(
    "python/__init__.py"
    "python/environment_detector.py"
    "python/storage_helper.py"
    "python/email_detector.py"
    "python/notebook_reader.py"
    "python/result_viewer.py"
    "python/grading_client.py"
    "python/submit_widget.py"
    "client_setup.py"
)

for file in "${python_files[@]}"; do
    echo "  📥 ${file}"
    if ! wget -q "${GITHUB_BASE_URL}/${file}" -O "${CLIENT_DIR}/${file}"; then
        echo "  ❌ ダウンロード失敗: ${file}"
        # 失敗時のフォールバック：空ファイル作成
        touch "${CLIENT_DIR}/${file}"
        echo "  🔄 空ファイルを作成しました"
    else
        echo "  ✅ ${file} ダウンロード完了"
    fi
done

# セットアップ完了確認
echo "🔍 セットアップ確認中..."

# ダウンロードしたファイル数をカウント
python_count=$(find "${CLIENT_DIR}/python" -name "*.py" | wc -l)

echo "  📊 Pythonファイル: ${python_count}個"

echo "🎉 セットアップ完了！"
echo "⚠️ 注意事項: このセットアップはNotebook再起動時に再実行してください"

exit 0