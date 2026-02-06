import sys
sys.path.append('../../')

from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class IidaScraper(BaseScraper):
    """長野県飯田市の空き家バンクスクレイパー"""
    
    def __init__(self):
        super().__init__(
            municipality_name="長野県飯田市",
            base_url="https://www.city.iida.lg.jp/site/akiyabank/"
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
        
        page_text = soup.get_text()
        
        for line in page_text.split('\n'):
            line = line.strip()
            
            if ('価格' in line or '金額' in line or '売買' in line) and '万円' in line:
                detail_data['price_raw'] = line
                price_match = re.search(r'(\d+)万円', line)
                if price_match:
                    detail_data['price'] = int(price_match.group(1)) * 10000
                print(f"    💰 {line}")
            
            if '土地' in line and ('㎡' in line or '坪' in line or '平米' in line):
                detail_data['land_area'] = line
                print(f"    📏 {line}")
            
            if '建物' in line and ('㎡' in line or '坪' in line or '平米' in line):
                detail_data['building_area'] = line
                print(f"    🏠 {line}")
            
            if '築年' in line or '建築年' in line or ('建築' in line and '年' in line):
                detail_data['built_year'] = line
                print(f"    📅 {line}")
        
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if any(keyword in src.lower() for keyword in ['photo', 'image', 'img', 'pic', 'akiya']):
                if not src.startswith('http'):
                    src = f"https://www.city.iida.lg.jp{src}"
                detail_data['images'].append(src)
        
        print(f"    🖼️  画像: {len(detail_data['images'])}枚")
        
        return detail_data
    
    def parse(self, html):
        """HTMLから物件情報を抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== 物件を抽出中 ===")
        
        links = soup.find_all('a', href=True)
        
        for link in links:
            text = link.text.strip()
            href = link.get('href', '')
            
            if '空き家情報' in text and '物件番号' in text and '成約済' not in text:
                print(f"\n発見: {text[:60]}")
                
                property_match = re.search(r'物件番号[：:]\s*([^\s【]+)', text)
                property_id = property_match.group(1) if property_match else 'unknown'
                
                property_type = '売買' if '売買' in text else '賃貸' if '賃貸' in text else '不明'
                
                if not href.startswith('http'):
                    full_url = f"https://www.city.iida.lg.jp{href}"
                else:
                    full_url = href
                
                property_data = {
                    'id': property_id,
                    'title': text,
                    'municipality': self.municipality_name,
                    'url': full_url,
                    'type': property_type,
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
        
        output_path = '../../data/raw/iida.json'
        self.save_data(output_path)
        
        return self.properties

if __name__ == '__main__':
    scraper = IidaScraper()
    scraper.run()