"""
91_notebook_client 初期化スクリプト
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

# 環境変数を読み込んで設定
DEFAULT_GRADING_SYSTEM_URL = "https://auto-grading-system-gc6kcexpcq-an.a.run.app"
GRADING_SYSTEM_URL = os.getenv('GRADING_SYSTEM_URL', DEFAULT_GRADING_SYSTEM_URL)

# グローバル設定変数
GLOBAL_NOTEBOOK_PATH = None

# .clientディレクトリをPythonパスに追加
client_dir = os.path.join(os.getcwd(), '.client')
if client_dir not in sys.path:
    sys.path.insert(0, client_dir)

try:
    # クライアントモジュールをインポート
    from python import (
        create_submit_button,
        initialize_common_program,
        SubmitWidget
    )
    from python.grading_client import GradingClient
    
    # 採点システムURL設定付きの初期化関数
    def initialize_with_config():
        """環境変数とnotebook_pathを考慮した初期化"""
        widget_manager = initialize_common_program()
        widget_manager.set_grading_system_url(GRADING_SYSTEM_URL)
        print(f"🔧 採点システムURL: {GRADING_SYSTEM_URL}")
        return widget_manager
    
    # URL設定付きの送信ボタン作成関数
    def create_submit_button_with_config(problem_number=1, button_name="練習プログラム"):
        """環境変数を考慮した送信ボタン作成"""
        widget_manager = SubmitWidget()
        widget_manager.set_grading_system_url(GRADING_SYSTEM_URL)
        
        # グローバル設定からnotebook_pathを適用
        global GLOBAL_NOTEBOOK_PATH
        if GLOBAL_NOTEBOOK_PATH:
            widget_manager.set_notebook_path(GLOBAL_NOTEBOOK_PATH)
        
        return widget_manager.create_submit_button(problem_number,button_name)
    
    # ノートブック環境変数設定関数
    def set_notebook_config(notebook_path):
        """ノートブック固有の環境変数を設定"""
        global GLOBAL_NOTEBOOK_PATH
        GLOBAL_NOTEBOOK_PATH = notebook_path
        print(f"📋 ノートブックパス: {notebook_path}")
        print("✅ グローバル設定に保存しました")
    
    # キャンセルボタンテスト関数
    def test_cancel_button(max_retry, retry_delay):
        """キャンセルボタンのテスト関数"""
        client = GradingClient()
        client.set_grading_system_url(GRADING_SYSTEM_URL)
        return client.test_cancel_button(max_retry, retry_delay)
    
    
    # 初期化実行
    initialize_with_config()
    
    print("✅ 送信機能の初期化完了")
    
    # グローバル名前空間に主要関数をエクスポート
    globals()['create_submit_button'] = create_submit_button_with_config
    globals()['set_notebook_config'] = set_notebook_config
    globals()['test_cancel_button'] = test_cancel_button
    # globals()['test_retry_countdown'] = test_retry_countdown
    globals()['GRADING_SYSTEM_URL'] = GRADING_SYSTEM_URL
    
except ImportError as e:
    print(f"❌ 初期化エラー: setup.shを再実行してください")
    import traceback
    print(f"⚠️ エラー: {e}")
    print(f"📋 トレースバック:")
    traceback.print_exc()

except Exception as e:
    print(f"⚠️ 初期化エラーが発生しました")