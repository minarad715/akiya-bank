import sys
sys.path.append('../../')

from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class ShimodaScraper(BaseScraper):
    """静岡県下田市の空き家バンクスクレイパー"""
    
    def __init__(self):
        super().__init__(
            municipality_name="静岡県下田市",
            base_url="https://www.city.shimoda.shizuoka.jp/category/100700akiyabank/"
        )
    
    def parse(self, html):
        """HTMLから物件情報を抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== ページ内容確認 ===")
        
        # 見出しを確認
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        print(f"\n見出し数: {len(headings)}")
        for h in headings[:10]:
            print(f"  {h.name}: {h.text.strip()[:60]}")
        
        # リンクを確認
        links = soup.find_all('a', href=True)
        print(f"\nリンク数: {len(links)}")
        print("\n物件らしいリンク:")
        
        count = 0
        for link in links:
            text = link.text.strip()
            href = link.get('href', '')
            
            if text and any(keyword in text for keyword in ['物件', '№', 'No', '売', '賃', '登録', '空き家']):
                print(f"  {text[:60]} -> {href[:60]}")
                count += 1
                if count >= 15:
                    break
    
    def run(self):
        """スクレイピング実行"""
        print(f"=== {self.municipality_name} スクレイピング開始 ===")
        
        html = self.fetch_page(self.base_url)
        if html:
            self.parse(html)
        
        print("\n（データは保存しません - 構造確認のみ）")
        
        return self.properties

if __name__ == '__main__':
    scraper = ShimodaScraper()
    scraper.run()