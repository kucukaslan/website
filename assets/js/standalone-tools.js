/* Embedded before paint; shares the parent site's theme preference. */
(() => {
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = 'system';
  try {
    const saved = localStorage.getItem('theme');
    if (saved === 'light' || saved === 'dark') preference = saved;
  } catch (_) { /* Local files and private contexts may deny storage. */ }

  function apply() {
    root.dataset.theme = preference === 'system' ? (system.matches ? 'dark' : 'light') : preference;
    const select = document.getElementById('tool-theme');
    if (select) select.value = preference;
    document.dispatchEvent(new Event('tool-theme-change'));
  }
  apply();
  system.addEventListener('change', () => {
    if (preference === 'system') apply();
  });
  window.addEventListener('storage', (event) => {
    if (event.key !== 'theme' && event.key !== null) return;
    preference = event.newValue === 'light' || event.newValue === 'dark' ? event.newValue : 'system';
    apply();
  });
  document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('tool-theme');
    if (!select) return;
    select.value = preference;
    select.addEventListener('change', () => {
      preference = select.value;
      try {
        if (preference === 'system') localStorage.removeItem('theme');
        else localStorage.setItem('theme', preference);
      } catch (_) { /* Theme switching still works without persistence. */ }
      apply();
    });
  });
})();
