(function () {
  'use strict';

  const STORAGE_KEY = 'theme';
  const root = document.documentElement;

  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function getSavedTheme() {
    return localStorage.getItem(STORAGE_KEY);
  }

  function setTheme(theme, persist) {
    root.dataset.theme = theme;
    if (persist) {
      localStorage.setItem(STORAGE_KEY, theme);
    }
  }

  setTheme(getSavedTheme() || getSystemTheme(), false);

  function toggleTheme() {
    const current = root.dataset.theme || getSystemTheme();
    setTheme(current === 'dark' ? 'light' : 'dark', true);
  }

  document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) {
      toggle.addEventListener('click', toggleTheme);
    }

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
      if (!getSavedTheme()) {
        setTheme(e.matches ? 'dark' : 'light', false);
      }
    });
  });
})();
