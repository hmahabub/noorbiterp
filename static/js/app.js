// Small progressive-enhancement helpers for the ERP UI.
document.addEventListener('DOMContentLoaded', function () {
  // Auto-dismiss alerts after 5s
  document.querySelectorAll('.alert').forEach(function (el) {
    setTimeout(function () {
      var alert = bootstrap.Alert.getOrCreateInstance(el);
      if (alert) alert.close();
    }, 5000);
  });

  // Confirm on any element carrying data-confirm="..."
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });
});
