import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

class BaseScraper:
    """空き家バンクスクレイパーの基底クラス"""
    
    def __init__(self, municipality_name, base_url):
        self.municipality_name = municipality_name
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.properties = []
    
    def fetch_page(self, url):
        """ページを取得"""
        try:
            print(f"取得中: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            time.sleep(3)  # 3秒待機（サーバー負荷軽減）
            return response.text
        except Exception as e:
            print(f"エラー: {url} - {e}")
            return None
    
    def parse(self, html):
        """HTMLを解析（各自治体でオーバーライド）"""
        raise NotImplementedError("parseメソッドを実装してください")
    
    def save_data(self, output_path):
        """データをJSON形式で保存"""
        data = {
            'municipality': self.municipality_name,
            'scraped_at': datetime.now().isoformat(),
            'count': len(self.properties),
            'properties': self.properties
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(self.properties)}件の物件を保存しました: {output_path}")
    
    def run(self):
        """スクレイピング実行"""
        raise NotImplementedError("runメソッドを実装してください")
