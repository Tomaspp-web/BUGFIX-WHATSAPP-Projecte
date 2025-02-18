document.getElementById('tema').addEventListener('change', function () {
    const theme = this.value;
    const body = document.getElementById('body-theme');
    if (theme === 'dark') {
        body.classList.add('dark-theme');
        body.classList.remove('light-theme');
    } else {
        body.classList.add('light-theme');
        body.classList.remove('dark-theme');
    }
});

window.onload = function () {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        const body = document.getElementById('body-theme');
        body.classList.add(savedTheme);
        document.getElementById('tema').value = savedTheme === 'dark-theme' ? 'dark' : 'light';
    }
};

document.getElementById('settings-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const selectedTheme = document.getElementById('tema').value;
    localStorage.setItem('theme', selectedTheme === 'dark' ? 'dark-theme' : 'light-theme');
});