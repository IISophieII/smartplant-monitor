const fields=[['temperature','温度','°C'],['vibration','振动','mm/s'],['rpm','转速','rpm'],['current','电流','A']];
const labels={normal:'正常',warning:'预警',critical:'异常'};
const $=id=>document.getElementById(id);
fields.forEach(([key,label,unit])=>{
  $('metrics').insertAdjacentHTML('beforeend',`<div class="metric"><label>${label}</label><strong><span id="${key}">—</span><small>${unit}</small></strong><i>● Motor 01 · 实时采样</i></div>`);
  $('charts').insertAdjacentHTML('beforeend',`<div class="chart"><label>${label} / ${unit} <span id="range-${key}"></span></label><svg viewBox="0 0 400 115" preserveAspectRatio="none" role="img" aria-label="${label}趋势"><polyline id="line-${key}" fill="none" stroke="#68dcb9" stroke-width="2"/></svg></div>`);
});
async function request(url,options){const r=await fetch(url,options);if(!r.ok)throw Error(`请求失败 (${r.status})`);return r.json();}
document.querySelectorAll('button').forEach(button=>button.onclick=async()=>{
  try{await request('/api/simulation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:button.dataset.mode})});await refresh();}
  catch(e){$('error').textContent=e.message;}
});
async function refresh(){
  try{
    const [state,history]=await Promise.all([request('/api/status'),request('/api/history?limit=120')]);
    $('connection').textContent=state.error?'● 采集异常':'● 服务已连接';
    $('error').textContent=state.error||'';
    $('mode').textContent=state.source==='modbus'?'Modbus TCP':state.mode==='normal'?'正常模拟':'渐进故障模拟 · 约 60 秒达到峰值';
    document.querySelectorAll('button').forEach(b=>b.disabled=state.source!=='simulator');
    const s=state.latest;if(!s)return;
    fields.forEach(([key])=>{
      $(key).textContent=s[key].toFixed(key==='rpm'?0:2);
      const values=history.map(x=>x[key]);if(!values.length)return;
      const low=Math.min(...values),high=Math.max(...values),span=Math.max(high-low,0.1);
      $(`line-${key}`).setAttribute('points',values.map((v,i)=>`${i*400/Math.max(values.length-1,1)},${105-(v-low)*95/span}`).join(' '));
      $(`range-${key}`).textContent=` · ${low.toFixed(1)}–${high.toFixed(1)}`;
    });
    $('gauge').textContent=s.health;$('gauge').style.borderColor=s.status==='normal'?'#4dccaa':s.status==='warning'?'#f3c775':'#ff8e8e';
    $('status').textContent=labels[s.status];$('status').className=s.status;
    $('reasons').replaceChildren(...(s.reasons.length?s.reasons:['当前数据处于合成正常基线范围']).map(x=>{const li=document.createElement('li');li.textContent=x;return li;}));
    $('margin').textContent=`模型决策值 ${s.anomaly_margin} · 小于 0 为异常`;
    $('updated').textContent=`最后采样 ${new Date(s.timestamp).toLocaleTimeString()}`;
    $('rows').replaceChildren(...history.slice(-6).reverse().map(row=>{const tr=document.createElement('tr');[new Date(row.timestamp).toLocaleTimeString(),row.temperature,row.vibration,row.rpm,row.current,labels[row.status]].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td);});tr.lastChild.className=row.status;return tr;}));
  }catch(e){$('connection').textContent='● 连接中断';$('error').textContent=e.message+'，将自动重试；当前显示可能已过期。';}
}
async function poll(){await refresh();setTimeout(poll,1000);}poll();
