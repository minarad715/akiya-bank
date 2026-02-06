import sys
sys.path.append('../../')

from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class AzuminoScraper(BaseScraper):
    """長野県安曇野市の空き家バンクスクレイパー"""
    
    def __init__(self):
        super().__init__(
            municipality_name="長野県安曇野市",
            # 物件リストページに変更
            base_url="https://www.city.azumino.nagano.jp/site/akiya/"
        )
    
    def parse(self, html):
        """HTMLから物件情報を抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== ページ内容確認 ===")
        
        # 見出しを確認
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        print(f"\n見出し:")
        for h in headings[:10]:
            print(f"  {h.name}: {h.text.strip()[:60]}")
        
        # テーブルを確認
        tables = soup.find_all('table')
        print(f"\nテーブル数: {len(tables)}")
        
        # リンクを確認
        links = soup.find_all('a', href=True)
        print(f"\nリンク数: {len(links)}")
        print("\n物件らしいリンク:")
        
        for link in links[:20]:
            href = link.get('href', '')
            text = link.text.strip()
            
            # 物件番号や「売」「賃」などのキーワード
            if text and any(keyword in text for keyword in ['物件', '№', 'No', '売', '賃', '登録']):
                print(f"  {text[:60]} -> {href[:60]}")
        
        # PDFリンクがあるか
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf', re.I))
        if pdf_links:
            print(f"\nPDFリンク: {len(pdf_links)}件")
            for pdf in pdf_links[:5]:
                print(f"  {pdf.text.strip()[:60]}")
        
        # 本文から「物件」を含む段落を探す
        page_text = soup.get_text()
        print(f"\n「物件」を含む行:")
        for line in page_text.split('\n')[:50]:
            if '物件' in line:
                print(f"  {line.strip()[:80]}")
    
    def run(self):
        """スクレイピング実行"""
        print(f"=== {self.municipality_name} スクレイピング開始 ===")
        
        html = self.fetch_page(self.base_url)
        if html:
            self.parse(html)
        
        print("\n（データは保存しません - 構造確認のみ）")
        
        return self.properties

if __name__ == '__main__':
    scraper = AzuminoScraper()
    scraper.run()