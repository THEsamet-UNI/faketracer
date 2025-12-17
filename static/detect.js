document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('detectForm');
  const fileInput = document.getElementById('fileInput');
  const resultDiv = document.getElementById('result');

  form.addEventListener('submit', async function(e){
    e.preventDefault();
    resultDiv.innerHTML = 'Yükleniyor... Lütfen bekleyin.';
    const file = fileInput.files[0];
    if(!file){ resultDiv.innerHTML = 'Lütfen bir dosya seçin.'; return; }
    const fd = new FormData(); fd.append('file', file);
    try{
      const res = await fetch('/api/detect', { method:'POST', body: fd });
      const json = await res.json();
      if(!res.ok){ resultDiv.innerText = 'Hata: ' + (json.error||res.status); return; }
      // render basic summary
      let html = `<pre style="white-space:pre-wrap">${JSON.stringify(json, null, 2)}</pre>`;
      resultDiv.innerHTML = html;
    }catch(err){
      resultDiv.innerText = 'İstek başarısız: ' + err;
    }
  });
});
