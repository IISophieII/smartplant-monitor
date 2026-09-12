const languageButton = document.getElementById('language');
let language = 'en';
try { language = localStorage.getItem('smartplant-language') || (navigator.language.startsWith('zh') ? 'zh' : 'en'); } catch {}
if (!['en', 'zh'].includes(language)) language = 'en';
const translations = [["Synthetic data demo · Health scores are heuristic indicators, not failure probabilities or safety assessments.", "合成数据演示 · 健康评分为启发式指标，非故障概率或工业安全结论。"], ["Collection failed. Retrying; showing the last successful sample, if available.", "采集失败，正在重试；显示的是最后一次成功数据"], ["Times shown in your local timezone · Stored locally in SQLite", "所有时间显示为本地时间 · 数据保存在本地 SQLite"], ["Follow every change in your equipment with live telemetry.", "从实时数据，观察设备状态的每一次变化。"], [". Retrying automatically; displayed data may be stale.", "，将自动重试；当前显示可能已过期。"], ["Readings are within the synthetic normal baseline.", "当前数据处于合成正常基线范围"], ["Vibration exceeds the demo threshold of 4.5 mm/s", "振动超过演示阈值 4.5 mm/s"], ["Temperature exceeds the demo threshold of 65°C", "温度超过演示阈值 65°C"], ["Progressive fault · Peaks in about 60 seconds", "渐进故障模拟 · 约 60 秒达到峰值"], ["Deviation from the synthetic normal baseline", "偏离合成正常基线"], ["Current exceeds the demo threshold of 5.5 A", "电流超过演示阈值 5.5 A"], ["Last 120 samples · Updated every second", "最近 120 个采样点 · 每秒更新"], ["Isolation Forest + threshold rules", "Isolation Forest + 规则阈值"], ["Three-phase motor · Demo device", "三相异步电机 · 演示设备"], ["Below 0 indicates an anomaly", "小于 0 为异常"], ["Built with AI collaboration", "AI 协作开发"], ["Inject progressive fault", "注入渐进故障"], ["Learning & validation", "学习与验证平台"], ["Equipment monitoring", "设备运行监控"], ["Waiting for samples", "等待采样"], ["Normal simulation", "正常模拟"], ["Normal operation", "正常运行"], ["Operating trends", "运行趋势"], ["Equipment health", "设备健康"], ["Waiting for data", "等待数据"], ["Collection error", "采集异常"], ["Status details", "状态解释"], ["Recent samples", "最近采样记录"], ["No samples yet", "尚未采样"], ["Live telemetry", "实时采样"], ["${label} trend", "${label}趋势"], ["Request failed", "请求失败"], ["Decision score", "模型决策值"], ["Disconnected", "连接中断"], ["Sample time", "采样时间"], ["Last sample", "最后采样"], ["Temperature", "温度"], ["Connecting", "正在连接"], ["Connected", "服务已连接"], ["Vibration", "振动"], ["Overview", "设备总览"], ["API docs", "API 文档"], ["Critical", "异常"], ["Loading", "加载中"], ["Current", "电流"], ["Warning", "预警"], ["Status", "状态"], ["Normal", "正常"], ["Speed", "转速"]];
translations.push([' trend', '趋势']);
function translateText(text, target) {
  const pairs = (target === 'zh' ? translations : translations.map(([en, zh]) => [zh, en]))
    .sort((a, b) => b[0].length - a[0].length);
  // Replace each source span once; translated output is never translated again.
  const escape = value => Array.from(value, char => "\\^$.*+?()[]{}|".includes(char) ? "\\" + char : char).join("");
  const lookup = new Map(pairs);
  const pattern = new RegExp(pairs.map(([key]) => escape(key)).join('|'), 'g');
  return text.replace(pattern, match => lookup.get(match));
}
function applyLanguage() {
  document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (node.parentElement.closest('script, style, #language')) continue;
    node.textContent = translateText(node.textContent, language);
  }
  document.querySelectorAll('[aria-label]').forEach(el => {
    el.setAttribute('aria-label', translateText(el.getAttribute('aria-label'), language));
  });
  languageButton.textContent = language === 'zh' ? 'English' : '中文';
  languageButton.setAttribute('aria-label', language === 'zh' ? 'Switch to English' : '切换到中文');
}
languageButton.onclick = () => {
  language = language === 'zh' ? 'en' : 'zh';
  try { localStorage.setItem('smartplant-language', language); } catch {}
  applyLanguage();
};
applyLanguage();

