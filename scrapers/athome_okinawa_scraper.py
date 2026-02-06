import sys
from base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class AthomeOkinawaScraper(BaseScraper):
    """アットホーム沖縄の空き家バンクスクレイパー"""
    
    def __init__(self):
        super().__init__(
            municipality_name="沖縄県（アットホーム）",
            base_url="https://www.akiya-athome.jp/buy/47/"
        )
    
    def parse_detail_page(self, url, property_id):
        """物件詳細ページから情報を取得"""
        print(f"\n  詳細ページ取得: {property_id}")
        html = self.fetch_page(url)
        
        if not html:
            return {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        detail_data = {
            'land_area': None,
            'building_area': None,
            'built_year': None,
            'description': '',
            'images': []
        }
        
        page_text = soup.get_text()
        
        for line in page_text.split('\n'):
            line = line.strip()
            
            if '土地面積' in line or ('土地' in line and ('㎡' in line or '坪' in line)):
                detail_data['land_area'] = line
                print(f"    📏 {line[:60]}")
            
            if '建物面積' in line or ('建物' in line and ('㎡' in line or '坪' in line)):
                detail_data['building_area'] = line
                print(f"    🏠 {line[:60]}")
            
            if '築年' in line or '建築年' in line:
                detail_data['built_year'] = line
                print(f"    📅 {line[:60]}")
        
        # 画像を取得
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if src and not any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'btn', 'button']):
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    base_domain = re.search(r'https://[^/]+', url).group(0)
                    src = f"{base_domain}{src}"
                elif not src.startswith('http'):
                    base_domain = re.search(r'https://[^/]+', url).group(0)
                    src = f"{base_domain}/{src}"
                
                if src not in detail_data['images']:
                    detail_data['images'].append(src)
        
        print(f"    🖼️  画像: {len(detail_data['images'])}枚")
        
        return detail_data
    
    def parse(self, html):
        """HTMLから物件情報を抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== 物件を抽出中 ===")
        
        links = soup.find_all('a', href=True)
        
        processed_urls = set()
        
        for link in links:
            href = link.get('href', '')
            
            if '/bukken/detail/buy/' in href:
                if href in processed_urls:
                    continue
                processed_urls.add(href)
                
                property_id_match = re.search(r'/buy/(\d+)', href)
                property_id = property_id_match.group(1) if property_id_match else 'unknown'
                
                municipality_match = re.search(r'https://([^.]+)\.akiya-athome\.jp', href)
                municipality_code = municipality_match.group(1) if municipality_match else 'unknown'
                
                title = link.text.strip()
                if not title or title == '※ 詳細を見る':
                    parent = link.parent
                    if parent:
                        title = parent.get_text(strip=True).replace('※ 詳細を見る', '')[:100]
                
                print(f"\n発見: {title[:60]} (ID: {property_id})")
                
                # タイトルから価格を抽出
                price = None
                price_raw = None
                price_match = re.search(r'価格(\d+(?:,\d+)?)万円', title)
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    price = int(price_str) * 10000
                    price_raw = f"価格{price_match.group(1)}万円"
                    print(f"  💰 {price_raw}")
                
                property_data = {
                    'id': property_id,
                    'title': title or f"物件番号{property_id}",
                    'municipality': f"沖縄県{municipality_code}",
                    'url': href,
                    'type': '売買',
                    'price': price,
                    'price_raw': price_raw,
                }
                
                detail_data = self.parse_detail_page(href, property_id)
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
        
        output_path = '../data/raw/athome_okinawa.json'
        self.save_data(output_path)
        
        return self.properties

if __name__ == '__main__':
    scraper = AthomeOkinawaScraper()
    scraper.run()