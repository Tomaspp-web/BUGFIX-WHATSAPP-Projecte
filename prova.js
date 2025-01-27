// Espera que el DOM estigui completament carregat
document.addEventListener("DOMContentLoaded", () => {
    console.log("El DOM s'ha carregat correctament.");

    // Controlar si volem que l'API estigui disponible o no
    let apiDisponible = true; // Canvia a false per simular un error d'API
    let carregarUsuarisCorrectament = true; // Canvia a false per simular un error en la càrrega

    // Array local d'usuaris per simular dades d'una API
    const usuarios = [
        { id: 1, nombre: "Sergi", apellido: "Tomas" },
        { id: 2, nombre: "Pepito", apellido: "Grillo" },
        { id: 3, nombre: "Maria", apellido: "Lopez" }
    ];

    // Simula una connexió a una API
    function connectarApi() {
        return new Promise((resolve, reject) => {
            console.log("Connectant amb l'API...");
            mostrarMissatge("Connectant amb l'API...");
            setTimeout(() => {
                if (apiDisponible) {
                    resolve("Connexió amb l'API completada.");
                } else {
                    reject("Error: L'API encara no està disponible.");
                }
            }, 2000); // Simulem un retard de 2 segons
        });
    }

    // Simula la càrrega d'usuaris des de l'array local
    function carregarUsuaris() {
        return new Promise((resolve, reject) => {
            console.log("Carregant usuaris des de l'API...");
            mostrarMissatge("Carregant usuaris des de l'API...");
            setTimeout(() => {
                if (!carregarUsuarisCorrectament) {
                    // Simula un error intencionat
                    reject("Error: No s'ha pogut carregar els usuaris.");
                    return;
                }

                // Resol la promesa amb les dades de l'array local
                resolve(usuarios);
            }, 1000); // Simulem un retard de 1 segon
        });
    }

    // Mostra un missatge al contenidor d'output
    function mostrarMissatge(missatge, isError = false) {
        const outputDiv = document.getElementById("output");
        const messageElement = document.createElement("p");
        messageElement.innerHTML = isError ? `<span style="color: red;">${missatge}</span>` : missatge;
        outputDiv.appendChild(messageElement);
    }

    // Mostra els usuaris al contenidor d'output
    function mostrarUsuaris(usuaris) {
        const outputDiv = document.getElementById("output");
        const table = document.createElement("table");
        table.style.borderCollapse = "collapse";
        table.style.width = "100%";
        table.style.marginTop = "10px";

        const headerRow = document.createElement("tr");
        ["ID", "Nom", "Cognom"].forEach((header) => {
            const th = document.createElement("th");
            th.textContent = header;
            th.style.border = "1px solid black";
            th.style.padding = "8px";
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        usuaris.forEach((usuari) => {
            const row = document.createElement("tr");
            Object.values(usuari).forEach((value) => {
                const td = document.createElement("td");
                td.textContent = value;
                td.style.border = "1px solid black";
                td.style.padding = "8px";
                row.appendChild(td);
            });
            table.appendChild(row);
        });

        outputDiv.appendChild(table);
    }

    // Exemple complet utilitzant promeses
    document.getElementById("start-button").addEventListener("click", () => {
        // Neteja l'output abans de començar
        document.getElementById("output").innerHTML = "";

        connectarApi()
            .then((message) => {
                mostrarMissatge(message);
                return carregarUsuaris();
            })
            .then((usuaris) => {
                mostrarMissatge("Usuaris carregats des de l'API:");
                mostrarUsuaris(usuaris);
            })
            .catch((error) => {
                mostrarMissatge(error, true);
            });
    });
});
