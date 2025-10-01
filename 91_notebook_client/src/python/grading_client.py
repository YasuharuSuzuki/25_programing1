"""
自動採点システムクライアントモジュール - CloudRunサービスへの送信
"""

import requests
import time
import json
from datetime import datetime

class GradingClient:
    """自動採点システムとの通信を管理するクラス"""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.notebook_path = None
        self.headers = {'Content-Type': 'application/json'}
    
    def set_grading_system_url(self, url):
        """採点システムのURLを設定"""
        self.base_url = url
        print(f"🔧 採点システムURL設定: {url}")
    
    def get_grading_system_url(self):
        """現在の採点システムURLを取得"""
        return self.base_url
    
    def set_notebook_path(self, notebook_path):
        """ノートブックパスを設定"""
        self.notebook_path = notebook_path
        print(f"📋 ノートブックパス設定: {notebook_path}")
    
    def get_notebook_path(self):
        """現在のノートブックパスを取得"""
        return self.notebook_path
    
    def create_submission_data(self, student_email, problem_number, notebook_cells):
        """送信データを構築"""
        return {
            "student_email": student_email,
            "assignment_id": f"practice_problem_{problem_number}",
            "notebook_path": self.notebook_path,
            "notebook": {
                "cells": notebook_cells,
                "metadata": {
                    "kernelspec": {
                        "name": "python3",
                        "display_name": "Python 3"
                    }
                }
            }
        }
    
    def save_submission_data_to_file(self, submission_data, problem_number):
        """送信データを自動保存（デバッグ用）"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"request_packet_p{problem_number:02d}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(submission_data, f, ensure_ascii=False, indent=2)
            
            print(f"🔍 送信データ保存: {filename} ({len(json.dumps(submission_data)):,} bytes)")
            return filename
            
        except Exception as save_error:
            print(f"⚠️ 自動保存エラー: {save_error}")
            return None
    
    def send_to_grading_system_with_retry(self, submission_data, max_retries=3, retry_delay=10):
        """
        リトライ機能付きでCloudRunの自動採点システムに送信
        
        Args:
            submission_data (dict): 送信データ
            max_retries (int): 最大リトライ回数
            retry_delay (int): リトライ間隔（秒）
        
        Returns:
            tuple: (success: bool, response_data: dict, error_message: str)
        """
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    print(f"🔄 リトライ {attempt}/{max_retries} （{retry_delay}秒後）...")
                    time.sleep(retry_delay)
                
                print(f"📡 送信試行 {attempt + 1}/{max_retries + 1}")
                
                response = requests.post(
                    f"{self.base_url}/grade",
                    json=submission_data,
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return True, result, None
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    print(f"❌ 送信エラー（試行 {attempt + 1}）: {error_msg}")
                    
                    if attempt < max_retries:
                        print(f"   {retry_delay}秒後にリトライします...")
                    else:
                        return False, None, error_msg
                        
            except requests.exceptions.RequestException as e:
                error_msg = f"ネットワークエラー: {str(e)}"
                print(f"❌ 送信失敗（試行 {attempt + 1}）: {error_msg}")
                
                if attempt < max_retries:
                    print(f"   {retry_delay}秒後にリトライします...")
                else:
                    return False, None, error_msg
                    
            except Exception as e:
                error_msg = f"予期しないエラー: {str(e)}"
                print(f"❌ 送信失敗（試行 {attempt + 1}）: {error_msg}")
                
                if attempt < max_retries:
                    print(f"   {retry_delay}秒後にリトライします...")
                else:
                    return False, None, error_msg
        
        return False, None, "最大リトライ回数に達しました"
    
    def submit_assignment(self, student_email, problem_number, notebook_cells, auto_save=True):
        """
        課題を自動採点システムに送信
        
        Args:
            student_email (str): 学生のメールアドレス
            problem_number (int): 問題番号
            notebook_cells (list): ノートブックセルデータ
            auto_save (bool): 送信前の自動保存を行うか
        
        Returns:
            tuple: (success: bool, result_data: dict, error_message: str)
        """
        try:
            print(f"📤 練習プログラム{problem_number}の解答を送信中...")
            
            # 送信データの構築
            submission_data = self.create_submission_data(student_email, problem_number, notebook_cells)
            
            # 自動保存（オプション）
            if auto_save:
                self.save_submission_data_to_file(submission_data, problem_number)
            
            # リトライ機能付きで送信
            success, result, error_msg = self.send_to_grading_system_with_retry(submission_data)
            
            if success:
                print(f"✅ 送信完了！")
                print(f"   メールアドレス: {student_email}")
                print(f"   ノートブック: {self.notebook_path}")
                print(f"   問題番号: {problem_number}")
                print(f"   送信セル数: {len(notebook_cells)}")
                print("")
                print("🎉 採点が完了しました")
                
                # 採点結果の保存と表示
                try:
                    from .result_viewer import ResultViewer
                    viewer = ResultViewer()
                    
                    # 結果をファイルに保存
                    saved_file = viewer.save_result_to_file(result)
                    if saved_file:
                        print(f"💾 採点結果を保存しました: {saved_file}")
                    
                    viewer.display_grading_result_with_details(result, problem_number)
                except Exception as e:
                    import traceback
                    print(f"⚠️ 採点結果表示エラー: {e}")
                    print(f"🔍 結果データ: {result}")
                    print(f"📋 トレースバック:")
                    traceback.print_exc()

                return True, result, None
            else:
                print(f"❌ 送信失敗: {error_msg}")
                print("   ネットワーク接続とCloudRunサービスの状態を確認してください")
                return False, None, error_msg
                
        except Exception as e:
            import traceback
            error_msg = f"予期しないエラー: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"📋 トレースバック:")
            traceback.print_exc()
            return False, None, error_msg