"""
ストレージ管理モジュール - localStorage/ファイル保存の統合管理
"""

import json
import os
from .environment_detector import EnvironmentDetector

class StorageManager:
    """環境に応じたストレージ管理を行うクラス"""
    
    def __init__(self, config_file=".student_email.json"):
        self.config_file = config_file
        self.env_detector = EnvironmentDetector()
    
    def save_to_storage(self, key, value):
        """環境に応じてlocalStorageまたはファイルに保存"""
        try:
            if self.env_detector.is_colab():
                return self._save_to_localstorage(key, value)
            else:
                return self._save_to_file(key, value)
        except Exception as e:
            print(f"⚠️ 保存エラー ({key}): {e}")
            return False
    
    def load_from_storage(self, key):
        """環境に応じてlocalStorageまたはファイルから読み込み"""
        try:
            if self.env_detector.is_colab():
                return self._load_from_localstorage(key)
            else:
                return self._load_from_file(key)
        except Exception as e:
            return None
    
    def _save_to_localstorage(self, key, value):
        """Google Colab: localStorage使用"""
        from google.colab import output
        output.eval_js(f"localStorage.setItem('{key}', '{value}');")
        return True
    
    def _load_from_localstorage(self, key):
        """Google Colab: localStorage読み込み"""
        from google.colab import output
        result = output.eval_js(f"localStorage.getItem('{key}') || ''")
        return result.strip() if result else None
    
    def _save_to_file(self, key, value):
        """VS Code: ファイル保存使用"""
        config_data = self._load_config_file()
        config_data[key] = value
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    
    def _load_from_file(self, key):
        """VS Code: ファイル読み込み使用"""
        config_data = self._load_config_file()
        return config_data.get(key, None)
    
    def _load_config_file(self):
        """設定ファイルの読み込み"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_email_address(self, email):
        """メールアドレスの保存"""
        return self.save_to_storage('studentEmail', email)
    
    def load_email_address(self):
        """保存されたメールアドレスの読み込み"""
        return self.load_from_storage('studentEmail')
    
    def clear_storage(self, key=None):
        """ストレージのクリア"""
        if key:
            # 特定のキーのみクリア
            if self.env_detector.is_colab():
                from google.colab import output
                output.eval_js(f"localStorage.removeItem('{key}');")
            else:
                config_data = self._load_config_file()
                config_data.pop(key, None)
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
        else:
            # 全てクリア
            if self.env_detector.is_colab():
                from google.colab import output
                output.eval_js("localStorage.clear();")
            else:
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)


