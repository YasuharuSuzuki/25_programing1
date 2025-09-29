"""
採点結果表示モジュール - Problem単位での結果表示
"""

import json
from datetime import datetime
from IPython.display import display, HTML
import ipywidgets as widgets

class ResultViewer:
    """採点結果の表示を管理するクラス"""
    
    def __init__(self):
        pass
    
    def display_grading_result(self, result_data):
        """
        採点結果をProblem単位で表示
        
        Args:
            result_data (dict): 採点システムからのレスポンスデータ
                Expected format:
                {
                    "student_id": "student@example.com",
                    "assignment_id": "practice_problem_1",
                    "notebook_result": {
                        "problems": [
                            {
                                "problem_number": 1,
                                "points_earned": 20,
                                "points_total": 20
                            },
                            ...
                        ],
                        "execution_log": "..."
                    },
                    "timestamp": "2023-09-17T12:00:00Z"
                }
        """
        if not result_data or "notebook_result" not in result_data:
            print("❌ 採点結果データが無効です")
            return
        
        student_id = result_data.get("student_id", "不明")
        assignment_id = result_data.get("assignment_id", "不明")
        timestamp = result_data.get("timestamp", "不明")
        
        notebook_result = result_data["notebook_result"]
        problems = notebook_result.get("problems", [])
        execution_log = notebook_result.get("execution_log", "")
        
        # 総合結果を計算
        total_earned = sum(p.get("points_earned", 0) for p in problems)
        total_possible = sum(p.get("points_total", 0) for p in problems)
        success_rate = (total_earned / total_possible * 100) if total_possible > 0 else 0
        
        print("="*80)
        print("🎯 採点結果レポート")
        print("="*80)
        print(f"📧 学生ID: {student_id}")
        print(f"📝 課題ID: {assignment_id}")
        print(f"🕒 採点時刻: {timestamp}")
        print(f"📊 総合得点: {total_earned}/{total_possible} ({success_rate:.1f}%)")
        print("="*80)
        
        # Problem単位の詳細表示
        if problems:
            print("\n📋 Problem別詳細結果:")
            print("-" * 60)
            
            for i, problem in enumerate(problems, 1):
                problem_number = problem.get("problem_number", i)
                points_earned = problem.get("points_earned", 0)
                points_total = problem.get("points_total", 0)
                
                # 合格判定
                if points_total > 0:
                    success_rate_problem = (points_earned / points_total * 100)
                    status = "✅ 合格" if points_earned == points_total else "⚠️ 部分点" if points_earned > 0 else "❌ 不合格"
                else:
                    success_rate_problem = 0
                    status = "❓ 採点不可"
                
                print(f"  Problem {problem_number:2d}: {points_earned:3d}/{points_total:3d}点 ({success_rate_problem:5.1f}%) {status}")
            
            print("-" * 60)
        else:
            print("\n⚠️ Problem別結果データが見つかりません")
        
        # 実行ログがある場合は表示
        if execution_log and execution_log.strip():
            print(f"\n🔍 実行ログ:")
            print("-" * 40)
            print(execution_log)
            print("-" * 40)
        
        print("\n" + "="*80)
        print("📝 採点結果レポート終了")
        print("="*80)
    
    def display_grading_result_with_details(self, result_data, submitted_problem_number):
        """
        詳細表示ボタン付きの採点結果表示
        
        Args:
            result_data (dict): 採点システムからのレスポンスデータ
            submitted_problem_number (int): 送信した問題番号（該当問題にマークを付ける）
        """
        if not result_data:
            print("❌ 採点結果データがありません")
            return
            
        notebook_result = result_data.get("notebook_result")
        if not notebook_result:
            print("❌ 採点結果データが無効です")
            print(f"🔍 利用可能なキー: {list(result_data.keys())}")
            return
        
        student_id = result_data.get("student_id", "不明")
        assignment_id = result_data.get("assignment_id", "不明")
        timestamp = result_data.get("timestamp", "不明")
        
        problems = notebook_result.get("problems", [])
        overall_feedback = notebook_result.get("overall_feedback", "")
        
        # 総合結果を計算
        total_earned = sum(p.get("points_earned", 0) for p in problems)
        total_possible = sum(p.get("points_total", 0) for p in problems)
        success_rate = (total_earned / total_possible * 100) if total_possible > 0 else 0
        
        # 基本情報の表示
        print("="*80)
        print("🎯 採点結果サマリー")
        print("="*80)
        print(f"🕒 採点時刻: {timestamp}")
        print(f"📊 総合得点: {total_earned}/{total_possible} ({success_rate:.1f}%)")
        
        # Problem別の簡易表示
        if problems:
            print(f"\n📋 問題別結果 (問{submitted_problem_number}):")
            print("-" * 60)
            for problem in problems:
                problem_number = problem.get("problem_number", "?")
                points_earned = problem.get("points_earned", 0)
                points_total = problem.get("points_total", 0)
                
                status = "✅" if points_earned >= points_total else "❌"
                rate = (points_earned / points_total * 100) if points_total > 0 else 0
                
                # 送信した問題にマークを付ける
                if problem_number == submitted_problem_number:
                    marker = "🚀"  # 送信マーク
                    print(f"  問題 {problem_number:02d}: {points_earned:3d}/{points_total:3d}点 ({rate:5.1f}%) {status} {marker}")
                else:
                    print(f"  問題 {problem_number:02d}: {points_earned:3d}/{points_total:3d}点 ({rate:5.1f}%) {status}")
            print("-" * 60)
        
        print("="*80)
        
        # 詳細表示ボタンを作成
        details_button = widgets.Button(
            description='📋 詳細を表示',
            disabled=False,
            button_style='info',
            tooltip='Problem別の詳細情報とフィードバックを表示',
            layout=widgets.Layout(width='150px', margin='10px 0')
        )
        
        # 詳細表示エリア
        details_output = widgets.Output()
        
        def show_details(b):
            """詳細表示ボタンのハンドラ"""
            with details_output:
                details_output.clear_output()
                
                print(f"📋 問題 {submitted_problem_number} 詳細情報")
                print("="*80)
                
                # 送信した問題のみを表示
                submitted_problem = None
                for problem in problems:
                    if problem.get("problem_number") == submitted_problem_number:
                        submitted_problem = problem
                        break
                
                if submitted_problem:
                    points_earned = submitted_problem.get("points_earned", 0)
                    points_total = submitted_problem.get("points_total", 0)
                    feedback = submitted_problem.get("feedback", "")
                    error_message = submitted_problem.get("error_message", "")
                    
                    print(f"\n🚀 問題 {submitted_problem_number}")
                    print(f"   得点: {points_earned}/{points_total}点")
                    print(f"   判定: {'✅ 正解' if points_earned >= points_total else '❌ 不正解'}")
                    
                    if feedback and feedback.strip():
                        print(f"   💬 フィードバック: {feedback}")
                    
                    if error_message and error_message.strip():
                        print(f"   ⚠️  エラー: {error_message}")
                else:
                    print(f"❌ 問題 {submitted_problem_number} の詳細情報が見つかりませんでした")
                
                # 全体フィードバック表示
                if overall_feedback and overall_feedback.strip():
                    print(f"\n📝 総合フィードバック:")
                    print("="*60)
                    for line in overall_feedback.strip().split('\n'):
                        print(f"  {line}")
                    print("="*60)
                
                print("\n📄 詳細情報表示完了")
        
        # ボタンのイベントハンドラを設定
        details_button.on_click(show_details)
        
        # ウィジェットを表示
        display(widgets.VBox([
            details_button,
            details_output
        ], layout=widgets.Layout(
            border='1px solid #ddd',
            border_radius='8px',
            padding='10px',
            margin='10px 0'
        )))
    
    def display_grading_result_html(self, result_data):
        """
        採点結果をHTML形式で表示（Jupyter Notebook用）
        
        Args:
            result_data (dict): 採点システムからのレスポンスデータ
        """
        if not result_data or "notebook_result" not in result_data:
            display(HTML('<div style="color: red; font-weight: bold;">❌ 採点結果データが無効です</div>'))
            return
        
        student_id = result_data.get("student_id", "不明")
        assignment_id = result_data.get("assignment_id", "不明")
        timestamp = result_data.get("timestamp", "不明")
        
        notebook_result = result_data["notebook_result"]
        problems = notebook_result.get("problems", [])
        execution_log = notebook_result.get("execution_log", "")
        
        # 総合結果を計算
        total_earned = sum(p.get("points_earned", 0) for p in problems)
        total_possible = sum(p.get("points_total", 0) for p in problems)
        success_rate = (total_earned / total_possible * 100) if total_possible > 0 else 0
        
        # CSSスタイル
        style = """
        <style>
        .grading-result {
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        .result-header {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            margin: -20px -20px 15px -20px;
            border-radius: 6px 6px 0 0;
            font-weight: bold;
            font-size: 18px;
        }
        .result-summary {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .problem-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
        }
        .problem-row:last-child {
            border-bottom: none;
        }
        .status-pass { color: #4CAF50; font-weight: bold; }
        .status-partial { color: #FF9800; font-weight: bold; }
        .status-fail { color: #f44336; font-weight: bold; }
        .execution-log {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        </style>
        """
        
        # HTMLコンテンツ構築
        html_content = f"""
        {style}
        <div class="grading-result">
            <div class="result-header">
                🎯 採点結果レポート
            </div>
            
            <div class="result-summary">
                <strong>📧 学生ID:</strong> {student_id}<br>
                <strong>📝 課題ID:</strong> {assignment_id}<br>
                <strong>🕒 採点時刻:</strong> {timestamp}<br>
                <strong>📊 総合得点:</strong> {total_earned}/{total_possible} ({success_rate:.1f}%)
            </div>
            
            <div>
                <strong>📋 Problem別詳細結果:</strong>
                <div style="margin-top: 10px;">
        """
        
        # Problem別結果
        if problems:
            for i, problem in enumerate(problems, 1):
                problem_number = problem.get("problem_number", i)
                points_earned = problem.get("points_earned", 0)
                points_total = problem.get("points_total", 0)
                
                if points_total > 0:
                    success_rate_problem = (points_earned / points_total * 100)
                    if points_earned == points_total:
                        status = '✅ 合格'
                        status_class = 'status-pass'
                    elif points_earned > 0:
                        status = '⚠️ 部分点'
                        status_class = 'status-partial'
                    else:
                        status = '❌ 不合格'
                        status_class = 'status-fail'
                else:
                    success_rate_problem = 0
                    status = '❓ 採点不可'
                    status_class = 'status-fail'
                
                html_content += f"""
                    <div class="problem-row">
                        <span>Problem {problem_number}</span>
                        <span>{points_earned}/{points_total}点 ({success_rate_problem:.1f}%)</span>
                        <span class="{status_class}">{status}</span>
                    </div>
                """
        else:
            html_content += '<div style="color: orange;">⚠️ Problem別結果データが見つかりません</div>'
        
        html_content += "</div></div>"
        
        # 実行ログがある場合は追加
        if execution_log and execution_log.strip():
            html_content += f"""
                <div style="margin-top: 15px;">
                    <strong>🔍 実行ログ:</strong>
                    <div class="execution-log">{execution_log}</div>
                </div>
            """
        
        html_content += "</div>"
        
        display(HTML(html_content))
    
    def save_result_to_file(self, result_data, filename=None):
        """
        採点結果をJSONファイルに保存
        
        Args:
            result_data (dict): 採点システムからのレスポンスデータ
            filename (str): 保存ファイル名（Noneの場合は自動生成）
        
        Returns:
            str: 保存されたファイル名
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"grading_result_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 採点結果を保存しました: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ ファイル保存エラー: {e}")
            return None
    
    def load_result_from_file(self, filename):
        """
        JSONファイルから採点結果を読み込み
        
        Args:
            filename (str): 読み込むファイル名
        
        Returns:
            dict: 採点結果データ（エラーの場合はNone）
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            print(f"📂 採点結果を読み込みました: {filename}")
            return result_data
            
        except Exception as e:
            print(f"❌ ファイル読み込みエラー: {e}")
            return None