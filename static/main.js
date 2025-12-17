// FakeTrace - Ana JavaScript Dosyası

document.addEventListener('DOMContentLoaded', function() {
    
    // Tab sistemi
    const tabBtns = document. querySelectorAll('. tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Tüm tabları deaktif yap
            tabBtns.forEach(b => b.classList. remove('active'));
            tabContents. forEach(c => c.classList. remove('active'));
            
            // Seçili tabı aktif yap
            this. classList.add('active');
            document.getElementById(tabId + '-tab').classList.add('active');
        });
    });
    
    // Dosya yükleme önizleme
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput. addEventListener('change', function(e) {
            const fileName = e.target. files[0]?.name;
            if (fileName) {
                const label = this.nextElementSibling;
                label.querySelector('span').textContent = fileName;
            }
        });
    }
    
    // Form gönderilirken loading göster
    const forms = document.querySelectorAll('. analyze-form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const btn = this.querySelector('button[type="submit"]');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analiz Ediliyor...';
            btn.disabled = true;
        });
    });
    
});