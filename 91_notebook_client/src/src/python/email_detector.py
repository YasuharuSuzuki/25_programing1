"""
メールアドレス自動取得モジュール - Google Colab環境でのメールアドレス自動検出
"""

import re
import subprocess
import json
import base64
from .environment_detector import EnvironmentDetector
from .storage_helper import StorageManager

class EmailDetector:
    """メールアドレスの検出と管理を行うクラス"""
    
    def __init__(self):
        self.env_detector = EnvironmentDetector()
        self.storage_manager = StorageManager()
        self.invalid_emails = ['default', 'none', 'null', 'undefined', '']
        self.email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def is_valid_email(self, email):
        """メールアドレスの有効性を検証"""
        if not email or not isinstance(email, str):
            return False
        
        if email.lower() in self.invalid_emails:
            return False
        
        return re.match(self.email_pattern, email) is not None
    
    def get_colab_email_oauth2(self):
        """OAuth2認証経由でメールアドレス取得"""
        try:
            from google.colab import auth
            import google.auth
            import google.auth.transport.requests
            
            print("   - 標準認証を実行中...")
            auth.authenticate_user()
            
            # 認証情報を取得
            credentials, project = google.auth.default()
            
            # トークン情報から直接取得を試行
            if hasattr(credentials, 'token'):
                print("   - OAuth2トークン情報を確認中...")
                # トークンをリフレッシュして最新情報を取得
                request = google.auth.transport.requests.Request()
                credentials.refresh(request)
                
                # ID トークンからユーザー情報を取得
                if hasattr(credentials, '_id_token') and credentials._id_token:
                    # JWT トークンを解析
                    token_parts = credentials._id_token.split('.')
                    if len(token_parts) >= 2:
                        # Base64デコード（パディング調整）
                        payload_b64 = token_parts[1]
                        payload_b64 += '=' * (4 - len(payload_b64) % 4)
                        payload = json.loads(base64.b64decode(payload_b64))
                        
                        if 'email' in payload:
                            email = payload['email']
                            if self.is_valid_email(email):
                                print(f"   ✅ OAuth2 ID トークンから取得: {email}")
                                return email
                            else:
                                print(f"   ❌ 無効なメールアドレス: {email}")
                        else:
                            print("   ❌ ID トークンにemailが含まれていません")
                    else:
                        print("   ❌ ID トークンの形式が不正です")
                else:
                    print("   ❌ ID トークンが利用できません")
            else:
                print("   ❌ OAuth2トークンが取得できません")
                
        except Exception as e:
            print(f"   ❌ OAuth2認証失敗: {str(e)}")
        
        return None
    
    def get_colab_email_gcloud(self):
        """gcloud auth経由でメールアドレス取得"""
        try:
            # gcloud auth list でアクティブなアカウントを取得
            result = subprocess.run(
                ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                email = result.stdout.strip()
                if self.is_valid_email(email):
                    print(f"   ✅ gcloud authから取得: {email}")
                    return email
                else:
                    print(f"   ❌ 無効なメールアドレス: {email}")
            else:
                print("   ❌ gcloud auth list が失敗しました")
                print(f"   stderr: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ❌ gcloud コマンドがタイムアウトしました")
        except FileNotFoundError:
            print("   ❌ gcloud コマンドが見つかりません")
        except Exception as e:
            print(f"   ❌ gcloud auth経由の取得失敗: {str(e)}")
        
        return None
    
    def get_colab_email_auto(self):
        """Google Colabからメールアドレスを自動取得"""
        print("🔍 メールアドレス自動取得を開始...")
        
        if not self.env_detector.is_colab():
            print("❌ Google Colab環境ではありません")
            return None
        
        try:
            # 最優先: 保存済みメールアドレスを確認
            print("📂 保存済みメールアドレス確認")
            saved_email = self.storage_manager.load_email_address()
            if saved_email and self.is_valid_email(saved_email):
                print(f"   ✅ 保存済みメールアドレス取得: {saved_email}")
                print("   📌 認証をスキップします")
                return saved_email
            elif saved_email:
                print(f"   ❌ 保存済みメールアドレスが無効: {saved_email}")
            else:
                print("   📂 保存済みメールアドレスがないため、認証を実行します")
            
            # 方法1: OAuth2認証経由（標準認証）
            print("📧 方法1: OAuth2認証経由（標準認証）")
            email = self.get_colab_email_oauth2()
            if email:
                return email
            
            # 方法2: gcloud auth経由
            print("📧 方法2: gcloud auth経由")
            email = self.get_colab_email_gcloud()
            if email:
                return email
            
            print("❌ すべてのメールアドレス取得方法が失敗しました")
            return None
            
        except Exception as e:
            print(f"❌ メール取得でエラー: {str(e)}")
            return None