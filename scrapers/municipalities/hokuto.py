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
    
    def parse_detail_page(self, url, property_id):
        """物件詳細ページから情報を取得"""
        print(f"\n  詳細ページ取得: {property_id}")
        html = self.fetch_page(url)
        
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        detail_data = {
            'price': None,
            'price_raw': None,
            'land_area': None,
            'building_area': None,
            'built_year': None,
            'description': '',
            'images': []
        }
        
        # ページ全体のテキストから情報を抽出
        page_text = soup.get_text()
        
        for line in page_text.split('\n'):
            line = line.strip()
            
            # 価格
            if '売却価格' in line or '賃料' in line:
                detail_data['price_raw'] = line
                # 数字を抽出（例：380万円 → 3800000）
                price_match = re.search(r'(\d+)万円', line)
                if price_match:
                    detail_data['price'] = int(price_match.group(1)) * 10000
                print(f"    💰 {line}")
            
            # 土地面積
            if '土地：' in line:
                detail_data['land_area'] = line.replace('土地：', '').strip()
                print(f"    📏 {line}")
            
            # 建物面積
            if '建物：' in line:
                detail_data['building_area'] = line.replace('建物：', '').strip()
                print(f"    🏠 {line}")
            
            # 築年
            if '建築年：' in line:
                detail_data['built_year'] = line.replace('建築年：', '').strip()
                print(f"    📅 {line}")
        
        # 画像を取得
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if '/fs/' in src:  # 物件写真
                if not src.startswith('http'):
                    src = f"https://www.city.hokuto.yamanashi.jp{src}"
                detail_data['images'].append(src)
        
        print(f"    🖼️  画像: {len(detail_data['images'])}枚")
        
        return detail_data
    
    def parse(self, html):
        """HTMLから物件情報を抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== 物件を抽出中 ===")
        property_headings = soup.find_all('h3')
        
        for heading in property_headings:
            heading_text = heading.text.strip()
            
            if '空き家バンク登録物件' in heading_text:
                print(f"\n発見: {heading_text}")
                
                property_number = re.search(r'【(.*?)】', heading_text)
                property_id = property_number.group(1) if property_number else 'unknown'
                
                parent = heading.parent
                if parent and parent.name == 'a':
                    relative_url = parent.get('href')
                    full_url = f"https://www.city.hokuto.yamanashi.jp{relative_url}"
                    
                    property_data = {
                        'id': property_id,
                        'title': heading_text,
                        'municipality': self.municipality_name,
                        'url': full_url,
                        'type': '売却' if '売' in property_id else '賃貸',
                    }
                    
                    detail_data = self.parse_detail_page(full_url, property_id)
                    property_data.update(detail_data)
                    
                    self.properties.append(property_data)
                    print(f"  ✅ {property_id} 完了")
        
        print(f"\n" + "="*50)
        print(f"合計: {len(self.properties)}件の物件を抽出しました")
        print("="*50)
    
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