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
    
    def _display_single_code_cell(self, code, indent="      "):
        """
        単一のコードセルを行番号付きで表示
        
        Args:
            code (str): コード内容
            indent (str): インデント文字列
        """
        # 複数行のコードを行番号付きで表示
        lines = code.split('\n')
        if len(lines) > 1:
            for i, line in enumerate(lines, 1):
                print(f"{indent}{i:>3}| {line}")
        else:
            print(f"{indent}{code}")
    
    def _display_student_code_cells(self, student_code_cells, base_indent="    "):
        """
        学生の提出コードセルを表示
        
        Args:
            student_code_cells (list): 学生のコードセルリスト
            base_indent (str): 基本インデント
        """
        if not student_code_cells:
            print(f"{base_indent}💻 提出コード: (未検出)")
            return
        
        print(f"{base_indent}💻 提出コード ({len(student_code_cells)}個):")
        
        if len(student_code_cells) == 1:
            # 単一コードセルの場合
            self._display_single_code_cell(student_code_cells[0], f"{base_indent}  ")
            print()  # 空行を追加
        else:
            # 複数コードセルの場合
            for j, code in enumerate(student_code_cells, 1):
                print(f"{base_indent}  📝 コードセル{j}:")
                self._display_single_code_cell(code, f"{base_indent}    ")
                print()  # 空行を追加
    
    def display_grading_result(self, result_data):
        """
        採点結果をProblem単位で表示
        
        Args:
        """
        if not result_data or "notebook_results" not in result_data:
            print("❌ 採点結果データが無効です")
            return
        
        student_email = result_data.get("student_email", result_data.get("student_id", "不明"))
        assignment_id = result_data.get("assignment_id", "不明")
        timestamp = result_data.get("timestamp", "不明")
        
        notebook_result = result_data["notebook_results"]
        problems = notebook_result.get("problems", [])
        log = notebook_result.get("log", "")
        
        # 総合結果を計算
        total_earned = sum(p.get("student_score", 0) for p in problems)
        total_possible = sum(p.get("answer_full_score", 0) for p in problems)
        success_rate = (total_earned / total_possible * 100) if total_possible > 0 else 0
        
        print("="*80)
        print("🎯 採点結果レポート")
        print("="*80)
        print(f"📧 学生メール: {student_email}")
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
                student_score = problem.get("student_score", 0)
                answer_full_score = problem.get("answer_full_score", 0)
                
                # 合格判定
                if answer_full_score > 0:
                    success_rate_problem = (student_score / answer_full_score * 100)
                    status = "✅ 合格" if student_score == answer_full_score else "⚠️ 部分点" if student_score > 0 else "❌ 不合格"
                else:
                    success_rate_problem = 0
                    status = "❓ 採点不可"
                
                print(f"  Problem {problem_number:2d}: {student_score:3d}/{answer_full_score:3d}点 ({success_rate_problem:5.1f}%) {status}")
            
            print("-" * 60)
        else:
            print("\n⚠️ Problem別結果データが見つかりません")
        
        # 実行ログがある場合は表示
        if log and log.strip():
            print(f"\n🔍 実行ログ:")
            print("-" * 40)
            print(log)
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
            
        notebook_result = result_data.get("notebook_results")
        if not notebook_result:
            print("❌ 採点結果データが無効です")
            print(f"🔍 利用可能なキー: {list(result_data.keys())}")
            return
        
        student_email = result_data.get("student_email", result_data.get("student_id", "不明"))
        assignment_id = result_data.get("assignment_id", "不明")
        timestamp = result_data.get("timestamp", "不明")
        
        problems = notebook_result.get("problems", [])
        overall_feedback = notebook_result.get("overall_feedback", "")
        
        # 総合結果を計算
        total_earned = sum(p.get("student_score", 0) for p in problems)
        total_possible = sum(p.get("answer_full_score", 0) for p in problems)
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
                student_score = problem.get("student_score", 0)
                answer_full_score = problem.get("answer_full_score", 0)
                
                status = "✅" if student_score >= answer_full_score else "❌"
                rate = (student_score / answer_full_score * 100) if answer_full_score > 0 else 0
                
                # 送信した問題にマークを付ける
                if problem_number == submitted_problem_number:
                    marker = "🚀"  # 送信マーク
                    print(f"  問題 {problem_number:02d}: {student_score:3d}/{answer_full_score:3d}点 ({rate:5.1f}%) {status} {marker}")
                else:
                    print(f"  問題 {problem_number:02d}: {student_score:3d}/{answer_full_score:3d}点 ({rate:5.1f}%) {status}")
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
                    student_score = submitted_problem.get("student_score", 0)
                    answer_full_score = submitted_problem.get("answer_full_score", 0)
                    sub_problems = submitted_problem.get("sub_problems", [])
                    
                    print(f"\n🚀 問題 {submitted_problem_number}")
                    print(f"   得点: {student_score}/{answer_full_score}点")
                    print(f"   判定: {'✅ 正解' if student_score >= answer_full_score else '❌ 不正解'}")
                    
                    # SubProblemの詳細情報を表示
                    # 用語としては「SubProblem」と言われても学生さんわからないので、使わないでください。
                    if sub_problems:
                        print(f"\n🔍 詳細情報 ({len(sub_problems)}個):")
                        print("-" * 70)
                        
                        for idx, sub_problem in enumerate(sub_problems, 1):
                            # 類似度を取得（新仕様）
                            similarity = sub_problem["markdown_similarity"]
                            
                            # 学生マークダウンから問題タイトルを抽出（#を除去）
                            student_markdown = sub_problem.get("student_markdown_cell", "")
                            if student_markdown:
                                # マークダウンの#を除去し、最初の行をタイトルとして使用
                                title_line = student_markdown.split('\n')[0]
                                clean_title = title_line.replace('#', '').strip()
                            else:
                                clean_title = f"詳細 {idx}"
                            
                            print(f"\n  📋 詳細 {idx}: {clean_title}")
                            
                            # 学生側コードセル（提出コード）
                            student_code_cells = sub_problem.get("student_code_cells", [])
                            self._display_student_code_cells(student_code_cells)
                            
                            # 得点率（％表記）
                            student_score_rate = sub_problem.get("student_score_rate", 0.0)
                            print(f"    📊 得点率: {student_score_rate*100:.0f}%")
                            
                            # フィードバック
                            feedbacks = sub_problem.get("feedbacks", [])
                            if feedbacks:
                                print(f"    💬 フィードバック:")
                                for feedback_item in feedbacks:
                                    fb_messages = feedback_item.get("messages", [])
                                    for msg in fb_messages:
                                        print(f"      {msg}")
                            else:
                                print(f"    💬 フィードバック: 正解です！")
                            
                            # 類似度が0.9未満の場合、マークダウン文字列を警告付きで表記
                            if similarity < 0.9:
                                answer_markdown = sub_problem.get("answer_markdown_cell", "")
                                print(f"    ⚠️  マークダウン類似度が低いです（{similarity:.2f}）")
                                print(f"         問題文を誤って修正・削除した可能性があります")
                                print(f"         教員に相談してください")
                                if answer_markdown:
                                    print(f"         期待される問題文: {answer_markdown[:100]}...")
                                if student_markdown:
                                    print(f"         提出された問題文: {student_markdown[:100]}...")
                        
                        print("-" * 70)
                    else:
                        print(f"\n⚠️  サブ問題情報が利用できません")
                
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
        if not result_data or "notebook_results" not in result_data:
            display(HTML('<div style="color: red; font-weight: bold;">❌ 採点結果データが無効です</div>'))
            return
        
        student_email = result_data.get("student_email", result_data.get("student_id", "不明"))
        assignment_id = result_data.get("assignment_id", "不明")
        timestamp = result_data.get("timestamp", "不明")
        
        notebook_result = result_data["notebook_results"]
        problems = notebook_result.get("problems", [])
        log = notebook_result.get("log", "")
        
        # 総合結果を計算
        total_earned = sum(p.get("student_score", 0) for p in problems)
        total_possible = sum(p.get("answer_full_score", 0) for p in problems)
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
                <strong>📧 学生メール:</strong> {student_email}<br>
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
                student_score = problem.get("student_score", 0)
                answer_full_score = problem.get("answer_full_score", 0)
                
                if answer_full_score > 0:
                    success_rate_problem = (student_score / answer_full_score * 100)
                    if student_score == answer_full_score:
                        status = '✅ 合格'
                        status_class = 'status-pass'
                    elif student_score > 0:
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
                        <span>{student_score}/{answer_full_score}点 ({success_rate_problem:.1f}%)</span>
                        <span class="{status_class}">{status}</span>
                    </div>
                """
        else:
            html_content += '<div style="color: orange;">⚠️ Problem別結果データが見つかりません</div>'
        
        html_content += "</div></div>"
        
        # 実行ログがある場合は追加
        if log and log.strip():
            html_content += f"""
                <div style="margin-top: 15px;">
                    <strong>🔍 実行ログ:</strong>
                    <div class="execution-log">{log}</div>
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