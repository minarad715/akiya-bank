import sys
sys.path.append('../../')

from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class AthomeTestScraper(BaseScraper):
    """アットホーム連携サイトのテストスクレイパー"""
    
    def __init__(self):
        super().__init__(
            municipality_name="アットホームテスト",
            # アットホーム空き家バンクのトップページ
            base_url="https://www.akiya-athome.jp/"
        )
    
    def parse(self, html):
        """HTMLから物件情報を抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== アットホームトップページ確認 ===")
        
        title = soup.find('title')
        if title:
            print(f"ページタイトル: {title.text.strip()}")
        
        headings = soup.find_all(['h1', 'h2', 'h3'])
        print(f"\n見出し数: {len(headings)}")
        for h in headings[:10]:
            print(f"  {h.name}: {h.text.strip()[:60]}")
        
        # 自治体リストへのリンクを探す
        links = soup.find_all('a', href=True)
        print(f"\n総リンク数: {len(links)}")
        
        print("\n都道府県・自治体へのリンク:")
        count = 0
        for link in links:
            href = link.get('href', '')
            text = link.text.strip()
            
            # 都道府県や自治体名を含むリンク
            if any(pref in text for pref in ['山梨', '長野', '静岡', '千葉', '北海道', '沖縄']):
                print(f"  {text[:40]} -> {href[:60]}")
                count += 1
                if count >= 15:
                    break
        
        # 物件検索へのリンク
        print("\n検索関連のリンク:")
        for link in links[:30]:
            href = link.get('href', '')
            text = link.text.strip()
            
            if any(keyword in text for keyword in ['検索', '探す', '物件', '一覧']):
                print(f"  {text[:40]} -> {href[:60]}")
    
    def run(self):
        """スクレイピング実行"""
        print(f"=== {self.municipality_name} スクレイピング開始 ===")
        
        html = self.fetch_page(self.base_url)
        if html:
            self.parse(html)
        
        print("\n（データは保存しません - 構造確認のみ）")
        
        return self.properties

if __name__ == '__main__':
    scraper = AthomeTestScraper()
    scraper.run()