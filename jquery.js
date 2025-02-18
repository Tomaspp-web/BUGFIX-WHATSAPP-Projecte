$(document).ready(function () {
    // DARK MODE TOGGLE BUTTON
    $("#toggle-dark-mode").click(function () {
        $("body").toggleClass("dark-theme light-theme");
        let currentTheme = $("body").hasClass("dark-theme") ? "dark-theme" : "light-theme";
        localStorage.setItem("theme", currentTheme);

        // Update Button Text
        $("#toggle-dark-mode").text(currentTheme === "dark-theme" ? "Modo Claro" : "Modo Oscuro");
    });

    // APPLY STORED THEME ON PAGE LOAD
    if (localStorage.getItem("theme")) {
        $("body").addClass(localStorage.getItem("theme"));
        $("#toggle-dark-mode").text(localStorage.getItem("theme") === "dark-theme" ? "Modo Claro" : "Modo Oscuro");
    }

    // BACKGROUND IMAGE CHANGE
    $("#background-selector").change(function () {
        let bgImage = $(this).val();
        $("body").css("background-image", `url(${bgImage})`);
        localStorage.setItem("background", bgImage);
    });

    // APPLY STORED BACKGROUND IMAGE ON LOAD
    if (localStorage.getItem("background")) {
        $("body").css("background-image", `url(${localStorage.getItem("background")})`);
    }

    // RESPONSIVE VIEW TOGGLE
    $("#toggle-responsive").click(function () {
        $("body").toggleClass("mobile-view");
    });
});
