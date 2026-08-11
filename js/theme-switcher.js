/* ==========================================================================
   theme-switcher.js — Theme & Mode Management
   Saves to localStorage, applies to <html> data-theme/data-mode
   ========================================================================== */
(function () {
  'use strict';

  var THEMES = ['biophilic', 'editorial', 'terminal', 'ocean'];
  var DEFAULT_THEME = 'terminal';
  var DEFAULT_MODE = 'dark';

  function load() {
    try {
      return {
        theme: localStorage.getItem('zerone_theme') || DEFAULT_THEME,
        mode: localStorage.getItem('zerone_mode') || DEFAULT_MODE
      };
    } catch (e) {
      return { theme: DEFAULT_THEME, mode: DEFAULT_MODE };
    }
  }

  function save(theme, mode) {
    try {
      localStorage.setItem('zerone_theme', theme);
      localStorage.setItem('zerone_mode', mode);
    } catch (e) {}
  }

  function apply(theme, mode) {
    var html = document.documentElement;
    html.setAttribute('data-theme', theme);
    html.setAttribute('data-mode', mode);
    // Update meta theme-color
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      var bg = getComputedStyle(html).getPropertyValue('--bg').trim();
      if (bg) meta.setAttribute('content', bg);
    }
  }

  function getModeIcon(mode) {
    return mode === 'dark' ? '🌙' : '☀️';
  }

  function init() {
    var saved = load();
    if (THEMES.indexOf(saved.theme) < 0) saved.theme = DEFAULT_THEME;
    if (saved.mode !== 'dark' && saved.mode !== 'light') saved.mode = DEFAULT_MODE;
    apply(saved.theme, saved.mode);

    // Create theme switcher
    var switcher = document.createElement('div');
    switcher.className = 'theme-switcher';
    switcher.innerHTML = THEMES.map(function (t) {
      return '<button class="theme-btn' + (t === saved.theme ? ' active' : '') +
        '" data-t="' + t + '" title="' + t + '"></button>';
    }).join('');

    switcher.querySelectorAll('.theme-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var theme = this.getAttribute('data-t');
        switcher.querySelectorAll('.theme-btn').forEach(function (b) { b.classList.remove('active'); });
        this.classList.add('active');
        var current = load();
        apply(theme, current.mode);
        save(theme, current.mode);
      });
    });

    // Create mode toggle
    var toggle = document.createElement('div');
    toggle.className = 'mode-toggle';
    toggle.textContent = getModeIcon(saved.mode);
    toggle.title = '切换亮/暗模式';

    toggle.addEventListener('click', function () {
      var current = load();
      var newMode = current.mode === 'dark' ? 'light' : 'dark';
      toggle.textContent = getModeIcon(newMode);
      apply(current.theme, newMode);
      save(current.theme, newMode);
    });

    document.body.appendChild(switcher);
    document.body.appendChild(toggle);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
