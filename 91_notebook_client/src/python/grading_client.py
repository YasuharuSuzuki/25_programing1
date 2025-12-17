"""
自動採点システムクライアントモジュール - CloudRunサービスへの送信
"""

import requests
import time
import json
from datetime import datetime
import threading
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
import asyncio

# Geminiのレスポンスが30秒超えることがあるため、長くしました
REQUEST_TIMEOUT = 180

class GradingClient:
    """自動採点システムとの通信を管理するクラス"""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.notebook_path = None
        self.headers = {'Content-Type': 'application/json'}
        self.cancel_retry = False
        
        # リトライ処理用のクラスフィールド
        self.current_submission_data = None
        self.current_attempt = 0
        self.max_retries = 1
        # self.retry_delay = 10
        self.retry_delay = 60
        self.success_callback = None
        self.error_callback = None
    
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
    
    def _save_error_response_to_file(self, response, attempt):
        """エラーレスポンスを詳細に保存（デバッグ用）"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_response_attempt{attempt}_{timestamp}.json"
            
            error_data = {
                "timestamp": timestamp,
                "attempt": attempt,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "response_text": response.text,
                "url": response.url,
                "request_headers": dict(response.request.headers) if response.request else None
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, ensure_ascii=False, indent=2)
            
            print(f"🔍 エラーレスポンス保存: {filename}")
            return filename, error_data
            
        except Exception as save_error:
            print(f"⚠️ エラーレスポンス保存失敗: {save_error}")
            return None, None
    
    def _display_error_from_response_text(self, error_data):
        response_data = json.loads(error_data['response_text'])
        pre_text = ""
        if 'error' in response_data:
            pre_text += f"  Error: {response_data['error']}\n"

            # tracebackがある場合
            if 'traceback' in response_data:
                pre_text += f"\n{'='*80}\n"
                pre_text += f"🚨 API ERROR TRACEBACK\n"
                pre_text += f"{'='*80}\n"
                pre_text += response_data['traceback']
                pre_text += f"{'='*80}\n"
                if 'environment' in response_data:
                    pre_text += f"Environment: {response_data['environment']}\n"
                if 'details' in response_data:
                    pre_text += f"Details: {response_data['details']}\n"
                pre_text += f"{'='*80}\n"

            # execution_logがある場合
            if 'log' in response_data:
                pre_text += f"\n{'-'*60}\n"
                pre_text += f"📊 EXECUTION LOG\n"
                pre_text += f"{'-'*60}\n"
                pre_text += response_data['log']
                pre_text += f"\n{'-'*60}\n"
        return pre_text


    def _display_error_details_widget(self, error_data, filename):
        """エラー詳細をWidgetで表示"""
        try:
            # エラー詳細表示用のHTML
            html_content = f"""
            <div style="border: 2px solid #ff6b6b; padding: 15px; margin: 10px 0; border-radius: 8px; background-color: #fff5f5;">
                <h3 style="color: #d63031; margin-top: 0;">🔍 サーバーエラー詳細</h3>
                <p><strong>ファイル保存:</strong> {filename}</p>
                <p><strong>ステータスコード:</strong> {error_data['status_code']}</p>
                <p><strong>URL:</strong> {error_data['url']}</p>
                <p><strong>タイムスタンプ:</strong> {error_data['timestamp']}</p>
                <details style="margin-top: 10px;">
                    <summary style="cursor: pointer; color: #d63031; font-weight: bold;">📋 レスポンスヘッダー</summary>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto;">{json.dumps(error_data['headers'], indent=2)}</pre>
                </details>
                <details style="margin-top: 10px;">
                    <summary style="cursor: pointer; color: #d63031; font-weight: bold;">📄 レスポンス本文</summary>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; max-height: 300px;">{self._display_error_from_response_text(error_data)}</pre>
                </details>
            </div>
            """
            display(HTML(html_content))
            
        except Exception as e:
            print(f"⚠️ エラー詳細Widget表示失敗: {e}")
            # フォールバック: テキスト出力
            print(f"📋 エラー詳細:")
            print(f"   ステータスコード: {error_data['status_code']}")
            print(f"   レスポンス: {error_data['response_text'][:500]}...")
    
    def show_retry_countdown_with_cancel2(self, retry_delay, attempt, max_retries, test_c_send, test_c_cancel):
        """リトライのカウントダウンとキャンセル機能を表示（コールバック方式）"""
        try:
            import threading
            from time import time

            print(f"🔄 送信関数 test_c_send を呼び出します...(1)")
            result = self.test_c_send()
            if result:  # 成功なら
                return  # その場で終了。必要な処理は送信処理の中で実装しておいてください。

            # リトライ回数を進めておく
            attempt += 1

            # リトライキャンセルフラグをリセット
            self.cancel_retry = False
            
            print(f"🔄 リトライ {attempt}/{max_retries} を {retry_delay} 秒後に実行します...")
            print("━" * 50)
            print("⚠️ リトライをキャンセルする方法:")
            print("1. 🛑 下のキャンセルボタンを押す")
            print("2. 🔴 または Kernel → Interrupt を選択")
            print("━" * 50)
            
            # プログレスバーとキャンセルボタン
            progress_bar = widgets.IntProgress(
                value=0,
                min=0,
                max=retry_delay,
                description=f'リトライ待機中 ({attempt}/{max_retries}):',
                bar_style='warning',
                orientation='horizontal'
            )
            
            cancel_button = widgets.Button(
                description="❌ キャンセル",
                button_style='danger',
                layout=widgets.Layout(width='120px')
            )
            
            # キャンセルボタンのイベントハンドラ
            def on_cancel_clicked(_):
                self.cancel_retry = True
                cancel_button.disabled = True
                cancel_button.description = "キャンセル済み"
                progress_bar.bar_style = 'danger'
                progress_bar.description = 'キャンセル済み:'
                print("🚫 リトライがキャンセルされました！")
                if test_c_cancel:
                    self.test_c_cancel()
            
            cancel_button.on_click(on_cancel_clicked)
            
            # UIを表示
            ui_box = widgets.VBox([progress_bar, cancel_button])
            display(ui_box)
            
            start_time = time()
            
            # 1秒間隔でのタイマーコールバック
            def on_timer():
                if self.cancel_retry:
                    return  # キャンセル済みなら何もしない
                
                # 経過時間を計算してプログレスバーを更新
                elapsed = time() - start_time
                remaining_seconds = max(0, retry_delay - int(elapsed))
                progress_value = min(int(elapsed), retry_delay)
                
                progress_bar.value = progress_value
                progress_bar.description = f'リトライまであと {remaining_seconds} 秒 ({attempt}/{max_retries}):'
                
                # 時間が経過していない場合は次のタイマーをセット
                if elapsed < retry_delay:

                    # 再度タイマーを開始
                    countdown_timer = threading.Timer(1.0, on_timer)
                    countdown_timer.start()

                else:

                    # 送信リトライまでのカウントダウン完了
                    progress_bar.value = retry_delay
                    progress_bar.bar_style = 'success'
                    progress_bar.description = f'リトライ {attempt}/{max_retries} 実行中:'
                    cancel_button.disabled = True
                    print(f"⏰ リトライ {attempt}/{max_retries} を実行します...")
                    print(f"🔄 送信関数 show_retry_countdown_with_cancel2 を呼び出します...(1)")

                    # リトライ回数がMaxに達したかどうかをチェックする
                    if attempt >= max_retries:
                        return

                    # あまりよろしくはないが、再帰的に呼び出す。
                    # こうすることで、再送信処理、引き続きリトライボタンの表示等が行える
                    self.show_retry_countdown_with_cancel2(retry_delay, attempt, max_retries,
                                                           test_c_send, test_c_cancel)

            # 最初のタイマーを開始
            countdown_timer = threading.Timer(1.0, on_timer)
            countdown_timer.start()
            
            # コールバック方式なので戻り値は不要
            
        except Exception as e:
            print(f"⚠️ リトライUI表示エラー: {e}")
            import traceback
            traceback.print_exc()
            
            # 最もシンプルなフォールバック
            print(f"📝 {retry_delay}秒後にリトライします...")
            print("🛑 キャンセルする場合は Kernel → Interrupt を選択してください")
            
            # time.sleep(retry_delay)
            # if on_complete_callback:
            #    on_complete_callback()

    def test_c_send(self):
        print("test_c_send() 送信処理のテストです。実際には送らず、sleep(3)します")
        time.sleep(3)
        print("test_c_send() 送信処理ダミー完了。sleep(3)しますた")

    def test_c_cancel(self):
        print("test_c_cancel() 送信キャンセル終了処理のテストです")

    def test_cancel_button(self, max_retry, retry_delay):
        """キャンセルボタンのテスト関数"""
        try:
            print("🧪 キャンセルボタンのテストを開始します...")
            
            self.cancel_retry = False
            
            test_button = widgets.Button(
                description="🧪 テストボタン",
                button_style='warning',
                layout=widgets.Layout(width='150px')
            )
            
            status_label = widgets.Label(value="ボタンを押してテストしてください")
            
            def on_test_clicked(_):
                self.cancel_retry = True
                status_label.value = "✅ ボタンが正常に動作しています！"
                test_button.disabled = True
                print("✅ テスト成功: ボタンクリックが検出されました")

                # 通信処理を実行しないテスト版
                # 第二引数に現在のリトライ数を渡すが、最初は０。なぜならリトライしていないため。
                self.show_retry_countdown_with_cancel2(retry_delay, 0, max_retry, self.test_c_send, self.test_c_cancel)

            test_button.on_click(on_test_clicked)
            
            ui_box = widgets.VBox([status_label, test_button])
            display(ui_box)
            
            print("ℹ️ 上のテストボタンを押して、Widget が正常に動作するか確認してください")
            
        except Exception as e:
            print(f"❌ テスト失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_retry_countdown_with_cancel(self, retry_delay, attempt, max_retries, send_func, cancel_func):
        """実際の送信処理用のリトライカウントダウン（show_retry_countdown_with_cancel2と同じ設計）"""
        try:
            import threading
            from time import time

            # 最初の送信処理を実行
            # print(f"🔄 送信処理を実行します... (試行 {attempt + 1}/{max_retries + 1})") # リトライしていないうちから回数表示するの辞めたい。
            if attempt == 0:
                print(f"🔄 送信処理を実行します...")
            else:
                print(f"🔄 送信処理を実行します... (試行 {attempt + 1}/{max_retries + 1})")

            result = send_func()
            if result:  # 成功なら
                return  # その場で終了。必要な処理は送信処理の中で実装済み

            # リトライ回数を進めておく
            attempt += 1

            # 最大リトライ回数チェック
            # if attempt >= max_retries:
            if attempt > max_retries:  # 超えた段階で終了とすること。
                print(f"❌ 最大リトライ回数({max_retries})に達しました")
                if self.error_callback:
                    self.error_callback("最大リトライ回数に達しました")
                return

            # リトライキャンセルフラグをリセット
            self.cancel_retry = False
            
            # print(f"🔄 リトライ {attempt + 1}/{max_retries} を {retry_delay} 秒後に実行します...")  # attempt+=1 してしまっているから多いです。
            print(f"🔄 リトライ {attempt}/{max_retries} を {retry_delay} 秒後に実行します...")
            print("━" * 50)
            print("⚠️ リトライをキャンセルする方法:")
            print("1. 🛑 下のキャンセルボタンを押す")
            print("2. 🔴 または Kernel → Interrupt を選択")
            print("━" * 50)
            
            # プログレスバーとキャンセルボタン
            progress_bar = widgets.IntProgress(
                value=0,
                min=0,
                max=retry_delay,
                # description=f'リトライ待機中 ({attempt + 1}/{max_retries}):',  # attempt+=1 してしまっているから多いです。
                description=f'リトライ待機中 ({attempt}/{max_retries}):',
                bar_style='warning',
                orientation='horizontal'
            )
            
            cancel_button = widgets.Button(
                description="❌ キャンセル",
                button_style='danger',
                layout=widgets.Layout(width='120px')
            )
            
            # キャンセルボタンのイベントハンドラ
            def on_cancel_clicked(_):
                self.cancel_retry = True
                cancel_button.disabled = True
                cancel_button.description = "キャンセル済み"
                progress_bar.bar_style = 'danger'
                progress_bar.description = 'キャンセル済み:'
                print("🚫 リトライがキャンセルされました！")
                if cancel_func:
                    cancel_func()
            
            cancel_button.on_click(on_cancel_clicked)
            
            # UIを表示
            ui_box = widgets.VBox([progress_bar, cancel_button])
            display(ui_box)
            
            start_time = time()
            
            # 1秒間隔でのタイマーコールバック
            def on_timer():
                if self.cancel_retry:
                    return  # キャンセル済みなら何もしない
                
                # 経過時間を計算してプログレスバーを更新
                elapsed = time() - start_time
                remaining_seconds = max(0, retry_delay - int(elapsed))
                progress_value = min(int(elapsed), retry_delay)
                
                progress_bar.value = progress_value
                # progress_bar.description = f'リトライまであと {remaining_seconds} 秒 ({attempt + 1}/{max_retries}):'   # attempt+=1 してしまっているから多いです。
                progress_bar.description = f'リトライまであと {remaining_seconds} 秒 ({attempt}/{max_retries}):'
                
                # 時間が経過していない場合は次のタイマーをセット
                if elapsed < retry_delay:
                    # 再度タイマーを開始
                    countdown_timer = threading.Timer(1.0, on_timer)
                    countdown_timer.start()
                else:
                    # 送信リトライまでのカウントダウン完了
                    progress_bar.value = retry_delay
                    progress_bar.bar_style = 'success'
                    # progress_bar.description = f'リトライ {attempt + 1}/{max_retries} 実行中:'   # attempt+=1 してしまっているから多いです。
                    progress_bar.description = f'リトライ {attempt}/{max_retries} 実行中:'
                    cancel_button.disabled = True
                    # print(f"⏰ リトライ {attempt + 1}/{max_retries} を実行します...")   # attempt+=1 してしまっているから多いです。
                    print(f"⏰ リトライ {attempt}/{max_retries} を実行します...")
                    
                    # 再帰的にリトライ実行
                    self._show_retry_countdown_with_cancel(
                        retry_delay, attempt, max_retries, send_func, cancel_func
                    )

            # 最初のタイマーを開始
            countdown_timer = threading.Timer(1.0, on_timer)
            countdown_timer.start()
            
        except Exception as e:
            print(f"⚠️ リトライUI表示エラー: {e}")
            import traceback
            traceback.print_exc()
            
            # 最もシンプルなフォールバック
            print(f"📝 {retry_delay}秒後にリトライします...")
            print("🛑 キャンセルする場合は Kernel → Interrupt を選択してください")
    
    
    def _send_to_grading_system_with_retry(self, submission_data, max_retries=1, retry_delay=60, success_callback=None, error_callback=None):
        """
        リトライ機能付きでCloudRunの自動採点システムに送信（新しい送信処理コールバック方式）
        
        Args:
            submission_data (dict): 送信データ
            max_retries (int): 最大リトライ回数
            retry_delay (int): リトライ間隔（秒）
            success_callback (callable): 成功時のコールバック関数
            error_callback (callable): エラー時のコールバック関数
        """
        # クラスフィールドに設定を保存
        self.current_submission_data = submission_data
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cancel_retry = False
        
        # コールバックを設定
        self.success_callback = success_callback
        self.error_callback = error_callback
        
        # 送信処理を定義（実際のHTTP通信を行う）
        def send_request():
            try:
                print(f"📡 送信処理実行中...")
                
                response = requests.post(
                    f"{self.base_url}/grade",
                    json=self.current_submission_data,
                    headers=self.headers,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if self.success_callback:
                        self.success_callback(result)
                    return True  # 成功
                else:
                    # エラーレスポンスの詳細保存
                    filename, error_data = self._save_error_response_to_file(response, 0)
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    print(f"❌ 送信エラー: {error_msg}")
                    
                    # エラー詳細をWidgetで表示
                    if error_data and filename:
                        self._display_error_details_widget(error_data, filename)
                    
                    return False  # 失敗
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"ネットワークエラー: {str(e)}"
                print(f"❌ 送信失敗: {error_msg}")
                return False  # 失敗
            except Exception as e:
                error_msg = f"予期しないエラー: {str(e)}"
                print(f"❌ 送信失敗: {error_msg}")
                return False  # 失敗
        
        # キャンセル処理
        def cancel_process():
            print("🚫 送信処理がキャンセルされました")
            if self.error_callback:
                self.error_callback("送信処理がユーザーによってキャンセルされました")
        
        # 新しいカウントダウン方式で送信開始（試行回数は0から開始）
        self._show_retry_countdown_with_cancel(
            self.retry_delay, 0, self.max_retries, send_request, cancel_process
        )
    
    def _handle_submission_success(self, result, student_email, problem_number, notebook_cells):
        """送信成功時の処理"""
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
            _ = viewer.save_result_to_file(result)

            viewer.display_grading_result_with_details(result, problem_number)
        except Exception as e:
            import traceback
            print(f"⚠️ 採点結果表示エラー: {e}")
            print(f"🔍 結果データ: {result}")
            print(f"📋 トレースバック:")
            traceback.print_exc()
    
    def _handle_submission_error(self, error_msg):
        """送信失敗時の処理"""
        print(f"❌ 送信失敗: {error_msg}")
        print("   ネットワーク接続とCloudRunサービスの状態を確認してください")
    
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
            
            # 成功時のコールバック（クロージャで変数をキャプチャ）
            def on_success(result):
                self._handle_submission_success(result, student_email, problem_number, notebook_cells)
            
            def on_error(error_msg):
                self._handle_submission_error(error_msg)
            
            # リトライ機能付きで送信（新しいコールバック方式）
            self._send_to_grading_system_with_retry(
                submission_data, 
                success_callback=on_success,
                error_callback=on_error
            )
                
        except Exception as e:
            import traceback
            error_msg = f"予期しないエラー: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"📋 トレースバック:")
            traceback.print_exc()
            return False, None, error_msg