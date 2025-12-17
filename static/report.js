// FakeTrace - Rapor Sayfası JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // reportData değişkeni HTML'den geliyor
    if (typeof reportData === 'undefined') return;
    
    // Harita oluştur
        // Harita ve grafik kütüphanelerinin yüklü olduğundan emin ol
        const missingLibs = [];
        if (typeof L === 'undefined') missingLibs.push('Leaflet (harita)');
        if (typeof Chart === 'undefined') missingLibs.push('Chart.js (grafikler)');
        if (typeof vis === 'undefined' && typeof visjs === 'undefined') missingLibs.push('vis-network (ağ grafiği)');

        if (missingLibs.length > 0) {
            console.error('Eksik kütüphane:', missingLibs.join(', '));
            const grid = document.querySelector('.viz-grid');
            if (grid) {
                grid.innerHTML = `<div style="padding:20px;color:#ef4444;background:rgba(0,0,0,0.4);border-radius:8px">Görselleştirme kütüphaneleri yüklenemedi: ${missingLibs.join(', ')}. Lütfen internet bağlantınızı veya CDN erişimini kontrol edin.</div>`;
            }
            return;
        }

        // Harita oluştur
        try {
            initMap(reportData);
            initTimelineChart(reportData);
            initCountryChart(reportData);
            initNetworkGraph(reportData);
        } catch (err) {
            console.error('Visualization init error:', err);
            const grid = document.querySelector('.viz-grid');
            if (grid) {
                grid.innerHTML = '<div style="padding:20px;color:#ef4444;background:rgba(0,0,0,0.4);border-radius:8px">Görselleştirme başlatılamadı. Konsolu kontrol edin.</div>';
            }
        }
    
});

// Yayılım Haritası
function initMap() {
    const mapContainer = document.getElementById('spreadMap');
        if (!mapContainer) return;
        if (!reportData.mapData || reportData.mapData.length === 0) {
            mapContainer.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8">Yayılma noktası bulunamadı</div>';
            return;
        }
    
    const map = L.map('spreadMap').setView([39.9334, 32.8597], 3);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);
    
        // Marker'ları ekle
        reportData.mapData.forEach((point, index) => {
            const color = index === 0 ? 'red' : 'blue';
            
            const marker = L.circleMarker([point.lat, point.lon], {
                radius: 10,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
    
            marker.bindPopup(`
                <strong>${point.name}</strong><br>
                Ülke: ${point.country}<br>
                Benzerlik: ${point.similarity}%
            `);
        });
    }
    
    // Zaman Çizelgesi Grafiği
    function initTimelineChart() {
        const ctx = document.getElementById('timelineChart');
            if (!ctx) return;
            if (!reportData.timelineData || reportData.timelineData.length === 0) {
                const parent = ctx.parentElement;
                if (parent) parent.innerHTML = '<div style="padding:20px;color:#94a3b8">Zaman çizelgesi için veri yok</div>';
                return;
            }
    
        const labels = reportData.timelineData.map((_, i) => `Nokta ${i + 1}`);
        const data = reportData.timelineData.map(item => item.similarity);
    
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Benzerlik Skoru',
                    data: data,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: '#0f172a' } }
                },
                scales: {
                    y: { beginAtZero: true, max: 100, ticks: { color: '#64748b' }, grid: { color: 'rgba(99,102,241,0.1)' } },
                    x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(99,102,241,0.1)' } }
                }
            }
        });
    }
    
    // Ülke Dağılımı Grafiği
    function initCountryChart() {
        const ctx = document.getElementById('countryChart');
            if (!ctx) return;
            if (!reportData.countryStats || Object.keys(reportData.countryStats).length === 0) {
                const parent = ctx.parentElement;
                if (parent) parent.innerHTML = '<div style="padding:20px;color:#94a3b8">Ülke dağılımı verisi yok</div>';
                return;
            }
    
        const labels = Object.keys(reportData.countryStats);
        const data = Object.values(reportData.countryStats);
    
        const colors = ['#6366f1', '#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];
    
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, labels.length),
                    borderColor: '#0f172a',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: '#0f172a' } } }
            }
        });
    }
    
    // Ağ Grafiği
    function initNetworkGraph() {
        const container = document.getElementById('networkGraph');
            if (!container) return;
            if (!reportData.networkData || !reportData.networkData.nodes || reportData.networkData.nodes.length <= 1) {
                container.innerHTML = '<div style="padding:20px;color:#94a3b8">Yayılma ağı verisi yok veya yetersiz</div>';
                return;
            }
    
        const nodes = new vis.DataSet(reportData.networkData.nodes.map(node => ({
            id: node.id,
            label: node.label,
            color: node.group === 'origin' ? '#ef4444' : '#6366f1',
            font: { color: '#0f172a' }
        })));
    
        const edges = new vis.DataSet(reportData.networkData.edges.map(edge => ({ from: edge.from, to: edge.to, color: { color: '#64748b' } })));
    
        const data = { nodes: nodes, edges: edges };
    
        const options = {
            physics: { stabilization: true, barnesHut: { gravitationalConstant: -2000, springLength: 100 } },
            nodes: { shape: 'dot', size: 20 }
        };
    
        new vis.Network(container, data, options);
    }