FakeTrace — Local development and testing

Bu repo, haber/metin/görsel analizleri için bir prototip sunar.

Hızlı kurulum

1) Sanal ortam oluşturup aktif edin (Windows örneği):

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Tesseract (OCR) yükleyin (pytesseract için):

- Windows: https://github.com/UB-Mannheim/tesseract/wiki
	veya Chocolatey ile:

```powershell
choco install tesseract
```

3) Demo model oluştur (isteğe bağlı, detector pipeline test için):

```powershell
python scripts/create_demo_model.py
```
Bu, `uploads/detector.pth` dosyasını oluşturur (küçük demo model).

4) Uçtan uca testleri çalıştırın (örnek çıktı `tests/output/` altında saklanır):

```powershell
python -c "from services.analyzer import analyze_text; print(analyze_text('örnek metin'))"
python -c "from services.detector import get_detector; d=get_detector(model_path='uploads/detector.pth'); print(d.detect_video('uploads/deneme_11.mp4'))"
```

5) Uygulamayı çalıştırma:

```powershell
python app.py
# ardından tarayıcıda http://127.0.0.1:5000 adresini açın
```

Notlar ve uyarılar

- `analyze_text` ve `check_factcheck_database` için opsiyonel `sentence-transformers` entegrasyonu eklenmiştir. İlk kullanımda model indirimi yapacaktır — internet bağlantısı ve biraz zaman gerektirir.
- `analyze_image` önce `pytesseract` deneyip yoksa `easyocr` ile fallback yapar. `pytesseract` kullanmak için sistemde Tesseract kurulu olmalıdır.
 - `analyze_image` önce `pytesseract` deneyip yoksa `easyocr` ile fallback yapar. `pytesseract` ve `opencv` ağır paketlerdir ve varsayılan Docker image'da yer almıyor — bunları kullanmak için lokal makinenize veya hedef sunucuya `requirements-optional.txt` içindekileri kurmanız gerekir.
- `scripts/create_demo_model.py` küçük bir demo model kaydeder. Gerçek derin sahte (deepfake) tespiti için uygun, eğitilmiş bir modele ihtiyaç vardır.
- PyTorch sürümünüzde `torch.load` güvenlik sınırlamaları (weights_only) olabilir; eğer `torch.load` ile kaydedilmiş model objeleri yüklenmiyorsa, modelin `state_dict()`'ını kullanmak/indirmek veya `torch.serialization.add_safe_globals` yöntemleri düşünülebilir.

İleri adımlar

- Gerçek bir deepfake modeli entegre etmek isterseniz model dosyasını `uploads/` içine koyun (ör. `detector.pth`) ve `/api/detect` endpoint'i otomatik olarak onu kullanmaya çalışacaktır.
- Tesseract veya `sentence-transformers` ile ilgili yardım isterseniz adım adım yükleme veya hız/performans tavsiyeleri verebilirim.