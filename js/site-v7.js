(() => {
  const cards = [...document.querySelectorAll('.work-card')];
  const groupsHost = document.getElementById('filter-groups');
  const summaryStatus = document.getElementById('filter-summary-status');
  const clearButton = document.getElementById('clear-filter');
  const filterPanel = document.getElementById('filter-panel');

  const groups = [
    { key: 'category', label: '大类' },
    { key: 'composer', label: '作曲家' },
    { key: 'artist', label: '艺术家' },
    { key: 'franchise', label: '相关作品' },
    { key: 'instrument', label: '乐器', hideWhenSingle: true }
  ];

  let active = null;

  function values(card, key) {
    return (card.dataset[key] || '').split('|').map(s => s.trim()).filter(Boolean);
  }

  function uniqueValues(key) {
    const set = new Set();
    cards.forEach(card => values(card, key).forEach(v => set.add(v)));
    return [...set].sort((a,b) => a.localeCompare(b, 'zh-CN'));
  }

  function renderGroups() {
    if (!groupsHost) return;
    groupsHost.innerHTML = '';
    groups.forEach(group => {
      const vals = uniqueValues(group.key);
      if (!vals.length || (group.hideWhenSingle && vals.length <= 1)) return;
      const row = document.createElement('div');
      row.className = 'filter-row';
      const label = document.createElement('div');
      label.className = 'filter-label';
      label.textContent = group.label;
      const options = document.createElement('div');
      options.className = 'filter-options';
      vals.forEach(value => {
        const button = document.createElement('button');
        button.className = 'filter-chip';
        button.type = 'button';
        button.dataset.filter = group.key;
        button.dataset.value = value;
        button.textContent = value;
        button.addEventListener('click', () => {
          if (active && active.key === group.key && active.value === value) active = null;
          else active = { key: group.key, value, label: group.label };
          apply();
        });
        options.appendChild(button);
      });
      row.append(label, options);
      groupsHost.appendChild(row);
    });
  }

  function apply() {
    let shown = 0;
    cards.forEach(card => {
      const ok = !active || values(card, active.key).includes(active.value);
      card.hidden = !ok;
      if (ok) shown++;
    });

    document.querySelectorAll('.filter-chip').forEach(btn => {
      const isActive = !!active && btn.dataset.filter === active.key && btn.dataset.value === active.value;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });

    if (summaryStatus) {
      summaryStatus.textContent = active ? `${active.value} · ${shown} 篇` : `未筛选 · ${shown} 篇`;
    }
    if (clearButton) clearButton.hidden = !active;
  }

  clearButton?.addEventListener('click', () => {
    active = null;
    apply();
  });

  renderGroups();
  apply();
})();
