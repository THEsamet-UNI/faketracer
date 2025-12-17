document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('detectForm');
  const fileInput = document.getElementById('fileInput');
  const resultDiv = document.getElementById('result');

  form.addEventListener('submit', async function(e){
    e.preventDefault();
    resultDiv.innerHTML = 'Yükleniyor... Kuyruğa ekleniyor.';
    const file = fileInput.files[0];
    if(!file){ resultDiv.innerHTML = 'Lütfen bir dosya seçin.'; return; }
    const fd = new FormData(); fd.append('file', file);
    try{
      const res = await fetch('/api/detect_async', { method:'POST', body: fd });
      const json = await res.json();
      if(!res.ok){ resultDiv.innerText = 'Hata: ' + (json.message||json.error||res.status); return; }
      resultDiv.innerHTML = `İş eklendi. İş kimliği: <strong>${json.job_id}</strong>. Durum sorgulanıyor...`;
      // poll status
      const jobId = json.job_id;
      const poll = async () => {
        try{
          const s = await fetch('/api/job_status/' + jobId);
          const sj = await s.json();
          if(sj.status === 'finished'){
            resultDiv.innerHTML = `<h3>Sonuç</h3><pre style="white-space:pre-wrap">${JSON.stringify(sj.result, null, 2)}</pre>`;
          } else if(sj.status === 'queued' || sj.status === 'started'){
            resultDiv.innerHTML = `İş durum: ${sj.status}... (İş kimliği: ${jobId})`;
            setTimeout(poll, 2000);
          } else if(sj.status === 'failed'){
            resultDiv.innerHTML = `İş başarısız: ${sj.exc}`;
          } else {
            resultDiv.innerHTML = `Durum: ${sj.status}`;
          }
        }catch(err){ resultDiv.innerText = 'Durum sorgusu başarısız: ' + err; }
      };
      setTimeout(poll, 1500);
    }catch(err){
      resultDiv.innerText = 'İstek başarısız: ' + err;
    }
  });
});
