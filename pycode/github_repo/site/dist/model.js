/* ============================================================ */
/* 模型说明页：读取 model.json，渲染图示与交互 */
(() => {
  const COLORS = ['#345c4b', '#6e8a61', '#93a86f', '#c2a878', '#b08968', '#a9768e', '#6c6aa8', '#7c9aa6'];
  const METHOD_LABELS = { keyword: '关键词基线', tfidf: 'TF-IDF', tfidf_mmr: 'TF-IDF + MMR' };
  const METHOD_COLORS = { keyword: '#c2a878', tfidf: '#6e8a61', tfidf_mmr: '#345c4b' };
  const METRICS = [
    { key: 'category_precision_at_5', label: '同类 P@5', hint: '越高越好' },
    { key: 'catalog_coverage', label: '目录覆盖率', hint: '越高越好' },
    { key: 'mean_intra_list_similarity', label: '列表内相似度', hint: '越低越不重复' },
  ];

  const $ = (selector) => document.querySelector(selector);
  const el = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  const color = (cluster) => COLORS[cluster % COLORS.length];

  function renderFacts(data) {
    const facts = [
      [data.total.toLocaleString(), '条活动记录'],
      [data.vocabulary.toLocaleString(), '维词表'],
      [data.clusters.length, '个主题'],
      [data.paths, '条兴趣路径'],
    ];
    const host = $('#facts');
    facts.forEach(([value, label]) => {
      const card = el('div', 'fact');
      card.append(el('b', '', String(value)), el('span', '', label));
      host.append(card);
    });
  }

  function renderSources(data) {
    const host = $('#sources');
    data.sources.slice().sort((a, b) => b.count - a.count).forEach((source) => {
      const card = el('div', 'source-card');
      card.append(el('b', '', source.label));
      const count = el('div', 'src-count', source.count.toLocaleString());
      count.append(el('small', '', '条'));
      card.append(count, el('span', 'src-kind', source.kind));
      host.append(card);
    });
  }

  function renderTokens(data) {
    const demo = data.token_demo;
    $('#token-input').textContent = demo.input;
    const host = $('#tokens');
    demo.tokens.forEach((token) => host.append(el('span', 'token', token)));
  }

  function renderMatrix() {
    const host = $('#matrix');
    const total = 48 * 18;
    const lit = new Set([7, 96, 231, 418, 605, 742]);
    for (let index = 0; index < total; index += 1) {
      host.append(el('i', lit.has(index) ? 'on' : ''));
    }
  }

  function renderClusters(data) {
    const host = $('#clusters');
    const legend = $('#legend');
    data.clusters.forEach((cluster) => {
      const card = el('button', 'cluster-card');
      card.type = 'button';
      card.dataset.cluster = String(cluster.id);
      card.title = cluster.examples.join(' / ');
      const dot = el('span', 'cluster-dot');
      dot.style.background = color(cluster.id);
      const body = el('span');
      body.append(
        el('span', 'cluster-name', `主题 ${cluster.id}`),
        el('span', 'cluster-terms', cluster.terms.slice(0, 3).join(' · ')),
      );
      card.append(dot, body, el('span', 'cluster-size', String(cluster.size)));
      card.addEventListener('click', () => toggleCluster(cluster.id));
      host.append(card);

      if (legend) {
        const chip = el('button', 'legend-chip');
        chip.type = 'button';
        chip.dataset.cluster = String(cluster.id);
        const swatch = el('span', 'cluster-dot');
        swatch.style.background = color(cluster.id);
        chip.append(swatch, document.createTextNode(`主题 ${cluster.id}`));
        chip.addEventListener('click', () => toggleCluster(cluster.id));
        legend.append(chip);
      }
    });
  }

  let activeCluster = null;

  function toggleCluster(cluster) {
    activeCluster = activeCluster === cluster ? null : cluster;
    document.querySelectorAll('.cluster-card').forEach((card) => {
      card.classList.toggle('active', Number(card.dataset.cluster) === activeCluster);
    });
    document.querySelectorAll('.legend-chip').forEach((chip) => {
      chip.classList.toggle('active', Number(chip.dataset.cluster) === activeCluster);
    });
    const svg = $('#scatter');
    svg.querySelectorAll('circle').forEach((point) => {
      const match = activeCluster === null || Number(point.dataset.cluster) === activeCluster;
      point.setAttribute('opacity', match ? '0.86' : '0.08');
      point.setAttribute('r', match && activeCluster !== null ? '4.4' : '3.1');
    });
  }

  function renderScatter(data) {
    const svg = $('#scatter');
    const width = 820;
    const height = 470;
    const pad = 28;
    const points = data.projection;
    const radius = 3.1;
    const fragment = document.createDocumentFragment();
    points.forEach(([x, y, cluster]) => {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', (pad + x * (width - pad * 2)).toFixed(1));
      circle.setAttribute('cy', (pad + (1 - y) * (height - pad * 2)).toFixed(1));
      circle.setAttribute('r', String(radius));
      circle.setAttribute('fill', color(cluster));
      circle.setAttribute('opacity', '0.72');
      circle.dataset.cluster = String(cluster);
      fragment.append(circle);
    });
    svg.append(fragment);
  }

  function renderRank(data) {
    const host = $('#rank');
    const lists = data.mmr;
    lists.forEach((list, index) => {
      const column = el('div', 'rank-col' + (index === 1 ? ' default' : ''));
      const header = el('header');
      header.append(
        el('b', '', index === 1 ? 'λ = 0.2 · 默认' : 'λ = 0'),
        el('span', '', `平均两两余弦 ${list.similarity.toFixed(3)}`),
      );
      const ordered = el('ol', 'rank-ol');
      list.items.forEach((item, position) => {
        const row = el('li', 'rank-item');
        row.append(
          el('span', 'rank-index', String(position + 1).padStart(2, '0')),
          el('span', 'rank-title', item.title),
          el('span', 'rank-score', item.score.toFixed(3)),
        );
        ordered.append(row);
      });
      column.append(header, ordered);
      host.append(column);
    });
    if (lists.length === 2) {
      $('#sim-a').textContent = lists[0].similarity.toFixed(3);
      $('#sim-b').textContent = lists[1].similarity.toFixed(3);
    }
  }

  function renderMetrics(data) {
    const host = $('#metrics');
    METRICS.forEach((metric) => {
      const values = Object.entries(data.metrics).map(([method, scores]) => [method, scores[metric.key]]);
      const max = Math.max(...values.map(([, value]) => value), 0.001);
      const card = el('div', 'metric');
      const head = el('div', 'metric-head');
      head.append(el('b', '', metric.label), el('span', '', metric.hint));
      const bars = el('div', 'metric-bars');
      values.forEach(([method, value]) => {
        const row = el('div', 'metric-row');
        row.append(el('label', '', METHOD_LABELS[method] || method));
        const track = el('div', 'metric-track');
        const fill = el('div', 'metric-fill');
        fill.style.width = `${Math.max((value / max) * 100, 2)}%`;
        fill.style.background = METHOD_COLORS[method] || '#93a86f';
        track.append(fill);
        const output = el('output', '', value.toFixed(3));
        row.append(track, output);
        bars.append(row);
      });
      card.append(head, bars);
      host.append(card);
    });
  }

  async function start() {
    renderMatrix();
    $('#cluster-reset').addEventListener('click', () => {
      if (activeCluster !== null) toggleCluster(activeCluster);
    });
    try {
      const response = await fetch('model.json');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      renderFacts(data);
      renderSources(data);
      renderTokens(data);
      renderClusters(data);
      renderScatter(data);
      renderRank(data);
      renderMetrics(data);
      $('#nonzero').textContent = data.nonzero.toLocaleString();
      $('#density').textContent = `${(data.density * 100).toFixed(2)}%`;
    } catch (error) {
      $('#facts').innerHTML = '<p class="step-note">模型数据加载失败，请检查 model.json 是否已发布。</p>';
      console.error(error);
    }
  }

  start();
})();
