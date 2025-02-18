window.onload = function () {
    const savedTheme = localStorage.getItem('theme');
    const body = document.getElementById('body-theme');
    if (savedTheme) {
        body.classList.add(savedTheme);
    }
};
