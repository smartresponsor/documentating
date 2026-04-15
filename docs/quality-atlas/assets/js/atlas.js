(function () {
  const storageKey = 'quality-atlas-theme';
  const layoutKey = 'quality-atlas-documentating-layout';
  const charts = {};

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function applyTheme(theme) {
    const root = document.documentElement;
    if (theme === 'light' || theme === 'dark') root.setAttribute('data-theme', theme);
    else root.removeAttribute('data-theme');
    document.querySelectorAll('[data-theme-value]').forEach((button) => {
      const active = button.getAttribute('data-theme-value') === theme;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    setTimeout(() => Object.values(charts).forEach((chart) => chart && chart.resize()), 80);
  }

  async function loadJson(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw new Error('Unable to load ' + path);
    return response.json();
  }

  function renderPortfolio(data) {
    document.querySelectorAll('[data-portfolio-average]').forEach((n) => { n.textContent = data.summary.averageScore; });
    document.querySelectorAll('[data-repositories-tracked]').forEach((n) => { n.textContent = data.summary.repositoriesTracked; });
    document.querySelectorAll('[data-last-review]').forEach((n) => { n.textContent = data.summary.lastReview; });
    const el = document.getElementById('portfolio-score-chart');
    if (!el || !window.echarts) return;
    charts.portfolio = echarts.init(el);
    charts.portfolio.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 32, right: 18, bottom: 32, top: 20, containLabel: true },
      xAxis: { type: 'category', data: data.components.map((c) => c.name), axisLabel: { color: cssVar('--muted') } },
      yAxis: { type: 'value', min: 0, max: 10, axisLabel: { color: cssVar('--muted') }, splitLine: { lineStyle: { color: cssVar('--line') } } },
      series: [{ type: 'bar', data: data.components.map((c) => c.score), itemStyle: { borderRadius: [10, 10, 3, 3], color: cssVar('--accent') } }]
    });
  }

  function renderDocumentating(data) {
    document.querySelectorAll('[data-component-score]').forEach((n) => { n.textContent = data.score; });
    document.querySelectorAll('[data-component-confidence]').forEach((n) => { n.textContent = data.confidence; });
    Object.entries(data.metrics).forEach(([key, value]) => {
      document.querySelectorAll(`[data-metric="${key}"]`).forEach((n) => { n.textContent = value; });
    });
    if (window.echarts) {
      const keys = Object.keys(data.metrics);
      const values = Object.values(data.metrics);
      const radar = document.getElementById('capability-radar-chart');
      if (radar) {
        charts.radar = echarts.init(radar);
        charts.radar.setOption({ tooltip: {}, radar: { indicator: keys.map((k) => ({ name: k.replaceAll('_', ' '), max: 10 })) }, series: [{ type: 'radar', data: [{ value: values, name: 'Documentating' }] }] });
      }
      const bar = document.getElementById('capability-bar-chart');
      if (bar) {
        charts.bar = echarts.init(bar);
        charts.bar.setOption({ tooltip: { trigger: 'axis' }, grid: { left: 32, right: 18, bottom: 42, top: 20, containLabel: true }, xAxis: { type: 'category', data: keys.map((k) => k.replaceAll('_', ' ')), axisLabel: { rotate: 25 } }, yAxis: { type: 'value', min: 0, max: 10 }, series: [{ type: 'bar', data: values, itemStyle: { color: cssVar('--accent-2') } }] });
      }
    }
    if (window.GridStack) {
      const grid = GridStack.init({ cellHeight: 92, margin: 12, float: true, resizable: { handles: 'all' } });
      const saved = localStorage.getItem(layoutKey);
      if (saved) { try { grid.load(JSON.parse(saved)); } catch (error) {} }
      grid.on('change', () => localStorage.setItem(layoutKey, JSON.stringify(grid.save(false))));
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-theme-value]').forEach((button) => button.addEventListener('click', () => {
      localStorage.setItem(storageKey, button.getAttribute('data-theme-value'));
      applyTheme(button.getAttribute('data-theme-value'));
    }));
    document.querySelectorAll('[data-atlas-year]').forEach((node) => { node.textContent = String(new Date().getFullYear()); });
    applyTheme(localStorage.getItem(storageKey) || 'system');
    if (document.body.classList.contains('atlas-page--landing')) loadJson('./assets/data/portfolio.json').then(renderPortfolio).catch(console.error);
    if (document.body.classList.contains('atlas-page--component')) loadJson('../assets/data/documentating.json').then(renderDocumentating).catch(console.error);
    window.addEventListener('resize', () => Object.values(charts).forEach((chart) => chart && chart.resize()));
  });
})();
