<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import manifest from '$lib/tag_hierarchy_manifest.json';

  // Reactive state using Svelte 5 runes
  let activeTab = $state('graph'); // 'graph' | 'matrix' | 'ontology'
  let selectedNode = $state(null);
  let searchQuery = $state('');
  let showOrder1 = $state(true);
  let showOrder2 = $state(true);
  let showOrder3 = $state(true);
  let selectedCore = $state('all'); // 'all' | 'core_psychology' | 'core_software_engineering'
  let selectedChannel = $state('all'); // 'all' | channel_slug

  let svgElement = $state();
  let simulation = $state();

  const CHANNEL_METADATA = {
    healthygamergg: { name: 'HealthyGamerGG', creator: 'Dr. Alok Kanojia', core: 'core_psychology', color: '#10b981', borderClass: 'border-hg', barClass: 'bar-hg' },
    theramintrees: { name: 'TheraminTrees', creator: 'TheraminTrees', core: 'core_psychology', color: '#f59e0b', borderClass: 'border-tt', barClass: 'bar-tt' },
    theprimeagen: { name: 'ThePrimeagen', creator: 'ThePrimeagen', core: 'core_software_engineering', color: '#ef4444', borderClass: 'border-tp', barClass: 'bar-tp' },
    web_dev_simplified: { name: 'Web Dev Simplified', creator: 'Kyle Cook', core: 'core_software_engineering', color: '#3b82f6', borderClass: 'border-wds', barClass: 'bar-wds' },
    freecodecamp: { name: 'freeCodeCamp.org', creator: 'Quincy Larson & Team', core: 'core_software_engineering', color: '#06b6d4', borderClass: 'border-fcc', barClass: 'bar-fcc' },
    a_life_engineered: { name: 'A Life Engineered', creator: 'Steve Huynh', core: 'core_software_engineering', color: '#8b5cf6', borderClass: 'border-ale', barClass: 'bar-ale' }
  };

  // Filtered graph data
  let filteredNodes = $derived(() => {
    return manifest.nodes.filter(n => {
      if (n.order === 1 && !showOrder1) return false;
      if (n.order === 2 && !showOrder2) return false;
      if (n.order === 3 && !showOrder3) return false;
      if (selectedCore !== 'all') {
        if (n.core && n.core !== 'cross_core' && n.core !== selectedCore) return false;
      }
      if (selectedChannel !== 'all' && n.channel && n.channel !== selectedChannel) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchLabel = (n.label || '').toLowerCase().includes(q);
        const matchTitle = (n.full_title || '').toLowerCase().includes(q);
        const matchCat = (n.category || '').toLowerCase().includes(q);
        if (!matchLabel && !matchTitle && !matchCat) return false;
      }
      return true;
    });
  });

  let filteredLinks = $derived(() => {
    const nodeIds = new Set(filteredNodes().map(n => n.id));
    return manifest.links.filter(l => {
      const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
      const targetId = typeof l.target === 'object' ? l.target.id : l.target;
      return nodeIds.has(sourceId) && nodeIds.has(targetId);
    });
  });

  let displayedChannels = $derived(() => {
    const keys = Object.keys(CHANNEL_METADATA);
    return keys.filter(k => {
      if (selectedCore !== 'all' && CHANNEL_METADATA[k].core !== selectedCore) return false;
      if (selectedChannel !== 'all' && k !== selectedChannel) return false;
      return true;
    });
  });

  function initD3Graph() {
    if (!svgElement) return;

    const width = svgElement.clientWidth || 960;
    const height = svgElement.clientHeight || 700;

    d3.select(svgElement).selectAll('*').remove();

    const svg = d3.select(svgElement)
      .attr('viewBox', [0, 0, width, height]);

    const g = svg.append('g');

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.15, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    const currentNodes = filteredNodes().map(d => ({ ...d }));
    const currentLinks = filteredLinks().map(d => ({ ...d }));

    simulation = d3.forceSimulation(currentNodes)
      .force('link', d3.forceLink(currentLinks).id(d => d.id).distance(d => d.value === 2 ? 120 : 65))
      .force('charge', d3.forceManyBody().strength(d => d.order === 3 ? -450 : (d.order === 2 ? -220 : -80)))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(d => d.radius + 10));

    // Draw Links
    const link = g.append('g')
      .attr('stroke-opacity', 0.45)
      .selectAll('line')
      .data(currentLinks)
      .join('line')
      .attr('stroke', d => d.value === 2 ? '#a855f7' : '#38bdf8')
      .attr('stroke-width', d => d.value === 2 ? 2 : 1)
      .attr('stroke-dasharray', d => d.value === 2 ? '4 2' : 'none');

    // Draw Node Groups
    const node = g.append('g')
      .selectAll('g')
      .data(currentNodes)
      .join('g')
      .attr('cursor', 'pointer')
      .call(drag(simulation));

    // Node Circles
    node.append('circle')
      .attr('r', d => d.radius)
      .attr('fill', d => d.color || '#94a3b8')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', d => d.order === 3 ? 2.5 : 1)
      .attr('stroke-opacity', 0.85)
      .attr('filter', d => d.order === 3 ? 'drop-shadow(0 0 10px rgba(168, 85, 247, 0.7))' : 'none');

    // Node Text Labels
    node.append('text')
      .attr('x', d => d.radius + 5)
      .attr('y', 4)
      .text(d => d.order === 1 ? '' : d.label)
      .attr('fill', '#f1f5f9')
      .attr('font-size', d => d.order === 3 ? '12px' : '10px')
      .attr('font-weight', d => d.order === 3 ? '700' : '500')
      .attr('pointer-events', 'none');

    // Hover & Click Interactions
    node.on('click', (event, d) => {
      event.stopPropagation();
      selectedNode = d;
    });

    node.on('mouseover', function(event, d) {
      d3.select(this).select('circle').transition().duration(150).attr('r', d.radius * 1.25);
    });

    node.on('mouseout', function(event, d) {
      d3.select(this).select('circle').transition().duration(150).attr('r', d.radius);
    });

    svg.on('click', () => {
      selectedNode = null;
    });

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
  }

  function drag(sim) {
    function dragstarted(event) {
      if (!event.active) sim.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }
    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }
    function dragended(event) {
      if (!event.active) sim.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
    return d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  }

  onMount(() => {
    initD3Graph();
  });

  // Re-run D3 layout when filters change
  $effect(() => {
    const _n = filteredNodes();
    const _l = filteredLinks();
    if (activeTab === 'graph') {
      setTimeout(() => initD3Graph(), 50);
    }
  });
</script>

<svelte:head>
  <title>Multi-Core Knowledge Silo: 3-Tier Tagging Hierarchy</title>
</svelte:head>

<div class="app-layout">
  <!-- Top Navigation Bar -->
  <header class="app-header">
    <div class="brand">
      <span class="logo">🏷️</span>
      <div>
        <h1>Multi-Core Knowledge Silo Visualizer</h1>
        <p class="subtitle">
          3-Tier Hierarchy • {manifest.summary.channels_indexed} Channels • {manifest.summary.total_videos_analyzed} Videos • {manifest.summary.total_words_analyzed.toLocaleString()} Spoken Words
        </p>
      </div>
    </div>

    <div class="tabs">
      <button class="tab-btn" class:active={activeTab === 'graph'} onclick={() => activeTab = 'graph'}>
        🌐 D3 Force Graph
      </button>
      <button class="tab-btn" class:active={activeTab === 'ontology'} onclick={() => activeTab = 'ontology'}>
        🏛️ 3rd-Order Ontology ({manifest.summary.third_order_count})
      </button>
      <button class="tab-btn" class:active={activeTab === 'matrix'} onclick={() => activeTab = 'matrix'}>
        📊 Channel Matrix
      </button>
    </div>
  </header>

  <!-- Control Bar -->
  <div class="control-bar">
    <div class="filter-group">
      <span class="filter-label">Knowledge Core:</span>
      <select bind:value={selectedCore} class="core-select">
        <option value="all">All Knowledge Cores</option>
        <option value="core_psychology">🧠 Cognitive Psychology</option>
        <option value="core_software_engineering">💻 Software Engineering & Systems</option>
      </select>
    </div>

    <div class="filter-group">
      <span class="filter-label">Channel:</span>
      <select bind:value={selectedChannel} class="channel-select">
        <option value="all">All Channels</option>
        {#each Object.entries(CHANNEL_METADATA) as [slug, meta]}
          {#if selectedCore === 'all' || meta.core === selectedCore}
            <option value={slug}>{meta.name}</option>
          {/if}
        {/each}
      </select>
    </div>

    <div class="filter-group">
      <span class="filter-label">Orders:</span>
      <label class="badge-toggle badge-3rd">
        <input type="checkbox" bind:checked={showOrder3} />
        3rd (Global)
      </label>
      <label class="badge-toggle badge-2nd">
        <input type="checkbox" bind:checked={showOrder2} />
        2nd (Channel)
      </label>
      <label class="badge-toggle badge-1st">
        <input type="checkbox" bind:checked={showOrder1} />
        1st (Video)
      </label>
    </div>

    <div class="search-box">
      <input type="text" placeholder="Search concepts, tags, videos..." bind:value={searchQuery} />
      {#if searchQuery}
        <button class="clear-btn" onclick={() => searchQuery = ''}>✕</button>
      {/if}
    </div>
  </div>

  <!-- Main View Container -->
  <main class="main-content">
    {#if activeTab === 'graph'}
      <div class="graph-wrapper">
        <svg bind:this={svgElement} class="d3-svg"></svg>
        <div class="graph-legend">
          <div class="legend-title">Taxonomy Legend</div>
          <div class="legend-item"><span class="dot dot-3rd"></span> 3rd-Order: Global Unbound Concept</div>
          <div class="legend-item"><span class="dot dot-hg"></span> 2nd-Order: HealthyGamerGG</div>
          <div class="legend-item"><span class="dot dot-tt"></span> 2nd-Order: TheraminTrees</div>
          <div class="legend-item"><span class="dot dot-tp"></span> 2nd-Order: ThePrimeagen</div>
          <div class="legend-item"><span class="dot dot-wds"></span> 2nd-Order: Web Dev Simplified</div>
          <div class="legend-item"><span class="dot dot-fcc"></span> 2nd-Order: freeCodeCamp.org</div>
          <div class="legend-item"><span class="dot dot-ale"></span> 2nd-Order: A Life Engineered</div>
          <div class="legend-item"><span class="dot dot-1st"></span> 1st-Order: Video Timestamp Node</div>
        </div>
      </div>
    {:else if activeTab === 'ontology'}
      <div class="ontology-view">
        <div class="view-header">
          <h2>🏛️ Third-Order Global Unbound Tag Ontology</h2>
          <p class="section-desc">Universal, cross-cutting conceptual anchors with no single-channel bounds, bridging cognitive architecture and software systems.</p>
        </div>
        
        <div class="ontology-grid">
          {#each Object.entries(manifest.third_order_ontology) as [t3Id, t3]}
            {#if selectedCore === 'all' || t3.core === 'cross_core' || t3.core === selectedCore}
              <div class="ontology-card">
                <div class="card-header">
                  <span class="order-badge order-3">3rd-Order</span>
                  <span class="core-tag {t3.core}">{t3.core === 'core_psychology' ? '🧠 Psychology' : (t3.core === 'core_software_engineering' ? '💻 Software' : '🔗 Cross-Core')}</span>
                  <span class="category-tag">{t3.category}</span>
                </div>
                <h3>{t3.name}</h3>
                <p class="desc">{t3.description}</p>

                <div class="mapping-section">
                  <h4>Bound 2nd-Order Channel Satellites ({t3.second_order_mapping.length}):</h4>
                  <div class="tag-chips">
                    {#each t3.second_order_mapping as s2}
                      <span class="chip">{s2.replace(/_/g, ' ')}</span>
                    {/each}
                  </div>
                </div>
              </div>
            {/if}
          {/each}
        </div>
      </div>
    {:else if activeTab === 'matrix'}
      <div class="matrix-view">
        <div class="view-header">
          <h2>📊 Second-Order Channel Pillar Matrix</h2>
          <p class="section-desc">Side-by-side comparison of creator-specific thematic signatures, vocabulary distribution, and relative topic prevalence.</p>
        </div>

        <div class="channel-matrix-grid">
          {#each displayedChannels() as chKey}
            {@const meta = CHANNEL_METADATA[chKey]}
            {@const pillars = manifest.nodes.filter(n => n.order === 2 && n.channel === chKey)}
            <div class="channel-col {meta.borderClass}">
              <div class="col-header">
                <div>
                  <h3>{meta.name}</h3>
                  <span class="col-creator">{meta.creator}</span>
                </div>
                <span class="col-stats">{pillars.length} Pillars</span>
              </div>
              <div class="pillar-list">
                {#each pillars as node}
                  <button type="button" class="pillar-row" onclick={() => selectedNode = node}>
                    <div class="pillar-title">{node.label}</div>
                    <div class="pillar-bar-wrap">
                      <div class="pillar-bar {meta.barClass}" style="width: {Math.min(100, node.prevalence * 2.2)}%"></div>
                      <span class="prevalence-label">{node.prevalence}% ({node.occurrences} vids)</span>
                    </div>
                  </button>
                {/each}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Inspector Drawer on Right -->
    {#if selectedNode}
      <aside class="inspector-drawer">
        <button class="close-drawer" onclick={() => selectedNode = null}>✕</button>

        <div class="drawer-header">
          <span class="order-badge order-{selectedNode.order}">
            {selectedNode.order === 3 ? '3rd-Order (Global Unbound)' : (selectedNode.order === 2 ? '2nd-Order (Channel-Bound)' : '1st-Order (Video-Bound)')}
          </span>
          {#if selectedNode.channel}
            <span class="channel-badge" style="border-left: 3px solid {CHANNEL_METADATA[selectedNode.channel]?.color || '#fff'}">
              {CHANNEL_METADATA[selectedNode.channel]?.name || selectedNode.channel.toUpperCase()}
            </span>
          {/if}
        </div>

        <h2>{selectedNode.full_title || selectedNode.label}</h2>

        {#if selectedNode.description}
          <div class="drawer-section">
            <h4>Description / Conceptual Definition</h4>
            <p>{selectedNode.description}</p>
          </div>
        {/if}

        {#if selectedNode.order === 2}
          <div class="drawer-section">
            <h4>Channel Statistics</h4>
            <p><strong>Occurrences:</strong> {selectedNode.occurrences} videos</p>
            <p><strong>Prevalence:</strong> {selectedNode.prevalence}% of channel output</p>
          </div>
        {/if}

        {#if selectedNode.order === 1}
          <div class="drawer-section">
            <h4>Video Metadata</h4>
            <p><strong>Duration:</strong> {selectedNode.duration}</p>
            <p><strong>URL:</strong> <a href={selectedNode.url} target="_blank" rel="noopener noreferrer">Watch on YouTube ↗</a></p>
          </div>
        {/if}
      </aside>
    {/if}
  </main>
</div>

<style>
  :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  :global(body) {
    background-color: #0b0f19;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    overflow: hidden;
    height: 100vh;
  }

  .app-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  .app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px;
    background: rgba(15, 23, 42, 0.95);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .logo { font-size: 1.6rem; }
  .brand h1 { font-size: 1.15rem; font-weight: 700; color: #fff; }
  .subtitle { font-size: 0.78rem; color: #94a3b8; }

  .tabs {
    display: flex;
    gap: 8px;
  }
  .tab-btn {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #94a3b8;
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.82rem;
    font-weight: 600;
    transition: all 0.15s;
  }
  .tab-btn:hover, .tab-btn.active {
    background: #6366f1;
    color: #fff;
    border-color: #818cf8;
  }

  .control-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 24px;
    background: rgba(18, 26, 43, 0.85);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    gap: 16px;
    flex-wrap: wrap;
  }
  .filter-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .filter-label {
    font-size: 0.75rem;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
  }
  .core-select, .channel-select {
    background: rgba(15, 23, 42, 0.85);
    color: #f1f5f9;
    border: 1px solid rgba(255, 255, 255, 0.14);
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    cursor: pointer;
  }
  .badge-toggle {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    padding: 3px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
  }
  .badge-3rd { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid #a855f7; }
  .badge-2nd { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }
  .badge-1st { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #0284c7; }

  .search-box {
    position: relative;
    width: 240px;
  }
  .search-box input {
    width: 100%;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #f1f5f9;
    padding: 5px 28px 5px 10px;
    border-radius: 4px;
    font-size: 0.8rem;
  }
  .clear-btn {
    position: absolute;
    right: 6px;
    top: 5px;
    background: none;
    border: none;
    color: #94a3b8;
    cursor: pointer;
  }

  .main-content {
    flex: 1;
    position: relative;
    overflow: hidden;
    display: flex;
  }

  .graph-wrapper {
    flex: 1;
    position: relative;
    background: radial-gradient(circle at 50% 50%, rgba(30, 41, 59, 0.4) 0%, rgba(11, 15, 25, 1) 100%);
  }
  .d3-svg {
    width: 100%;
    height: 100%;
  }
  .graph-legend {
    position: absolute;
    bottom: 16px;
    left: 16px;
    background: rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 0.72rem;
    display: flex;
    flex-direction: column;
    gap: 5px;
    max-height: 280px;
    overflow-y: auto;
  }
  .legend-title { font-weight: 700; color: #f8fafc; font-size: 0.76rem; margin-bottom: 2px; }
  .legend-item { display: flex; align-items: center; gap: 8px; color: #cbd5e1; }
  .dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
  .dot-3rd { background: #a855f7; box-shadow: 0 0 6px #a855f7; }
  .dot-hg { background: #10b981; }
  .dot-tt { background: #f59e0b; }
  .dot-tp { background: #ef4444; }
  .dot-wds { background: #3b82f6; }
  .dot-fcc { background: #06b6d4; }
  .dot-ale { background: #8b5cf6; }
  .dot-1st { background: #38bdf8; }

  /* Ontology View */
  .ontology-view, .matrix-view {
    flex: 1;
    overflow-y: auto;
    padding: 28px 32px;
  }
  .view-header h2 { font-size: 1.3rem; margin-bottom: 4px; color: #fff; }
  .section-desc { color: #94a3b8; font-size: 0.85rem; margin-bottom: 24px; }

  .ontology-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 20px;
  }
  .ontology-card {
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 20px;
    border-top: 3px solid #a855f7;
    display: flex;
    flex-direction: column;
  }
  .card-header {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
  }
  .core-tag { font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
  .core-tag.core_psychology { background: rgba(16, 185, 129, 0.2); color: #34d399; }
  .core-tag.core_software_engineering { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
  .core-tag.cross_core { background: rgba(168, 85, 247, 0.2); color: #c084fc; }
  .category-tag { font-size: 0.7rem; color: #cbd5e1; background: rgba(255, 255, 255, 0.06); padding: 2px 6px; border-radius: 4px; }
  .ontology-card h3 { font-size: 1.05rem; margin-bottom: 8px; color: #fff; }
  .ontology-card .desc { font-size: 0.82rem; color: #94a3b8; margin-bottom: 16px; line-height: 1.45; }
  .mapping-section h4 { font-size: 0.72rem; color: #a855f7; text-transform: uppercase; margin-bottom: 8px; }
  .tag-chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip { background: rgba(255, 255, 255, 0.06); padding: 3px 8px; border-radius: 4px; font-size: 0.73rem; color: #e2e8f0; }

  /* Channel Matrix View */
  .channel-matrix-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
  }
  .channel-col {
    background: rgba(18, 26, 43, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 18px;
  }
  .border-hg { border-top: 3px solid #10b981; }
  .border-tt { border-top: 3px solid #f59e0b; }
  .border-tp { border-top: 3px solid #ef4444; }
  .border-wds { border-top: 3px solid #3b82f6; }
  .border-fcc { border-top: 3px solid #06b6d4; }
  .border-ale { border-top: 3px solid #8b5cf6; }

  .col-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
  .col-header h3 { font-size: 1.0rem; color: #fff; }
  .col-creator { font-size: 0.75rem; color: #94a3b8; }
  .col-stats { font-size: 0.72rem; color: #94a3b8; background: rgba(255, 255, 255, 0.06); padding: 2px 6px; border-radius: 4px; }
  .pillar-list { display: flex; flex-direction: column; gap: 6px; }
  .pillar-row {
    display: block;
    width: 100%;
    text-align: left;
    border: 1px solid transparent;
    font-family: inherit;
    padding: 7px 9px;
    background: rgba(15, 23, 42, 0.5);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .pillar-row:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.1);
  }
  .pillar-title { font-size: 0.8rem; font-weight: 600; color: #f1f5f9; margin-bottom: 3px; }
  .pillar-bar-wrap { display: flex; align-items: center; gap: 8px; }
  .pillar-bar { height: 5px; border-radius: 3px; }
  .bar-hg { background: #10b981; }
  .bar-tt { background: #f59e0b; }
  .bar-tp { background: #ef4444; }
  .bar-wds { background: #3b82f6; }
  .bar-fcc { background: #06b6d4; }
  .bar-ale { background: #8b5cf6; }
  .prevalence-label { font-size: 0.7rem; color: #94a3b8; }

  /* Inspector Drawer */
  .inspector-drawer {
    width: 360px;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(16px);
    border-left: 1px solid rgba(255, 255, 255, 0.08);
    padding: 24px;
    overflow-y: auto;
    position: relative;
    z-index: 20;
  }
  .close-drawer {
    position: absolute;
    right: 16px;
    top: 16px;
    background: none;
    border: none;
    color: #94a3b8;
    font-size: 1.2rem;
    cursor: pointer;
  }
  .drawer-header { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .order-badge { font-size: 0.7rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
  .order-3 { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #a855f7; }
  .order-2 { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
  .order-1 { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #0284c7; }
  .channel-badge { font-size: 0.7rem; font-weight: 600; padding: 2px 6px; border-radius: 4px; background: rgba(255, 255, 255, 0.08); color: #cbd5e1; }
  .inspector-drawer h2 { font-size: 1.15rem; margin-bottom: 16px; color: #fff; }
  .drawer-section { margin-bottom: 16px; }
  .drawer-section h4 { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px; }
  .drawer-section p { font-size: 0.82rem; color: #cbd5e1; line-height: 1.45; }
  .drawer-section a { color: #38bdf8; text-decoration: none; font-weight: 600; }
  .drawer-section a:hover { text-decoration: underline; }
</style>
