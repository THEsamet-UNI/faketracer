# FakeTrace — Deepfake Tespit (Türkçe)

Bu dal (`feature/deepfake-detector`) projeye derin sahtecilik (deepfake) tespiti için ekler içerir. Ama dikkat: proje şu an gerçek bir üretim sınıflandırıcısı değil — bir iskelet ve örnek iş akışı sağlar.

Özet
- `services/video.py` : Video → kare (frame) çıkarma yardımcıları.
- `services/face.py` : Yüz algılama (MTCNN varsa kullanılır; yoksa OpenCV Haar cascade fallback).
- `services/detector.py` : `MockDetector` (basit laplacian tabanlı heuristik) ve `Detector` sınıfı. Gerçek model entegre edilebilir.
- `services/model_manager.py` : Model ağırlıklarını indirip doğrulama ve (isteğe bağlı) PyTorch ile yükleme yardımcıları.
- `/api/detect` : Video yükleyip tespit çalıştıran endpoint.
- `/detect` : Basit ön yüz (upload UI) — `templates/detect.html`, `static/detect.js`.

Kısa kullanım (development)
1. Sanal ortamı etkinleştirin ve bağımlılıkları yükleyin (Windows örneği):

```powershell
& venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Not: torch CPU/GPU kurulumları platforma göre değişir; resmi PyTorch talimatlarını izleyin.
```

2. Uygulamayı başlatın:

```powershell
python app.py
```

3. Tarayıcıda `http://127.0.0.1:5000/detect` adresine gidin, bir video yükleyin ve "Tespit Et" butonuna tıklayın.

Model ekleme (örnek)
- Eğer gerçek bir PyTorch modeliniz varsa, modeli sunucuya koyup `/api/download_model` ile indirebilirsiniz veya doğrudan `UPLOAD_FOLDER` içine yerleştirebilirsiniz.
- Örnek: POST JSON `{ "url": "https://.../model.pth", "filename": "detector.pth", "sha256": "..." }` ile `/api/download_model` çağrısı yapın.
- İndirildikten sonra `services/detector.get_detector(model_path)` çağırılarak model kullanılabilir.

Üretim/Deploy notları
- Ağır modeller için Railway/Vercel gibi platformlar uygun değildir (CPU/GPU sınırlamaları). Tavsiye: model inference servisini GPU destekli bir VM veya yönetilen bir model-serving (ör. AWS/GCP/Azure) üzerinde çalıştırın.
- Uzun süren görevlere (video işleme) arka plan kuyruğu (RQ/Celery + Redis/RabbitMQ) ekleyin; HTTP istekleri bloklamayın.

Etik ve sınırlamalar
- Hazır iskelet yalnızca başlangıç içindir. `MockDetector` gerçek tespit sağlamaz.
- Deepfake tespiti hatalara açıktır (yanlış pozitif/negatif). Sonuçlar karar verme için tek kaynak olarak kullanılmamalıdır.
- Gizlilik: kullanıcı verilerini (yüklenen videolar) saklarken açık izin ve veri politikalarına uyun.

İleri adımlar (öneriler)
- Güvenilir, açık kaynak bir deepfake tespit modelini entegre etmek (ör. Xception tabanlı modeller).
- Model ağırlıklarını otomatik indirme + doğrulama ve deployment dokümantasyonu.
- Background job kuyruğu ve test veri setleri ile doğruluk ölçümleri.

---
Geliştirmeye devam etmemi istiyorsanız hangi adımı yapmamı istersiniz? (A) Gerçek model entegrasyonu, (B) Arka plan görev kuyruğu, (C) Test/README genişletme ve örnekler, (D) Hepsi (sıralı).
