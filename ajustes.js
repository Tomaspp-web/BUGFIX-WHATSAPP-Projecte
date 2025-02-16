$(document).ready(function () {
    $("#toggle-dark-mode").click(function () {
        $("body").toggleClass("dark-theme light-theme");
        let currentTheme = $("body").hasClass("dark-theme") ? "dark-theme" : "light-theme";
        localStorage.setItem("theme", currentTheme);

        $("#toggle-dark-mode").text(currentTheme === "dark-theme" ? "Modo Claro" : "Modo Oscuro");
    });

    $("#font-size-select").change(function (event) {
        const selectedSize = event.target.value;
        document.body.classList.remove("small-font", "normal-font", "big-font", "very-big-font");
        document.body.classList.add(`${selectedSize}-font`);
        localStorage.setItem("fontSize", selectedSize);
    });

    if (localStorage.getItem("theme")) {
        $("body").addClass(localStorage.getItem("theme"));
        $("#toggle-dark-mode").text(localStorage.getItem("theme") === "dark-theme" ? "Modo Claro" : "Modo Oscuro");
    }

    if (localStorage.getItem("fontSize")) {
        const savedSize = localStorage.getItem("fontSize");
        document.body.classList.remove("small-font", "normal-font", "big-font", "very-big-font");
        document.body.classList.add(`${savedSize}-font`);
        document.getElementById("font-size-select").value = savedSize;
    }

    $("#background-upload").change(function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const backgroundImage = e.target.result;
                localStorage.setItem("chatBackground", backgroundImage);
                alert("Imagen de fondo guardada correctamente.");
            };
            reader.readAsDataURL(file);
        }
    });

    $("#remove-background").click(function () {
        localStorage.removeItem("chatBackground");
        alert("Imagen de fondo eliminada correctamente.");
    });

    $("#go-to-chat").click(function () {
        window.location.href = "chat.html";
    });

    $("#logout").click(function () {
        sessionStorage.removeItem("token");
        alert("Sesión cerrada correctamente.");
        window.location.href = "formulari.html";
    });
});