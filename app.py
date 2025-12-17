"""
FakeTrace - Dezenformasyon Analiz Platformu
Ana uygulama dosyası
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
import os

# Modüllerimizi import et
from models. database import init_database, get_all_contents
from services.analyzer import analyze_url, analyze_text, analyze_image, get_analysis_report
from services.detector import get_detector
from services.model_manager import download_model, load_torch_model

# Flask uygulamasını oluştur
app = Flask(__name__)
app.secret_key = 'faketrace-secret-key-2024'

from auth.routes import auth_bp
app.register_blueprint(auth_bp)
from history.routes import history_bp
app.register_blueprint(history_bp)

# Upload klasörü ayarları
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path. exists(UPLOAD_FOLDER):
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


@app.route('/debug/report/<int:content_id>')
def debug_report(content_id):
    """Debug route: return the raw JSON of get_analysis_report for inspection."""
    report_data = get_analysis_report(content_id)
    if not report_data:
        return jsonify({'error': 'report not found'}), 404
    # Ensure serializable (fallback to str for any non-serializable values)
    import json as _json
    try:
        body = _json.dumps(report_data, default=str, ensure_ascii=False)
        return app.response_class(body, mimetype='application/json')
    except Exception as e:
        return jsonify({'error': 'serialization failed', 'detail': str(e)}), 500


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


@app.route('/detect')
def detect_page():
    return render_template('detect.html')


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


@app.route('/api/detect', methods=['POST'])
def api_detect():
    """Accepts a multipart file upload (form field 'file') and runs detection."""
    if 'file' not in request.files:
        return jsonify({'error':'no_file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error':'empty_filename'}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(save_path)
    except Exception as e:
        return jsonify({'error':'save_failed', 'detail': str(e)}), 500

    # instantiate detector (no model path by default; uses MockDetector)
    detector = get_detector()
    try:
        result = detector.detect_video(save_path)
    except Exception as e:
        return jsonify({'error':'detection_failed', 'detail': str(e)}), 500
    return jsonify(result)


@app.route('/api/download_model', methods=['POST'])
def api_download_model():
    """Download a model weights file to server. JSON body: { url, filename, sha256 (optional) }"""
    data = request.get_json() or {}
    url = data.get('url')
    filename = data.get('filename')
    sha256 = data.get('sha256')
    if not url or not filename:
        return jsonify({'error':'missing_params'}), 400
    dest = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    ok, msg = download_model(url, dest, expected_sha256=sha256)
    if not ok:
        return jsonify({'error':'download_failed', 'detail': msg}), 500
    # try load if torch available
    ok2, loaded = load_torch_model(dest)
    if not ok2:
        return jsonify({'status':'downloaded', 'path': dest, 'load': 'failed', 'detail': loaded})
    return jsonify({'status':'downloaded', 'path': dest, 'load':'ok'})


# ==================== UYGULAMA BAŞLAT ====================

if __name__ == '__main__':
    # Veritabanını oluştur
    print("🔧 Veritabanı kontrol ediliyor...")
    init_database()
    
    print("🚀 FakeTrace başlatılıyor...")
    print("📍 http://127.0.0.1:5000 adresinde çalışıyor")
    print("=" * 50)
    
    # Uygulamayı başlat
    app.run(debug=True, host='0.0.0.0', port=5000)
