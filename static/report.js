// FakeTrace - Rapor Sayfası JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // reportData değişkeni HTML'den geliyor
    if (typeof reportData === 'undefined') return;
    
    // Harita oluştur
    initMap();
    
    // Grafikler oluştur
    initTimelineChart();
    initCountryChart();
    initNetworkGraph();
    
});

// Yayılım Haritası
function initMap() {
    const mapContainer = document.getElementById('spreadMap');
    if (! mapContainer || !reportData.mapData) return;
    
    const map = L.map('spreadMap').setView([39.9334, 32.8597], 3);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);
    
    // Marker'ları ekle
    reportData.mapData. forEach((point, index) => {
        const color = index === 0 ? 'red' : 'blue';
        
        const marker = L.circleMarker([point.lat, point.lon], {
            radius: 10,
            fillColor: color,
            color: '#fff',
            weight:  2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
        
        marker.bindPopup(`
            <strong>${point.name}</strong><br>
            Ülke: ${point.country}<br>
            Benzerlik: ${point. similarity}%
        `);
    });
}

// Zaman Çizelgesi Grafiği
function initTimelineChart() {
    const ctx = document.getElementById('timelineChart');
    if (!ctx || !reportData.timelineData) return;
    
    const labels = reportData.timelineData.map((item, i) => `Nokta ${i + 1}`);
    const data = reportData.timelineData. map(item => item.similarity);
    
    new Chart(ctx, {
        type:  'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Benzerlik Skoru',
                data: data,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                fill: true,
                tension:  0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#64748b' },
                    grid: { color: 'rgba(99, 102, 241, 0.1)' }
                },
                x: {
                    ticks: { color:  '#64748b' },
                    grid: { color: 'rgba(99, 102, 241, 0.1)' }
                }
            }
        }
    });
}

// Ülke Dağılımı Grafiği
function initCountryChart() {
    const ctx = document.getElementById('countryChart');
    if (!ctx || !reportData.countryStats) return;
    
    const labels = Object.keys(reportData.countryStats);
    const data = Object.values(reportData.countryStats);
    
    const colors = [
        '#6366f1', '#0ea5e9', '#22c55e', '#f59e0b', 
        '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'
    ];
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors. slice(0, labels.length),
                borderColor: '#0f172a',
                borderWidth: 2
            }]
        },
        options:  {
            responsive:  true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels:  { color: '#f1f5f9' }
                }
            }
        }
    });
}

// Ağ Grafiği
function initNetworkGraph() {
    const container = document.getElementById('networkGraph');
    if (!container || ! reportData.networkData) return;
    
    const nodes = new vis.DataSet(reportData.networkData. nodes. map(node => ({
        id: node.id,
        label: node.label,
        color:  node.group === 'origin' ? '#ef4444' : '#6366f1',
        font: { color: '#f1f5f9' }
    })));
    
    const edges = new vis.DataSet(reportData. networkData.edges. map(edge => ({
        from: edge.from,
        to: edge.to,
        color: { color: '#64748b' }
    })));
    
    const data = { nodes: nodes, edges: edges };
    
    const options = {
        physics:  {
            stabilization: true,
            barnesHut: {
                gravitationalConstant: -2000,
                springLength:  100
            }
        },
        nodes: {
            shape: 'dot',
            size: 20
        }
    };
    
    new vis. Network(container, data, options);
}