const chartConfig = {
  temperature: {min:30,max:90,threshold:65}, vibration: {min:0,max:9,threshold:4.5},
  rpm: {min:1150,max:1550}, current: {min:0,max:8,threshold:5.5}
};
const chartSamples = {};
function drawTrend(key, history, unit) {
  const svg=document.querySelector(`#line-${key}`).ownerSVGElement;
  svg.setAttribute('viewBox','0 0 440 200');
  svg.style.height='190px';
  const c=chartConfig[key], values=history.map(s=>s[key]);
  if(!values.length)return;
  const lo=Math.min(c.min,...values), hi=Math.max(c.max,...values);
  const start=Date.parse(history[0].timestamp), end=Date.parse(history.at(-1).timestamp);
  const x=t=>50+(Date.parse(t)-start)*370/Math.max(end-start,1000);
  const y=v=>160-(v-lo)*140/(hi-lo);
  svg.querySelectorAll('.axis').forEach(el=>el.remove());
  const add=(tag,attrs,text)=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);el.classList.add('axis');Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));if(text!==undefined)el.textContent=text;svg.append(el);return el;};
  for(let i=0;i<5;i++){
    const v=lo+(hi-lo)*i/4;
    add('line',{x1:50,x2:420,y1:y(v),y2:y(v),stroke:'#294051'});
    add('text',{x:44,y:y(v)+4,'text-anchor':'end',fill:'#96aabd','font-size':11},v.toFixed(key==='rpm'?0:1));
  }
  const time=t=>new Date(t).toLocaleTimeString(language==='zh'?'zh-CN':'en-GB',{hour12:false});
  for(const [t,anchor] of [[history[0].timestamp,'start'],[history.at(-1).timestamp,'end']])add('text',{x:x(t),y:184,'text-anchor':anchor,fill:'#96aabd','font-size':11},time(t));
  if(c.threshold!==undefined){
    add('line',{x1:50,x2:420,y1:y(c.threshold),y2:y(c.threshold),stroke:'#f3c775','stroke-dasharray':'5 4'});
    add('text',{x:418,y:y(c.threshold)-5,'text-anchor':'end',fill:'#f3c775','font-size':11},`${c.threshold} ${unit}`);
  }
  const line=document.querySelector(`#line-${key}`);
  line.setAttribute('points',history.map(s=>`${x(s.timestamp)},${y(s[key])}`).join(' '));svg.append(line);
  chartSamples[key]=history;
  if(!svg.dataset.interactive){
    svg.dataset.interactive='true';svg.setAttribute('tabindex','0');
    const tip=document.createElement('div');tip.className='chart-tip';tip.setAttribute('role','status');svg.after(tip);
    const show=index=>{const samples=chartSamples[key];const s=samples[Math.max(0,Math.min(samples.length-1,index))];tip.textContent=`${time(s.timestamp)} · ${s[key]} ${unit}`;};
    svg.onpointermove=e=>{const rect=svg.getBoundingClientRect();const frac=Math.max(0,Math.min(1,((e.clientX-rect.left)/rect.width*440-50)/370));const samples=chartSamples[key];const target=Date.parse(samples[0].timestamp)+frac*(Date.parse(samples.at(-1).timestamp)-Date.parse(samples[0].timestamp));let nearest=0;samples.forEach((s,i)=>{if(Math.abs(Date.parse(s.timestamp)-target)<Math.abs(Date.parse(samples[nearest].timestamp)-target))nearest=i;});svg.dataset.index=nearest;show(nearest);};
    svg.onfocus=()=>{svg.dataset.index=chartSamples[key].length-1;show(Number(svg.dataset.index));};
    svg.onkeydown=e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();svg.dataset.index=Math.max(0,Math.min(chartSamples[key].length-1,Number(svg.dataset.index||0)+(e.key==='ArrowLeft'?-1:1)));show(Number(svg.dataset.index));}};
  }
}
