document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;

  /* THEME TOGGLE (persist) */
  const themeBtn = document.getElementById('theme-toggle');
  const saved = localStorage.getItem('wt-theme');
  if (saved === 'dark') body.classList.add('dark');
  if (themeBtn) {
    themeBtn.textContent = body.classList.contains('dark') ? 'Light' : 'Dark';
    themeBtn.addEventListener('click', () => {
      body.classList.toggle('dark');
      themeBtn.textContent = body.classList.contains('dark') ? 'Light' : 'Dark';
      localStorage.setItem('wt-theme', body.classList.contains('dark') ? 'dark' : 'light');
    });
  }

  /* MOBILE MENU */
  const mobileBtn = document.getElementById('mobile-menu');
  const navLinks = document.querySelector('.nav-links');
  mobileBtn?.addEventListener('click', () => {
    navLinks?.classList.toggle('open');
  });

  /* CATEGORY PALETTE (manual map + fallback) */
  const palette = ['#16a34a','#06b6d4','#8b5cf6','#f97316','#ef4444','#2563eb','#9ca3af'];
  const manualMap = {
    'health':'#16a34a',
    'work':'#2563eb',
    'mental health':'#8b5cf6',
    'others':'#9ca3af'
  };

  function contrastClass(hex) {
    if (!hex) return 'contrast-light';
    const h = hex.replace('#','');
    const r = parseInt(h.substring(0,2),16);
    const g = parseInt(h.substring(2,4),16);
    const b = parseInt(h.substring(4,6),16);
    const luminance = (0.299*r + 0.587*g + 0.114*b);
    return luminance > 180 ? 'contrast-dark' : 'contrast-light';
  }

  // assign colors to categories
  document.querySelectorAll('.category-item').forEach((item, idx) => {
    const nameEl = item.querySelector('.cat-name');
    const name = nameEl ? nameEl.textContent.trim().toLowerCase() : '';
    const inlineColor = item.style.getPropertyValue('--cat-color');
    let color = '';
    if (inlineColor && inlineColor.trim() !== '' && inlineColor.trim() !== 'unset') {
      color = inlineColor.trim();
    } else if (manualMap[name]) {
      color = manualMap[name];
    } else {
      color = palette[idx % palette.length];
    }
    item.dataset.color = color;
    const btn = item.querySelector('.cat-btn');
    if (btn) {
      btn.style.borderLeftColor = color;
      btn.dataset.color = color;
    }
  });

  // apply colors to existing task tags (template may provide inline color)
  document.querySelectorAll('.task-tag').forEach(tag => {
    let bg = tag.style.background;
    const catId = tag.dataset.cat;
    if ((!bg || bg.trim()==='') && catId) {
      const catEl = document.querySelector(`.category-item[data-cat-id="${catId}"]`);
      if (catEl) bg = catEl.dataset.color;
    }
    if (!bg) bg = palette[0];
    tag.style.background = bg;
    tag.classList.add(contrastClass(bg));
  });

  /* CATEGORY CLICK: Behavior 3 — filter tasks showing only that category (toggle to clear) */
  let activeCat = null;
  document.querySelectorAll('.cat-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const li = btn.closest('.category-item');
      const catId = li.getAttribute('data-cat-id');
      const isActive = btn.classList.contains('active');

      // clear all active
      document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));

      if (isActive) {
        activeCat = null;
        filterByCategory(null);
        btn.setAttribute('aria-pressed','false');
      } else {
        btn.classList.add('active');
        btn.setAttribute('aria-pressed','true');
        activeCat = catId;
        filterByCategory(catId);
      }
    });
  });

  function filterByCategory(catId) {
    const tasks = document.querySelectorAll('#taskList .task-item');
    if (!catId) {
      tasks.forEach(li => li.style.display = 'flex');
      return;
    }
    tasks.forEach(li => {
      const taskCat = li.getAttribute('data-cat-id') || '';
      li.style.display = (taskCat === catId) ? 'flex' : 'none';
    });
  }

  // Clear filter button
  const clearBtn = document.getElementById('clearFilter');
  clearBtn?.addEventListener('click', () => {
    activeCat = null;
    document.querySelectorAll('.cat-btn').forEach(b=>b.classList.remove('active'));
    filterByCategory(null);
  });

  /* FILTER SELECT (done/pending/all) */
  const filterSelect = document.getElementById('filterSelect');
  filterSelect?.addEventListener('change', () => {
    const v = filterSelect.value;
    document.querySelectorAll('#taskList .task-item').forEach(li => {
      if (v === 'all') li.style.display = 'flex';
      else if (v === 'done') li.style.display = li.classList.contains('done') ? 'flex' : 'none';
      else if (v === 'pending') li.style.display = !li.classList.contains('done') ? 'flex' : 'none';
    });
  });

  /* QUICK UX: when clicking the check button we toggle done visually quickly
     Note: form still submits to backend to persist change. */
  document.querySelectorAll('#taskList .check').forEach(btn => {
    btn.addEventListener('click', () => {
      const li = btn.closest('.task-item');
      if (!li) return;
      // toggle class quickly; backend will persist on submit
      setTimeout(() => li.classList.toggle('done'), 80);
    });
  });

});
