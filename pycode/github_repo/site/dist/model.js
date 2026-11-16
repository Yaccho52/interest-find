/* ============================================================ */
/* 模型说明页：读取 model.json，渲染图示与交互 */
(() => {
  const COLORS = ['#345c4b', '#6e8a61', '#93a86f', '#c2a878', '#b08968', '#a9768e', '#6c6aa8', '#7c9aa6'];
  const SOURCE_COLORS = ['#345c4b', '#6e8a61', '#b08968', '#c2a878'];
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
    const ordered = data.sources.slice().sort((a, b) => b.count - a.count);
    ordered.forEach((source) => {
      const card = el('div', 'source-card');
      card.append(el('b', '', source.label));
      const count = el('div', 'src-count', source.count.toLocaleString());
      count.append(el('small', '', '条'));
      card.append(count, el('span', 'src-kind', source.kind));
      host.append(card);
    });

    const bar = $('#composition');
    const legend = $('#composition-legend');
    const total = ordered.reduce((sum, item) => sum + item.count, 0);
    ordered.forEach((source, index) => {
      const segment = el('i');
      segment.style.width = `${(source.count / total) * 100}%`;
      segment.style.background = SOURCE_COLORS[index % SOURCE_COLORS.length];
      segment.title = `${source.label} ${source.count}`;
      bar.append(segment);

      const item = el('li');
      const dot = el('span', 'dot');
      dot.style.background = SOURCE_COLORS[index % SOURCE_COLORS.length];
      item.append(dot, document.createTextNode(`${source.label} · ${source.count.toLocaleString()} 条`));
      legend.append(item);
    });
    $('#composition-total').textContent = `共 ${total.toLocaleString()} 条`;
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

  let activeCluster = null;

  function toggleCluster(cluster) {
    activeCluster = activeCluster === cluster ? null : cluster;
    document.querySelectorAll('.cluster-card').forEach((card) => {
      card.classList.toggle('active', Number(card.dataset.cluster) === activeCluster);
    });
    document.querySelectorAll('.legend-chip').forEach((chip) => {
      chip.classList.toggle('active', Number(chip.dataset.cluster) === activeCluster);
    });
    document.querySelectorAll('#scatter circle').forEach((point) => {
      const match = activeCluster === null || Number(point.dataset.cluster) === activeCluster;
      point.setAttribute('opacity', match ? '0.86' : '0.08');
      point.setAttribute('r', match && activeCluster !== null ? '4.6' : '3.2');
    });
  }

  function renderClusters(data) {
    const legend = $('#legend');
    const host = $('#clusters');
    data.clusters.forEach((cluster) => {
      const chip = el('button', 'legend-chip');
      chip.type = 'button';
      chip.dataset.cluster = String(cluster.id);
      const swatch = el('span', 'cluster-dot');
      swatch.style.background = color(cluster.id);
      chip.append(swatch, document.createTextNode(`主题 ${cluster.id}`));
      chip.addEventListener('click', () => toggleCluster(cluster.id));
      legend.append(chip);

      const card = el('button', 'cluster-card');
      card.type = 'button';
      card.dataset.cluster = String(cluster.id);
      const header = el('header');
      const dot = el('span', 'cluster-dot');
      dot.style.background = color(cluster.id);
      header.append(dot, el('span', 'cluster-name', `主题 ${cluster.id}`),
                    el('span', 'cluster-size', `${cluster.size} 条`));
      card.append(
        header,
        el('p', 'cluster-terms', cluster.terms.slice(0, 4).join(' · ')),
        el('p', 'cluster-example', cluster.examples[0] || '—'),
      );
      card.title = cluster.examples.join(' / ');
      card.addEventListener('click', () => toggleCluster(cluster.id));
      host.append(card);
    });
  }

  function renderScatter(data) {
    const svg = $('#scatter');
    const width = 1160;
    const height = 540;
    const pad = 42;
    const fragment = document.createDocumentFragment();
    data.projection.forEach(([x, y, cluster]) => {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', (pad + x * (width - pad * 2)).toFixed(1));
      circle.setAttribute('cy', (pad + (1 - y) * (height - pad * 2)).toFixed(1));
      circle.setAttribute('r', '3.2');
      circle.setAttribute('fill', color(cluster));
      circle.setAttribute('opacity', '0.72');
      circle.dataset.cluster = String(cluster);
      fragment.append(circle);
    });
    svg.append(fragment);
  }

  function renderRank(data) {
    const host = $('#rank');
    data.mmr.forEach((list, index) => {
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
    if (data.mmr.length === 2) {
      $('#sim-a').textContent = data.mmr[0].similarity.toFixed(3);
      $('#sim-b').textContent = data.mmr[1].similarity.toFixed(3);
    }

    const bars = $('#simbars');
    const scale = 0.55;
    data.mmr.forEach((list, index) => {
      const row = el('div', 'sim-row');
      row.append(el('label', '', index === 1 ? 'λ = 0.2' : 'λ = 0'));
      const track = el('div', 'sim-track');
      const fill = el('div', 'sim-fill');
      fill.style.width = `${Math.min((list.similarity / scale) * 100, 100)}%`;
      fill.style.background = index === 1 ? '#345c4b' : '#c2a878';
      track.append(fill);
      row.append(track, el('output', '', list.similarity.toFixed(3)));
      bars.append(row);
    });
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
        row.append(track, el('output', '', value.toFixed(3)));
        bars.append(row);
      });
      card.append(head, bars);
      host.append(card);
    });
  }

  async function start() {
    renderMatrix();
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
