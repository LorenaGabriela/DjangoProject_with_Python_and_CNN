if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/temapltes/medical/serviceworker.js').then(function(registration) {
      // Înregistrarea a fost reușită
      console.log('ServiceWorker registration successful with scope: ', registration.scope);
    }, function(err) {
      // Înregistrarea a eșuat
      console.error('ServiceWorker registration failed: ', err);
    });
  });
}
