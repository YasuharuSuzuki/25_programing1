"""
91_notebook_client Python モジュール
自動採点システム向けクライアント機能の統合パッケージ
"""

# 主要クラスのインポート
from .environment_detector import EnvironmentDetector
from .storage_helper import StorageManager
from .email_detector import EmailDetector
from .notebook_reader import NotebookReader
from .grading_client import GradingClient
from .submit_widget import SubmitWidget
from .result_viewer import ResultViewer

# バージョン情報
__version__ = "2.0.0"
__author__ = "Programming I Course 2025"

# 主要クラスのエクスポート
__all__ = [
    # 環境検出
    'EnvironmentDetector',
    
    # ストレージ管理
    'StorageManager',
    
    # メールアドレス検出
    'EmailDetector',
    
    # ノートブック読み込み
    'NotebookReader',
    
    # 採点システムクライアント
    'GradingClient',
    
    # UI ウィジェット
    'SubmitWidget',
    
    # 結果表示
    'ResultViewer',
]

# 簡単な使用方法のための便利関数
def create_submit_button(problem_number=1, button_name="練習プログラム"):
    """
    送信ボタンを作成する便利関数
    
    Args:
        problem_number (int): 問題番号
    
    Returns:
        widgets.VBox: 送信ウィジェット
    """
    widget_manager = SubmitWidget()
    return widget_manager.create_submit_button(problem_number, button_name)

def initialize_common_program():
    """
    共通プログラムの初期化
    
    Returns:
        SubmitWidget: 設定済みのSubmitWidgetインスタンス
    """
    widget_manager = SubmitWidget()
    widget_manager.initialize_common_program()
    return widget_manager