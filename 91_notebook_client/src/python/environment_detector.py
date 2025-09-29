"""
環境検出モジュール - Google Colab vs VS Code 環境の判別
"""

class EnvironmentDetector:
    """実行環境の検出と管理を行うクラス"""
    
    def __init__(self):
        self._is_colab = None
        self._environment_info = None
    
    def detect_colab_environment(self):
        """Google Colab環境を検出"""
        if self._is_colab is None:
            try:
                import google.colab
                self._is_colab = True
            except ImportError:
                self._is_colab = False
        return self._is_colab
    
    def get_environment_info(self):
        """実行環境の詳細情報を取得"""
        if self._environment_info is None:
            is_colab = self.detect_colab_environment()
            self._environment_info = {
                "is_colab": is_colab,
                "environment": "Google Colab" if is_colab else "VS Code/Local",
                "supports_javascript": is_colab,
                "supports_widgets": True  # 両環境でipywidgetsは利用可能
            }
        return self._environment_info
    
    def is_colab(self):
        """Google Colab環境かどうかを判定"""
        return self.detect_colab_environment()
    
    def is_vscode(self):
        """VS Code/Local環境かどうかを判定"""
        return not self.detect_colab_environment()
    
    def supports_javascript(self):
        """JavaScript実行をサポートするかどうか"""
        return self.detect_colab_environment()
    
    def print_environment_info(self):
        """環境情報を表示"""
        info = self.get_environment_info()
        print(f"🔍 実行環境: {info['environment']}")
        print(f"   Google Colab: {info['is_colab']}")
        print(f"   JavaScript対応: {info['supports_javascript']}")
        print(f"   Widget対応: {info['supports_widgets']}")


