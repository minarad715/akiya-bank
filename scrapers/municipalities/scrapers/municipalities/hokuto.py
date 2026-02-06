import sys
sys.path.append('../../')

from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class HokutoScraper(BaseScraper):
    """山梨県北杜市の空き家バンクスクレイパー"""
    
    def __init__(self):
        super().__init__(
            municipality_name="山梨県北杜市",
            base_url="https://www.city.hokuto.yamanashi.jp/teijyu_ijyu/bank/"
        )
    
    def parse(self, html):
        """HTMLから物件情報を抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # h3タグから物件を探す
        print("\n=== 物件を抽出中 ===")
        property_headings = soup.find_all('h3')
        
        for heading in property_headings:
            heading_text = heading.text.strip()
            
            # 「空き家バンク登録物件」を含むものだけ
            if '空き家バンク登録物件' in heading_text:
                print(f"発見: {heading_text}")
                
                # 物件番号を抽出（例：【売220】→ 220）
                property_number = re.search(r'【(.*?)】', heading_text)
                property_id = property_number.group(1) if property_number else 'unknown'
                
                # リンクを取得
                link_tag = heading.find('a')
                if link_tag:
                    relative_url = link_tag.get('href')
                    full_url = f"https://www.city.hokuto.yamanashi.jp{relative_url}"
                    
                    # 物件データを構築
                    property_data = {
                        'id': property_id,
                        'title': heading_text,
                        'municipality': self.municipality_name,
                        'url': full_url,
                        'type': '売却' if '売' in property_id else '賃貸',
                    }
                    
                    self.properties.append(property_data)
                    print(f"  ✅ 追加: {property_id} - {full_url}")
        
        print(f"\n合計: {len(self.properties)}件の物件を抽出しました")
    
    def run(self):
        """スクレイピング実行"""
        print(f"=== {self.municipality_name} スクレイピング開始 ===")
        
        html = self.fetch_page(self.base_url)
        if html:
            self.parse(html)
        
        output_path = '../../data/raw/hokuto.json'
        self.save_data(output_path)
        
        return self.properties

if __name__ == '__main__':
    scraper = HokutoScraper()
    scraper.run()