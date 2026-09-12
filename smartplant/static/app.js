const fields=[['temperature','Temperature','°C'],['vibration','Vibration','mm/s'],['rpm','Speed','rpm'],['current','Current','A']];
const labels={normal:'Normal',warning:'Warning',critical:'Critical'};
const $=id=>document.getElementById(id);
fields.forEach(([key,label,unit])=>{
  $('metrics').insertAdjacentHTML('beforeend',`<div class="metric"><label>${label}</label><strong><span id="${key}">—</span><small>${unit}</small></strong><i>● Motor 01 · Live telemetry</i></div>`);
  $('charts').insertAdjacentHTML('beforeend',`<div class="chart"><label>${label} / ${unit} <span id="range-${key}"></span></label><svg viewBox="0 0 400 115" preserveAspectRatio="none" role="img" aria-label="${label} trend"><polyline id="line-${key}" fill="none" stroke="#68dcb9" stroke-width="2"/></svg></div>`);
});
async function request(url,options){const r=await fetch(url,options);if(!r.ok)throw Error(`Request failed (${r.status})`);return r.json();}
document.querySelectorAll('button[data-mode]').forEach(button=>button.onclick=async()=>{
  try{await request('/api/simulation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:button.dataset.mode})});await refresh();applyLanguage();}
  catch(e){$('error').textContent=e.message;}
});
async function refresh(){
  try{
    const [state,history]=await Promise.all([request('/api/status'),request('/api/history?limit=120')]);
    $('connection').textContent=state.error?'● Collection error':'● Connected';
    $('error').textContent=state.error||'';
    $('mode').textContent=state.source==='modbus'?'Modbus TCP':state.mode==='normal'?'Normal simulation':'Progressive fault · Peaks in about 60 seconds';
    document.querySelectorAll('button[data-mode]').forEach(b=>b.disabled=state.source!=='simulator');
    const s=state.latest;if(!s){applyLanguage();return;}
    fields.forEach(([key])=>{
      $(key).textContent=s[key].toFixed(key==='rpm'?0:2);
      const values=history.map(x=>x[key]);if(!values.length)return;
      const low=Math.min(...values),high=Math.max(...values),span=Math.max(high-low,0.1);
      $(`line-${key}`).setAttribute('points',values.map((v,i)=>`${i*400/Math.max(values.length-1,1)},${105-(v-low)*95/span}`).join(' '));
      $(`range-${key}`).textContent=` · ${low.toFixed(1)}–${high.toFixed(1)}`;
    });
    $('gauge').textContent=s.health;$('gauge').style.borderColor=s.status==='normal'?'#4dccaa':s.status==='warning'?'#f3c775':'#ff8e8e';
    $('status').textContent=labels[s.status];$('status').className=s.status;
    $('reasons').replaceChildren(...(s.reasons.length?s.reasons:['Readings are within the synthetic normal baseline.']).map(x=>{const li=document.createElement('li');li.textContent=x;return li;}));
    $('margin').textContent=`Decision score ${s.anomaly_margin} · Below 0 indicates an anomaly`;
    $('updated').textContent=`Last sample ${new Date(s.timestamp).toLocaleTimeString(language === 'zh' ? 'zh-CN' : 'en-GB')}`;
    $('rows').replaceChildren(...history.slice(-6).reverse().map(row=>{const tr=document.createElement('tr');[new Date(row.timestamp).toLocaleTimeString(language === 'zh' ? 'zh-CN' : 'en-GB'),row.temperature,row.vibration,row.rpm,row.current,labels[row.status]].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td);});tr.lastChild.className=row.status;return tr;}));
  }catch(e){$('connection').textContent='● Disconnected';$('error').textContent=e.message+'. Retrying automatically; displayed data may be stale.';}
}
applyLanguage();
async function poll(){await refresh();applyLanguage();setTimeout(poll,1000);}poll();
