/* ==========================================================================
   app.js — Shared utilities for AI News Hub
   Provides: window.fmt, window.API, window.renderState
   ========================================================================== */
(function () {
  'use strict';

  /* ---------- window.fmt: formatting helpers ---------- */
  window.fmt = {
    esc: function (s) {
      if (s == null) return '';
      return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    },
    stars: function (n) {
      n = n || 0;
      if (n >= 10000) {
        var w = n / 10000;
        return (w >= 100 ? Math.round(w) : w.toFixed(1).replace(/\.0$/, '')) + '万';
      }
      return n.toLocaleString();
    },
    relTime: function (dateStr) {
      if (!dateStr) return '-';
      var d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      var diff = Date.now() - d.getTime();
      var min = Math.floor(diff / 60000);
      if (min < 1) return '刚刚';
      if (min < 60) return min + ' 分钟前';
      var hr = Math.floor(min / 60);
      if (hr < 24) return hr + ' 小时前';
      var day = Math.floor(hr / 24);
      if (day < 30) return day + ' 天前';
      var mo = Math.floor(day / 30);
      if (mo < 12) return mo + ' 个月前';
      return Math.floor(mo / 12) + ' 年前';
    },
    date: function (dateStr) {
      if (!dateStr) return '-';
      var d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    }
  };

  /* ---------- window.API: data fetcher with fallback ---------- */
  window.API = {
    get: function (urls) {
      if (typeof urls === 'string') urls = [urls];
      var promises = urls.map(function (url) {
        return fetch(url, { credentials: 'omit' }).then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.json();
        });
      });
      // Try each URL in sequence, return first success
      return new Promise(function (resolve, reject) {
        var idx = 0;
        function tryNext() {
          if (idx >= promises.length) {
            reject(new Error('All data sources failed'));
            return;
          }
          promises[idx].then(function (data) {
            resolve(data);
          }).catch(function () {
            idx++;
            tryNext();
          });
        }
        tryNext();
      });
    }
  };

  /* ---------- window.renderState: UI state helpers ---------- */
  window.renderState = {
    loading: function (msg) {
      return '<div class="state state-loading"><div class="state-spinner"></div><p>' + (msg || '加载中…') + '</p></div>';
    },
    empty: function (msg) {
      return '<div class="state"><p>' + (msg || '暂无数据') + '</p></div>';
    },
    error: function (msg) {
      return '<div class="state state-error"><p>⚠ ' + (msg || '数据加载失败') + '</p></div>';
    }
  };
})();
