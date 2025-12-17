// FakeTrace - Ana JavaScript Dosyası

document.addEventListener('DOMContentLoaded', function() {
    // Tab sistemi
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');

            // Tüm tabları deaktif yap
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Seçili tabı aktif yap
            this.classList.add('active');
            const target = document.getElementById(tabId + '-tab');
            if (target) target.classList.add('active');
        });
    });

    // Dosya yükleme önizleme
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                const label = this.nextElementSibling;
                if (label) label.querySelector('span').textContent = fileName;
            }
        });
    }

    // Form gönderilirken loading göster
    const forms = document.querySelectorAll('.analyze-form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const btn = this.querySelector('button[type="submit"]');
            if (btn) {
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analiz Ediliyor...';
                btn.disabled = true;
            }
        });
    });

    // Animate progress bars on pages including report
    const progressFills = document.querySelectorAll('.progress-fill');
    progressFills.forEach(el => {
        const width = el.dataset.width || el.getAttribute('data-width') || '0';
        // allow numeric or string percentage
        const w = parseFloat(width);
        if (!isNaN(w)) {
            el.style.transition = 'width 800ms ease';
            // small timeout to ensure transition
            setTimeout(() => { el.style.width = Math.max(0, Math.min(100, w)) + '%'; }, 50);
        }
    });

    // Animate similarity bars
    const similarityFills = document.querySelectorAll('.similarity-bar .fill');
    similarityFills.forEach(el => {
        const width = el.dataset.width || el.getAttribute('data-width') || '0';
        const w = parseFloat(width);
        if (!isNaN(w)) {
            el.style.transition = 'width 800ms ease';
            setTimeout(() => { el.style.width = Math.max(0, Math.min(100, w)) + '%'; }, 50);
        }
    });

});