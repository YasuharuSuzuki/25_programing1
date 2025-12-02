"""
送信ウィジェットモジュール - ipywidgetsを使った送信UI作成
"""

import ipywidgets as widgets
from IPython.display import display

from .email_detector import EmailDetector
from .storage_helper import StorageManager
from .notebook_reader import NotebookReader
from .grading_client import GradingClient

class SubmitWidget:
    """送信UIの管理を行うクラス"""
    
    def __init__(self):
        self.email_detector = EmailDetector()
        self.storage_manager = StorageManager()
        self.notebook_reader = NotebookReader()
        self.grading_client = GradingClient()
        self.detected_email = None
    
    def initialize_common_program(self):
        """共通プログラムの初期化（メールアドレス自動取得）"""
        print("🚀 共通プログラム初期化中...")
        
        # 保存済みメールアドレスの確認
        saved_email = self.storage_manager.load_email_address()
        if saved_email and self.email_detector.is_valid_email(saved_email):
            print(f"✅ 保存済みメールアドレス取得: {saved_email}")
            self.detected_email = saved_email
        else:
            # 新規取得を試行（Google Colabのみ）
            auto_email = self.email_detector.get_colab_email_auto()
            if auto_email:
                print(f"✅ 自動取得成功: {auto_email}")
                self.detected_email = auto_email
            else:
                print("❌ 自動取得失敗（送信ボタン使用時に手動で取得してください）")
                self.detected_email = None
        
        print("送信ボタン用関数が読み込まれました（問題番号別送信ボタン検索・Notebook構造解析・localStorage/ファイル保存対応・送信時自動保存）")
    
    def create_submit_button(self, problem_number=1, button_name="練習プログラム"):
        """
        実際の自動採点システム向け送信ボタンを作成（送信時自動保存機能付き）
        
        Args:
            problem_number (int): 問題番号
        
        Returns:
            widgets.VBox: 送信ウィジェット
        """
        # メールアドレス入力ウィジェット
        email_widget = widgets.Text(
            value='',
            placeholder='99ZZ888@okiu.ac.jp',
            description='メールアドレス:',
            disabled=False,
            style={'description_width': '100px'}
        )
        
        # 保存済みメールアドレスを自動設定
        saved_email = self.storage_manager.load_email_address()
        if saved_email and self.email_detector.is_valid_email(saved_email):
            email_widget.value = saved_email
            print(f"🎯 保存済みメールアドレスを自動設定: {saved_email}")
        elif self.detected_email and self.email_detector.is_valid_email(self.detected_email):
            email_widget.value = self.detected_email
            print(f"🎯 共通プログラムで取得したメールアドレスを自動設定: {self.detected_email}")
        
        # 送信ボタン
        submit_button = widgets.Button(
            description=f'📤 {button_name}{problem_number} 送信',
            disabled=False,
            button_style='success',
            tooltip=f'{button_name}{problem_number}の解答を送信',
            layout=widgets.Layout(width='250px')
        )
        
        # Python版メールアドレス取得ボタン
        reload_python_button = widgets.Button(
            description='🔄 メアド取得',
            disabled=False,
            button_style='warning',
            tooltip='Google Colabからメールアドレスを取得',
            layout=widgets.Layout(width='120px')
        )
        
        # ステータス表示
        status_widget = widgets.HTML(
            value='<small>💡 メールアドレスは自動保存されます</small>'
        )
        
        # 結果表示
        output_widget = widgets.Output()
        
        def on_reload_python_clicked(b):
            """Python版メールアドレス取得ボタンのハンドラ"""
            with output_widget:
                output_widget.clear_output()
                print("🔄 メールアドレスを再取得中...")
                
                email = self.email_detector.get_colab_email_auto()
                if email:
                    email_widget.value = email
                    self.detected_email = email
                    print(f"✅ メールアドレスを設定しました: {email}")
                else:
                    print("❌ メールアドレスを取得できませんでした")
        
        def on_submit_clicked(b):
            """送信ボタンのハンドラ"""
            with output_widget:
                output_widget.clear_output()
                
                student_email = email_widget.value.strip()
                
                if not student_email:
                    print("⚠️ メールアドレスを入力してください")
                    return
                
                if not self.email_detector.is_valid_email(student_email):
                    print("⚠️ 有効なメールアドレスを入力してください")
                    return
                
                # メールアドレス保存
                if self.storage_manager.save_email_address(student_email):
                    print(f"💾 メールアドレスを保存しました: {student_email}")
                
                # 指定された問題番号の送信ボタン前のセル内容を取得
                notebook_cells = self.notebook_reader.get_notebook_cells_before_submit(problem_number)
                
                if not notebook_cells:
                    print("❌ 送信対象のセルが見つかりませんでした")
                    return
                
                # 自動採点システムに送信
                self.grading_client.submit_assignment(
                    student_email, 
                    problem_number, 
                    notebook_cells,
                    auto_save=True
                )
                
        
        submit_button.on_click(on_submit_clicked)
        reload_python_button.on_click(on_reload_python_clicked)
        
        # ウィジェット組み立て
        button_row = widgets.HBox([submit_button, reload_python_button])
        submit_widget = widgets.VBox([
            widgets.HTML(f"<h4>📤 練習プログラム{problem_number} 解答送信</h4>"),
            status_widget,
            email_widget,
            button_row,
            widgets.HTML('<small>🔄=localStorage/ファイル保存、📡=3回リトライ機能付き送信、🔍=送信時自動保存</small>'),
            output_widget
        ], layout=widgets.Layout(
            border='2px solid #4CAF50',
            border_radius='8px',
            padding='15px',
            margin='10px 0'
        ))
        
        return submit_widget
    
    def get_detected_email(self):
        """検出済みメールアドレスを取得"""
        return self.detected_email
    
    def set_detected_email(self, email):
        """検出済みメールアドレスを設定"""
        self.detected_email = email
    
    def set_grading_system_url(self, url):
        """採点システムのURLを設定"""
        self.grading_client.set_grading_system_url(url)
    
    def set_notebook_path(self, notebook_path):
        """ノートブックパスを設定"""
        self.grading_client.set_notebook_path(notebook_path)
        self.notebook_reader.set_notebook_path(notebook_path)
    
    def get_notebook_path(self):
        """現在のノートブックパスを取得"""
        return self.grading_client.get_notebook_path()