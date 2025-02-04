document.addEventListener('DOMContentLoaded', cargaDOM);

function cargaDOM() {
    let logout = document.getElementById("logout");
    logout.addEventListener("click", cerrarSesion);

}


function cerrarSesion() {
    sessionStorage.removeItem("token");
    window.location.href = "formulari.html";
}

