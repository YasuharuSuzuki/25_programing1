"""
ノートブック読み込みモジュール - セル内容の取得とフィルタリング
"""

import json
import os
import glob
from datetime import datetime
from .environment_detector import EnvironmentDetector

class NotebookReader:
    """ノートブックの読み込みとセル管理を行うクラス"""
    
    def __init__(self):
        self.env_detector = EnvironmentDetector()
    
    def filter_submission_cells(self, cells):
        """送信対象外セルを除外するフィルター（#@titleで始まるセルを除外）"""
        filtered_cells = []
        
        for cell in cells:
            # セルタイプがcodeの場合のみチェック
            if cell.get('cell_type') == 'code' and 'source' in cell:
                source = cell['source']
                if isinstance(source, list):
                    source = ''.join(source)
                
                # #@titleで始まるセルは除外
                if source.strip().startswith('#@title'):
                    # print(f"🚫 除外セル（#@title）: {source[:50]}...")
                    continue
            
            # 除外対象でない場合は追加
            filtered_cells.append(cell)
        
        return filtered_cells
    
    def get_notebook_cells_colab(self):
        """Google Colabからノートブック情報を取得"""
        try:
            from google.colab import _message
            notebook_data = _message.blocking_request('get_ipynb', request='', timeout_sec=10)
            
            # レスポンス構造: {'ipynb': {'cells': [...]}}
            if (isinstance(notebook_data, dict) and 
                'ipynb' in notebook_data and 
                isinstance(notebook_data['ipynb'], dict) and
                'cells' in notebook_data['ipynb']):
                
                all_cells = notebook_data['ipynb']['cells']
                print(f"✅ Google Colab: {len(all_cells)}セル取得")
                return all_cells
            else:
                print("❌ Google Colab: Notebook構造が取得できませんでした")
                return []
                
        except Exception as e:
            print(f"❌ Google Colab API エラー: {str(e)}")
            return []
    
    def get_notebook_cells_vscode(self):
        """VS Code環境からノートブックファイルを読み込み"""
        try:
            # カレントディレクトリの.ipynbファイルを検索
            notebook_file = None
            ipynb_files = glob.glob("*.ipynb")
            
            if ipynb_files:
                # ファイル名パターンでマッチング
                for file in ipynb_files:
                    if "プログラミング言語Python" in file:
                        notebook_file = file
                        break
                
                # マッチしない場合は最初のファイルを使用
                if not notebook_file:
                    notebook_file = ipynb_files[0]
            
            if notebook_file and os.path.exists(notebook_file):
                with open(notebook_file, 'r', encoding='utf-8') as f:
                    notebook_json = json.load(f)
                
                if 'cells' in notebook_json:
                    all_cells = notebook_json['cells']
                    print(f"✅ VS Code: {len(all_cells)}セル取得（{notebook_file}）")
                    return all_cells
                else:
                    print("❌ VS Code: セル情報が見つかりません")
                    return []
            else:
                print("❌ VS Code: Notebookファイルが見つかりません")
                return []
                    
        except Exception as e:
            print(f"❌ VS Code ファイル読み込みエラー: {str(e)}")
            return []
    
    def get_notebook_cells_before_submit(self, problem_number):
        """
        指定された問題番号の送信ボタンより前のセルを取得（#@titleセル除外）
        create_submit_button(problem_number=X) を検索して位置を特定
        """
        try:
            print(f"🔍 環境検出: Google Colab = {self.env_detector.is_colab()}")
            
            # 環境に応じてセル取得
            if self.env_detector.is_colab():
                all_cells = self.get_notebook_cells_colab()
            else:
                all_cells = self.get_notebook_cells_vscode()
            
            if not all_cells:
                print("🔄 フォールバック: 空のセルリストを返します")
                return []
            
            # 指定された問題番号の送信ボタンを検索
            submit_button_index = None
            search_pattern = f"create_submit_button(problem_number={problem_number})"
            
            for i, cell in enumerate(all_cells):
                if cell.get('cell_type') == 'code' and 'source' in cell:
                    source = cell['source']
                    if isinstance(source, list):
                        source = ''.join(source)
                    if search_pattern in source:
                        submit_button_index = i
                        break
            
            # 送信ボタンより前のセルを取得
            if submit_button_index is not None:
                cells_before_submit = all_cells[:submit_button_index]
                print(f"✅ 問題{problem_number}送信ボタン前の{len(cells_before_submit)}セル（全{len(all_cells)}セル中）")
            else:
                # 共通プログラム実行セルより前を取得（フォールバック）
                for i, cell in enumerate(all_cells):
                    if cell.get('cell_type') == 'code' and 'source' in cell:
                        source = cell['source']
                        if isinstance(source, list):
                            source = ''.join(source)
                        if '送信処理用共通プログラム実行' in source:
                            cells_before_submit = all_cells[:i]
                            print(f"✅ フォールバック: 共通プログラム前の{len(cells_before_submit)}セル")
                            break
                else:
                    print(f"⚠️ 送信ボタンが見つからないため全セルを返します: {len(all_cells)}セル")
                    cells_before_submit = all_cells
            
            # #@titleで始まるセルを除外
            filtered_cells = self.filter_submission_cells(cells_before_submit)
            print(f"📋 送信対象セル: {len(filtered_cells)}セル（#@title除外後）")
            
            return filtered_cells
            
        except Exception as e:
            print(f"❌ セル内容取得エラー: {str(e)}")
            return []
    
    def save_request_packet(self, student_email, assignment_id):
        """現在のNotebookをリクエスト形式でファイル保存（デバッグ用）"""
        try:
            # Notebook内容取得
            if self.env_detector.is_colab():
                from google.colab import _message
                notebook_data = _message.blocking_request('get_notebook_info', request='', timeout_sec=10)
            else:
                # VS Code環境の場合は現在のファイルから読み込み
                notebook_data = {"cells": self.get_notebook_cells_vscode()}
            
            # リクエストデータ作成
            request_data = {
                'notebook': notebook_data,
                'student_email': student_email,
                'assignment_id': assignment_id,
                'notebook_path': '02_プログラミング言語Python/01_プログラミング言語Python.ipynb'
            }
            
            # ファイル保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"request_packet_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ リクエストパケット保存完了: {filename}")
            print(f"📦 ファイルサイズ: {len(json.dumps(request_data)):,} bytes")
            
        except Exception as e:
            print(f"❌ 保存エラー: {e}")