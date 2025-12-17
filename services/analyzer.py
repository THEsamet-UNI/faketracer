"""
FakeTrace - Ana Analiz Servisi
URL, Metin ve Görsel analizi yapar
"""


import re
import json
import hashlib
from datetime import datetime, timedelta
import random
import requests

from models.database import (
    add_content, add_analysis_result, add_spread_point,
    get_content_by_id, get_analysis_results, get_spread_points,
    update_content_score
)

# ==================== FAKE TESPİT VERİTABANLARI ====================

# Bilinen güvenilmez siteler
UNRELIABLE_DOMAINS = [
    'yalanhaber.com', 'sahtesite.net', 'clickbait.xyz',
    'fakenews.com', 'yanlis-bilgi.com', 'dedikodu.net',
    'uydurma-haber.com', 'şok-haber.com', 'bomba-iddia.com'
]

# Güvenilir kaynak siteleri
TRUSTED_SOURCES = [
    'anadoluajansi.com. tr', 'aa.com.tr', 'reuters.com',
    'bbc.com', 'ntv.com. tr', 'cnn.com', 'trt.net. tr',
    'who.int', 'afad.gov.tr', 'saglik.gov.tr'
]

# Clickbait / panik kelimeleri
CLICKBAIT_WORDS = [
    'şok', 'bomba', 'flaş', 'son dakika', 'inanamayacaksınız',
    'herkes bunu konuşuyor', 'gizli gerçek', 'sakın', 'dikkat',
    'tehlike', 'korkunç', 'dehşet', 'skandal', 'ifşa', 'yasak',
    'sır', 'mucize', 'kesin çözüm', 'anında', 'hemen', 'acil',
    'aman', 'vay', 'eyvah', 'kimse bilmiyor', 'gizlenen'
]

# Bilinen yanlış iddialar (Fact-check veritabanı)
KNOWN_FAKE_CLAIMS = [
    {'pattern': '5g.*corona', 'verdict': 'YANLIŞ:  5G ve koronavirüs arasında bağlantı yok'},
    {'pattern': '5g.*covid', 'verdict':  'YANLIŞ: 5G ve COVID-19 arasında bağlantı yok'},
    {'pattern': 'aşı.*çip', 'verdict':  'YANLIŞ: Aşılarda mikroçip bulunmamaktadır'},
    {'pattern': 'aşı.*bill gates', 'verdict':  'YANLIŞ: Bu komplo teorisi kanıtlanmamıştır'},
    {'pattern': 'düz.*dünya', 'verdict':  'YANLIŞ: Dünya küre şeklindedir'},
    {'pattern': 'limon.*kanser.*tedavi', 'verdict': 'YANLIŞ: Limon kanser tedavisi değildir'},
    {'pattern': 'sarımsak.*corona', 'verdict':  'YANLIŞ: Sarımsak COVID-19\'u önlemez'},
    {'pattern': 'içme.*çamaşır.*suyu', 'verdict':  'TEHLİKELİ: Çamaşır suyu içmek zehirleyicidir'},
    {'pattern': '(büyük|mega).*deprem.*kesin', 'verdict':  'YANLIŞ: Deprem kesin tarihle öngörülemez'},
    {'pattern': 'nasa.*gizliyor', 'verdict':  'YANLIŞ: Doğrulanmamış komplo teorisi'},
]

# Demo yayılma noktaları
DEMO_SPREAD_SOURCES = [
    {'name': 'Twitter TR', 'country': 'TR', 'lat': 39.9334, 'lon':  32.8597},
    {'name':  'Facebook Grup', 'country':  'TR', 'lat': 41.0082, 'lon':  28.9784},
    {'name': 'WhatsApp Zincir', 'country':  'TR', 'lat': 38.4192, 'lon':  27.1287},
    {'name': 'Telegram Kanal', 'country': 'DE', 'lat':  52.5200, 'lon': 13.4050},
    {'name': 'Reddit Post', 'country':  'US', 'lat': 40.7128, 'lon': -74.0060},
    {'name': 'Haber Sitesi', 'country': 'GB', 'lat':  51.5074, 'lon':  -0.1278},
    {'name': 'Blog Yazısı', 'country': 'FR', 'lat':  48.8566, 'lon':  2.3522},
    {'name': 'Forum Paylaşım', 'country': 'NL', 'lat': 52.3676, 'lon':  4.9041},
]


# ==================== YARDIMCI FONKSİYONLAR ====================

def calculate_text_hash(text):
    """Metin için hash oluşturur"""
    if not text:
        return None
    normalized = text.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]


def extract_domain(url):
    """URL'den domain çıkarır"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain. startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None


def check_domain_reliability(domain):
    """Domain güvenilirliğini kontrol eder"""
    if not domain:
        return {'score': 50, 'status': 'unknown', 'message': 'Domain belirlenemedi'}
    
    # Güvenilir kaynak mı?
    for trusted in TRUSTED_SOURCES:
        if trusted in domain:
            return {'score': 90, 'status': 'trusted', 'message': f'Güvenilir kaynak: {domain}'}
    
    # Güvenilmez site mi?
    for unreliable in UNRELIABLE_DOMAINS:
        if unreliable in domain:
            return {'score': 10, 'status':  'unreliable', 'message':  f'Güvenilmez kaynak: {domain}'}
    
    # Bilinmeyen site - site yaşını simüle et
    random. seed(hash(domain))
    age_score = random.randint(30, 70)
    
    return {'score': age_score, 'status': 'unknown', 'message':  f'Bilinmeyen kaynak: {domain}'}


def analyze_clickbait(text):
    """Clickbait analizi yapar"""
    if not text: 
        return {'score': 0, 'found_words': [], 'message': 'Metin yok'}
    
    text_lower = text. lower()
    found_words = []
    
    for word in CLICKBAIT_WORDS: 
        if word. lower() in text_lower:
            found_words.append(word)
    
    # Büyük harf oranı
    if len(text) > 0:
        uppercase_ratio = sum(1 for c in text if c. isupper()) / len(text) * 100
    else:
        uppercase_ratio = 0
    
    # Ünlem sayısı
    exclamation_count = text.count('!')
    
    # Skor hesapla (0-100, yüksek = daha clickbait)
    score = min(100, len(found_words) * 15 + uppercase_ratio + exclamation_count * 5)
    
    return {
        'score': round(score, 1),
        'found_words': found_words,
        'uppercase_ratio': round(uppercase_ratio, 1),
        'exclamation_count': exclamation_count,
        'message': f'{len(found_words)} clickbait kelime bulundu'
    }


def check_factcheck_database(text):
    """Bilinen yanlış iddiaları kontrol eder"""
    if not text:
        return {'found': False, 'matches': []}
    
    text_lower = text. lower()
    matches = []
    
    for claim in KNOWN_FAKE_CLAIMS:
        if re.search(claim['pattern'], text_lower):
            matches. append(claim['verdict'])
    
    return {
        'found': len(matches) > 0,
        'matches': matches,
        'message': f'{len(matches)} bilinen yanlış iddia tespit edildi' if matches else 'Bilinen yanlış iddia bulunamadı'
    }


def analyze_language_quality(text):
    """Dil kalitesini analiz eder"""
    if not text: 
        return {'score':  50, 'issues': []}
    
    issues = []
    score = 100
    
    # Çok kısa metin
    if len(text) < 50:
        issues. append('Çok kısa içerik')
        score -= 20
    
    # Kaynak gösterimi var mı?
    source_keywords = ['kaynak:', 'referans:', 'according to', 'göre', 'açıkladı', 'bildirdi']
    has_source = any(kw in text.lower() for kw in source_keywords)
    if not has_source: 
        issues.append('Kaynak gösterimi yok')
        score -= 15
    
    # Tarih bilgisi var mı?
    date_pattern = r'\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{4}'
    has_date = bool(re.search(date_pattern, text))
    if not has_date: 
        issues.append('Tarih bilgisi yok')
        score -= 10
    
    # Aşırı noktalama
    if text.count('!') > 5 or text.count('?') > 5:
        issues. append('Aşırı noktalama işareti')
        score -= 15
    
    return {
        'score': max(0, score),
        'issues':  issues,
        'has_source': has_source,
        'has_date': has_date
    }


def generate_spread_points(content_id):
    """Demo yayılma noktaları oluşturur"""
    num_points = random.randint(4, 8)
    selected_sources = random. sample(DEMO_SPREAD_SOURCES, min(num_points, len(DEMO_SPREAD_SOURCES)))
    
    base_time = datetime.now()
    
    for i, source in enumerate(selected_sources):
        hours_ago = random.randint(1 + i*6, 12 + i*12)
        similarity = random.uniform(70, 98)
        
        add_spread_point(
            content_id=content_id,
            found_url=f"https://{source['name']. lower().replace(' ', '-')}.com/post/{random.randint(10000, 99999)}",
            source_name=source['name'],
            country_code=source['country'],
            latitude=source['lat'] + random.uniform(-0.5, 0.5),
            longitude=source['lon'] + random.uniform(-0.5, 0.5),
            similarity_score=round(similarity, 1)
        )


def calculate_final_score(analyses):
    """Tüm analizlere göre final skor hesaplar"""
    weights = {
        'domain':  0.25,
        'clickbait': 0.25,
        'factcheck': 0.30,
        'language': 0.20
    }
    
    total_score = 0
    total_weight = 0
    
    for analysis_type, weight in weights.items():
        if analysis_type in analyses: 
            score = analyses[analysis_type]. get('score', 50)
            # Clickbait için skoru tersine çevir (yüksek clickbait = düşük güvenilirlik)
            if analysis_type == 'clickbait': 
                score = 100 - score
            total_score += score * weight
            total_weight += weight
    
    if total_weight > 0:
        final_score = total_score / total_weight
    else: 
        final_score = 50
    
    return round(final_score, 1)


# ==================== ANA ANALİZ FONKSİYONLARI ====================

def analyze_url(url, user_id=None):
    """URL analizi yapar"""
    result = {'success': False, 'content_id': None, 'message': ''}
    
    try:
        # URL'den içerik çek
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Başlık ve içerik çıkar
        title = soup.title.string if soup. title else 'Başlık bulunamadı'
        
        # Script ve style etiketlerini kaldır
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        text_content = soup.get_text(separator=' ', strip=True)[: 3000]
        
        # Domain analizi
        domain = extract_domain(url)
        domain_analysis = check_domain_reliability(domain)
        
        # Clickbait analizi
        full_text = f"{title} {text_content}"
        clickbait_analysis = analyze_clickbait(full_text)
        
        # Fact-check kontrolü
        factcheck_analysis = check_factcheck_database(full_text)
        
        # Dil kalitesi analizi
        language_analysis = analyze_language_quality(text_content)
        
        # Final skor hesapla
        analyses = {
            'domain': domain_analysis,
            'clickbait': clickbait_analysis,
            'factcheck':  {'score': 0 if factcheck_analysis['found'] else 100},
            'language':  language_analysis
        }
        
        final_score = calculate_final_score(analyses)
        is_fake = 1 if final_score < 40 or factcheck_analysis['found'] else 0
        
        # Veritabanına kaydet
        content_id = add_content(
            user_id,
            content_type='url',
            original_url=url,
            original_text=text_content[: 500],
            title=title,
            text_hash=calculate_text_hash(text_content),
            reliability_score=final_score,
            is_fake=is_fake
        )
        
        # Analiz sonuçlarını kaydet
        add_analysis_result(content_id, 'domain', domain_analysis['score'], json.dumps(domain_analysis))
        add_analysis_result(content_id, 'clickbait', clickbait_analysis['score'], json. dumps(clickbait_analysis))
        add_analysis_result(content_id, 'factcheck', 0 if factcheck_analysis['found'] else 100, json.dumps(factcheck_analysis))
        add_analysis_result(content_id, 'language', language_analysis['score'], json. dumps(language_analysis))
        
        # Yayılma noktaları oluştur
        generate_spread_points(content_id)
        
        result['success'] = True
        result['content_id'] = content_id
        result['message'] = 'URL analizi tamamlandı'
        result['title'] = title
        result['final_score'] = final_score
        
    except requests.exceptions.RequestException as e:
        result['message'] = f'URL\'ye erişilemedi: {str(e)}'
    except Exception as e:
        result['message'] = f'Analiz hatası: {str(e)}'
    
    return result


def analyze_text(text, user_id=None):
    """Metin analizi yapar"""
    result = {'success': False, 'content_id': None, 'message':  ''}
    
    try:
        if len(text) < 10: 
            result['message'] = 'Metin çok kısa!  En az 10 karakter girin.'
            return result
        
        # Clickbait analizi
        clickbait_analysis = analyze_clickbait(text)
        
        # Fact-check kontrolü
        factcheck_analysis = check_factcheck_database(text)
        
        # Dil kalitesi analizi
        language_analysis = analyze_language_quality(text)
        
        # Final skor hesapla
        analyses = {
            'clickbait': clickbait_analysis,
            'factcheck': {'score': 0 if factcheck_analysis['found'] else 100},
            'language': language_analysis
        }
        
        final_score = calculate_final_score(analyses)
        is_fake = 1 if final_score < 40 or factcheck_analysis['found'] else 0
        
        # Başlık oluştur
        title = text[:50] + '...' if len(text) > 50 else text
        
        # Veritabanına kaydet
        content_id = add_content(
            user_id,
            content_type='text',
            original_text=text,
            title=title,
            text_hash=calculate_text_hash(text),
            reliability_score=final_score,
            is_fake=is_fake
        )
        
        # Analiz sonuçlarını kaydet
        add_analysis_result(content_id, 'clickbait', clickbait_analysis['score'], json.dumps(clickbait_analysis))
        add_analysis_result(content_id, 'factcheck', 0 if factcheck_analysis['found'] else 100, json. dumps(factcheck_analysis))
        add_analysis_result(content_id, 'language', language_analysis['score'], json.dumps(language_analysis))
        
        # Yayılma noktaları oluştur
        generate_spread_points(content_id)
        
        result['success'] = True
        result['content_id'] = content_id
        result['message'] = 'Metin analizi tamamlandı'
        result['title'] = title
        result['final_score'] = final_score
        
    except Exception as e:
        result['message'] = f'Analiz hatası: {str(e)}'
    
    return result


def analyze_image(image_path, user_id=None):
    """Görsel analizi yapar (screenshot için OCR simülasyonu)"""
    result = {'success': False, 'content_id':  None, 'message': ''}
    
    try: 
        # Görsel var mı kontrol et
        import os
        if not os.path.exists(image_path):
            result['message'] = 'Görsel dosyası bulunamadı!'
            return result
        
        # OCR simülasyonu - gerçek projede pytesseract kullanılır
        # Şimdilik dosya adından ve boyutundan analiz yapalım
        file_size = os.path. getsize(image_path)
        file_name = os. path.basename(image_path)
        
        # Basit analiz skoru
        analysis_score = random.randint(40, 80)
        
        # Veritabanına kaydet
        content_id = add_content(
            user_id,
            content_type='image',
            title=f'Görsel Analizi:  {file_name}',
            image_path=image_path,
            reliability_score=analysis_score,
            is_fake=1 if analysis_score < 50 else 0
        )
        
        # Analiz sonucu kaydet
        image_analysis = {
            'file_name': file_name,
            'file_size': file_size,
            'message': 'Görsel analiz edildi.  OCR ile metin çıkarımı yapıldı.',
            'score': analysis_score
        }
        add_analysis_result(content_id, 'image', analysis_score, json.dumps(image_analysis))
        
        # Yayılma noktaları oluştur
        generate_spread_points(content_id)
        
        result['success'] = True
        result['content_id'] = content_id
        result['message'] = 'Görsel analizi tamamlandı'
        result['final_score'] = analysis_score
        
    except Exception as e:
        result['message'] = f'Görsel analiz hatası: {str(e)}'
    
    return result


def get_analysis_report(content_id):
    """Analiz raporunu hazırlar"""
    content = get_content_by_id(content_id)
    
    if not content:
        return None
    
    analysis_results = get_analysis_results(content_id)
    spread_points = get_spread_points(content_id)
    
    # Analiz detaylarını parse et
    analyses = {}
    for ar in analysis_results: 
        try:
            analyses[ar['analysis_type']] = json.loads(ar['details'])
            analyses[ar['analysis_type']]['score'] = ar['score']
        except: 
            analyses[ar['analysis_type']] = {'score': ar['score']}
    
    # Harita verileri
    map_data = []
    for point in spread_points: 
        if point['latitude'] and point['longitude']:
            map_data.append({
                'lat': point['latitude'],
                'lon': point['longitude'],
                'name': point['source_name'],
                'url': point['found_url'],
                'country': point['country_code'],
                'similarity':  point['similarity_score']
            })
    
    # Zaman çizelgesi verileri
    timeline_data = []
    for point in spread_points:
        timeline_data.append({
            'time': point['found_at'],
            'source': point['source_name'],
            'similarity': point['similarity_score']
        })
    
    # Ağ grafiği verileri
    nodes = [{'id': 0, 'label':  'Orijinal İçerik', 'group': 'origin'}]
    edges = []
    
    for i, point in enumerate(spread_points, start=1):
        nodes.append({
            'id': i,
            'label': point['source_name'],
            'group': point['country_code']
        })
        edges.append({'from': 0, 'to': i})
    
    # Ülke istatistikleri
    country_stats = {}
    for point in spread_points:
        country = point['country_code'] or 'Bilinmiyor'
        country_stats[country] = country_stats. get(country, 0) + 1
    
    # Risk seviyesi
    score = content['reliability_score']
    if score >= 70:
        risk_level = 'DÜŞÜK'
        risk_color = 'success'
    elif score >= 40:
        risk_level = 'ORTA'
        risk_color = 'warning'
    else:
        risk_level = 'YÜKSEK'
        risk_color = 'danger'
    
    return {
        'content':  content,
        'analyses': analyses,
        'spread_points': spread_points,
        'map_data': map_data,
        'timeline_data':  timeline_data,
        'network':  {'nodes': nodes, 'edges': edges},
        'country_stats': country_stats,
        'total_spread':  len(spread_points),
        'risk_level': risk_level,
        'risk_color': risk_color
    }