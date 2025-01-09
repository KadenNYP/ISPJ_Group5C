document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    });

    document.addEventListener('selectstart', function (e) {
        e.preventDefault();
    });

    document.addEventListener('copy', function (e) {
        e.preventDefault();
        alert("Copy action is disabled on this page.");
    });

    document.addEventListener('paste', function (e) {
        e.preventDefault();
        alert("Paste action is disabled on this page.");
    });