"""
FakeTrace - Dezenformasyon Analiz Platformu
Ana uygulama dosyası
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os

# Modüllerimizi import et
from models. database import init_database, get_all_contents
from services.analyzer import analyze_url, analyze_text, analyze_image, get_analysis_report

# Flask uygulamasını oluştur
app = Flask(__name__)
app.secret_key = 'faketrace-secret-key-2024'

from auth.routes import auth_bp
app.register_blueprint(auth_bp)
from history.routes import history_bp
app.register_blueprint(history_bp)

# Upload klasörü ayarları
UPLOAD_FOLDER = os.path.join('/tmp', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


# ==================== SAYFALAR ====================

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


from utils.auth import login_required

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Analiz işlemini başlat"""
    
    # Hangi analiz türü seçilmiş?
    analysis_type = request. form.get('analysis_type', 'url')
    
    result = None
    
    user_id = session.get('user_id')
    if analysis_type == 'url':
        # URL analizi
        url = request.form.get('url', '').strip()
        if not url:
            return render_template('index.html', error="Lütfen bir URL girin!")
        result = analyze_url(url, user_id=user_id)
    elif analysis_type == 'text':
        # Metin analizi
        text = request.form.get('text', '').strip()
        if not text:
            return render_template('index.html', error="Lütfen analiz edilecek metni girin!")
        result = analyze_text(text, user_id=user_id)
    elif analysis_type == 'image':
        # Görsel analizi
        if 'image' not in request.files:
            return render_template('index.html', error="Lütfen bir görsel yükleyin!")
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', error="Dosya seçilmedi!")
        # Dosyayı kaydet
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        result = analyze_image(filepath, user_id=user_id)
    
    # Sonuç kontrolü
    if result and result. get('success'):
        return redirect(url_for('report', content_id=result['content_id']))
    else:
        error_msg = result.get('message', 'Analiz sırasında bir hata oluştu! ') if result else 'Bilinmeyen hata!'
        return render_template('index.html', error=error_msg)


@app.route('/report/<int:content_id>')
@login_required
def report(content_id):
    """Analiz raporu sayfası"""
    report_data = get_analysis_report(content_id)
    
    if not report_data: 
        return render_template('index.html', error="Rapor bulunamadı!")
    
    return render_template('report.html', report=report_data)


@app.route('/history')
@login_required
def history():
    """Geçmiş analizler (sadece girişli kullanıcıya özel)"""
    user_id = session.get('user_id')
    from models.database import get_contents_by_user_id
    contents = get_contents_by_user_id(user_id)
    return render_template('history.html', contents=contents)


@app.route('/about')
def about():
    """Hakkında sayfası"""
    return render_template('about.html')


# ==================== API ENDPOINTS ====================

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API üzerinden analiz"""
    data = request.get_json()
    
    if not data: 
        return jsonify({'error': 'Veri gönderilmedi'}), 400
    
    analysis_type = data.get('type', 'url')
    
    if analysis_type == 'url':
        result = analyze_url(data. get('url', ''))
    elif analysis_type == 'text':
        result = analyze_text(data.get('text', ''))
    else:
        return jsonify({'error':  'Geçersiz analiz türü'}), 400
    
    return jsonify(result)


# ==================== UYGULAMA BAŞLAT ====================

if __name__ == '__main__':
    print("🔧 Veritabanı kontrol ediliyor...")
    init_database()
    print("🚀 FakeTrace başlatılıyor...")
    print("📍 http://127.0.0.1:5000 adresinde çalışıyor")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

# Vercel için Flask app nesnesi export edilmeli
else:
    init_database()
