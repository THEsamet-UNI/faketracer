// FakeTrace - Rapor Sayfası JavaScript (clean, with fallbacks)

document.addEventListener('DOMContentLoaded', function() {
    const raw = document.getElementById('report-data');
    if (!raw) return;
    let reportData = {};
    try {
        reportData = JSON.parse(raw.textContent || raw.innerText || '{}');
    } catch (e) {
        console.error('Invalid report data JSON', e);
        return;
    }

    // detect libraries
    const hasLeaflet = typeof L !== 'undefined';
    const hasChart = typeof Chart !== 'undefined';
    const hasVis = typeof vis !== 'undefined' || typeof visjs !== 'undefined';
    const usingFallback = !(hasLeaflet && hasChart && hasVis);

    if (usingFallback) console.warn('Using fallback visualizers (missing CDNs).');

    try {
        if (hasLeaflet) initMap(reportData);
        else renderFallbackMap(reportData);

        if (hasChart) {
            initTimelineChart(reportData);
            initCountryChart(reportData);
        } else {
            renderFallbackTimeline(reportData);
            renderFallbackCountry(reportData);
        }

        if (hasVis) initNetworkGraph(reportData);
        else renderFallbackNetwork(reportData);
    } catch (err) {
        console.error('Visualization init error:', err);
        const grid = document.querySelector('.viz-grid');
        if (grid) grid.innerHTML = '<div style="padding:20px;color:#ef4444;background:rgba(0,0,0,0.4);border-radius:8px">Görselleştirme başlatılamadı. Konsolu kontrol edin.</div>';
    }
});

// --- Leaflet based map ---
function initMap(reportData) {
    const mapContainer = document.getElementById('spreadMap');
    if (!mapContainer) return;
    if (!reportData.mapData || reportData.mapData.length === 0) {
        mapContainer.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8">Yayılma noktası bulunamadı</div>';
        return;
    }
    // initialize map
    try {
        const map = L.map('spreadMap').setView([39.9334, 32.8597], 3);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(map);
        reportData.mapData.forEach((point, index) => {
            const color = index === 0 ? 'red' : 'blue';
            const marker = L.circleMarker([point.lat, point.lon], { radius: 8, fillColor: color, color: '#fff', weight: 1, opacity: 1, fillOpacity: 0.9 }).addTo(map);
            marker.bindPopup(`<strong>${point.name}</strong><br>Ülke: ${point.country}<br>Benzerlik: ${point.similarity}%`);
        });
    } catch (e) {
        console.error('Leaflet init error', e);
        renderFallbackMap(reportData);
    }
}

// --- Chart.js timeline ---
function initTimelineChart(reportData) {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;
    if (!reportData.timelineData || reportData.timelineData.length === 0) { ctx.parentElement && (ctx.parentElement.innerHTML = '<div style="padding:20px;color:#94a3b8">Zaman çizelgesi için veri yok</div>'); return; }
    const labels = reportData.timelineData.map((_,i)=>`Nokta ${i+1}`);
    const data = reportData.timelineData.map(d=>d.similarity);
    new Chart(ctx, { type:'line', data:{ labels, datasets:[{ label:'Benzerlik Skoru', data, borderColor:'#6366f1', backgroundColor:'rgba(99,102,241,0.08)', fill:true, tension:0.4 }] }, options:{ responsive:true } });
}

// --- Chart.js country chart ---
function initCountryChart(reportData) {
    const ctx = document.getElementById('countryChart');
    if (!ctx) return;
    const stats = reportData.countryStats || {};
    if (Object.keys(stats).length===0) { ctx.parentElement && (ctx.parentElement.innerHTML = '<div style="padding:20px;color:#94a3b8">Ülke dağılımı verisi yok</div>'); return; }
    const labels = Object.keys(stats); const data = Object.values(stats);
    const colors = ['#6366f1','#0ea5e9','#22c55e','#f59e0b','#ef4444','#8b5cf6','#ec4899','#14b8a6'];
    new Chart(ctx, { type:'doughnut', data:{ labels, datasets:[{ data, backgroundColor: colors.slice(0,labels.length), borderColor:'#0f172a', borderWidth:2 }] }, options:{ responsive:true } });
}

// --- vis-network graph ---
function initNetworkGraph(reportData) {
    const container = document.getElementById('networkGraph');
    if (!container) return;
    try {
        const data = { nodes: new vis.DataSet(reportData.network.nodes), edges: new vis.DataSet(reportData.network.edges) };
        new vis.Network(container, data, { nodes:{ shape:'dot', size:20 }, physics:{ stabilization:true } });
    } catch (e) { console.error('vis init error', e); renderFallbackNetwork(reportData); }
}

// ----------------- FALLBACK RENDERERS -----------------
function renderFallbackMap(reportData) {
    const mapContainer = document.getElementById('spreadMap'); if (!mapContainer) return;
    if (!reportData.mapData || reportData.mapData.length===0){ mapContainer.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8">Yayılma noktası bulunamadı</div>'; return; }
    const list = document.createElement('div'); list.style.display='grid'; list.style.gridTemplateColumns='repeat(auto-fill,minmax(220px,1fr))'; list.style.gap='10px';
    reportData.mapData.forEach(p=>{ const card=document.createElement('div'); card.style.padding='12px'; card.style.background='rgba(15,23,42,0.6)'; card.style.border='1px solid rgba(99,102,241,0.08)'; card.style.borderRadius='8px'; card.innerHTML=`<strong>${p.name}</strong><br><small>${p.country}</small><div style="margin-top:6px;color:#94a3b8">Benzerlik: ${p.similarity}%</div>`; list.appendChild(card); });
    mapContainer.innerHTML=''; mapContainer.appendChild(list);
}

function renderFallbackTimeline(reportData) {
    const canvas = document.getElementById('timelineChart'); if (!canvas) return;
    if (!reportData.timelineData || reportData.timelineData.length===0){ const parent=canvas.parentElement; if(parent) parent.innerHTML='<div style="padding:20px;color:#94a3b8">Zaman çizelgesi için veri yok</div>'; return; }
    canvas.width = canvas.clientWidth || 600; canvas.height = 240; const ctx = canvas.getContext('2d'); ctx.clearRect(0,0,canvas.width,canvas.height);
    const data = reportData.timelineData.map(d=>d.similarity); const max = Math.max(...data,100); const pad=30; const step=(canvas.width-pad*2)/(data.length-1||1);
    ctx.strokeStyle='#6366f1'; ctx.lineWidth=2; ctx.beginPath(); data.forEach((v,i)=>{ const x=pad+i*step; const y=canvas.height-pad-(v/max)*(canvas.height-pad*2); if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y); ctx.fillStyle='#94a3b8'; ctx.fillText(`N${i+1}`,x-8,canvas.height-8); }); ctx.stroke();
}

function renderFallbackCountry(reportData){ const canvas=document.getElementById('countryChart'); if(!canvas) return; const stats=reportData.countryStats||{}; const keys=Object.keys(stats); if(keys.length===0){ const p=canvas.parentElement; if(p) p.innerHTML='<div style="padding:20px;color:#94a3b8">Ülke dağılımı verisi yok</div>'; return;} canvas.width=canvas.clientWidth||400; canvas.height=200; const ctx=canvas.getContext('2d'); ctx.clearRect(0,0,canvas.width,canvas.height); const total=keys.reduce((s,k)=>s+stats[k],0); const barH=(canvas.height-20)/keys.length; keys.forEach((k,i)=>{ const val=stats[k]; const w=Math.round((val/total)*(canvas.width-120)); const y=10+i*barH; ctx.fillStyle='#6366f1'; ctx.fillRect(100,y+4,w,barH-8); ctx.fillStyle='#f1f5f9'; ctx.fillText(k,8,y+14); ctx.fillStyle='#94a3b8'; ctx.fillText(val,110+w+6,y+14); }); }

function renderFallbackNetwork(reportData){ const container=document.getElementById('networkGraph'); if(!container) return; const net=reportData.network || reportData.networkData; if(!net||!net.nodes||net.nodes.length<=1){ container.innerHTML='<div style="padding:20px;color:#94a3b8">Yayılma ağı verisi yok veya yetersiz</div>'; return;} const svgNS='http://www.w3.org/2000/svg'; const w=container.clientWidth||600; const h=300; const svg=document.createElementNS(svgNS,'svg'); svg.setAttribute('width',w); svg.setAttribute('height',h); const cx=w/2, cy=h/2, r=Math.min(w,h)/3; const n=net.nodes.length; net.edges.forEach(e=>{ const from=net.nodes.find(x=>x.id===e.from); const to=net.nodes.find(x=>x.id===e.to); if(!from||!to) return; const fi=net.nodes.indexOf(from), ti=net.nodes.indexOf(to); const fx=cx+r*Math.cos(2*Math.PI*fi/n), fy=cy+r*Math.sin(2*Math.PI*fi/n); const tx=cx+r*Math.cos(2*Math.PI*ti/n), ty=cy+r*Math.sin(2*Math.PI*ti/n); const line=document.createElementNS(svgNS,'line'); line.setAttribute('x1',fx); line.setAttribute('y1',fy); line.setAttribute('x2',tx); line.setAttribute('y2',ty); line.setAttribute('stroke','#94a3b8'); line.setAttribute('stroke-width','1.5'); svg.appendChild(line); }); net.nodes.forEach((node,i)=>{ const x=cx+r*Math.cos(2*Math.PI*i/n), y=cy+r*Math.sin(2*Math.PI*i/n); const circle=document.createElementNS(svgNS,'circle'); circle.setAttribute('cx',x); circle.setAttribute('cy',y); circle.setAttribute('r',14); circle.setAttribute('fill', node.group==='origin'?'#ef4444':'#6366f1'); svg.appendChild(circle); const text=document.createElementNS(svgNS,'text'); text.setAttribute('x',x+18); text.setAttribute('y',y+4); text.setAttribute('fill','#f1f5f9'); text.setAttribute('font-size','12'); text.textContent=node.label; svg.appendChild(text); }); container.innerHTML=''; container.appendChild(svg); }
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

        const usingFallback = missingLibs.length > 0;
        if (usingFallback) {
            console.warn('Viz libraries missing, using fallback renderers:', missingLibs.join(', '));
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
            try {
                if (!usingFallback) {
                    initMap(reportData);
                    initTimelineChart(reportData);
                    initCountryChart(reportData);
                    initNetworkGraph(reportData);
                } else {
                    // fallback renderers
                    renderFallbackMap(reportData);
                    renderFallbackTimeline(reportData);
                    renderFallbackCountry(reportData);
                    renderFallbackNetwork(reportData);
                }
            } catch (err) {
                console.error('Visualization init error:', err);
                const grid = document.querySelector('.viz-grid');
                if (grid) {
                    grid.innerHTML = '<div style="padding:20px;color:#ef4444;background:rgba(0,0,0,0.4);border-radius:8px">Görselleştirme başlatılamadı. Konsolu kontrol edin.</div>';
                }
            }
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