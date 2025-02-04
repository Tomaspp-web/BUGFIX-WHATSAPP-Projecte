import { apiGet, apiPostWithToken } from "./connectivitat.js";

document.addEventListener('DOMContentLoaded', async () => {
    let usuaris = await fetchUsuarios();
    mostrarUsuarios(usuaris);

    document.getElementById('openGroupModal').addEventListener('click', () => {
        document.getElementById('groupModal').style.display = 'block';
    });

    document.getElementById('closeGroupModal').addEventListener('click', () => {
        document.getElementById('groupModal').style.display = 'none';
    });

    document.getElementById('groupForm').addEventListener('submit', crearGrupo);
});

async function mostraChat(contacto) {
    console.log("📩 Click en usuario/grupo:", contacto);

    let token = comprobarToken();

    if (!contacto || (contacto.id_usuario === undefined && contacto.id_grupo === undefined)) {
        console.error("❌ Error: El objeto contacto no tiene un ID válido.", contacto);
        return;
    }

    let id = contacto.id_usuario !== undefined ? contacto.id_usuario : contacto.id_grupo;
    console.log(`📡 Solicitando mensajes del usuario/grupo con ID: ${id}`);

    let response;

    if (contacto.id_usuario !== undefined) {
        response = await apiGet(`/missatgesAmics/${id}`, token);
    } else if (contacto.id_grupo !== undefined) {
        response = await apiGet(`/missatgesGrup/${id}`, token);
    }

    console.log("📡 Respuesta del servidor:", response);

    if (!response) {
        console.error("❌ Error: La respuesta de la API es null o undefined.");
        alert("Error cargando el chat.");
        return;
    }

    let chatContainer = document.getElementById('chatContainer');
    chatContainer.innerHTML = '';

    if (!response.missatges || response.missatges.length === 0) {
        console.warn("⚠ No hay mensajes en este chat.");
        chatContainer.innerHTML = '<p>No hay mensajes en este chat.</p>';
        return;
    }

    response.missatges.reverse().forEach(missatge => {
        let messageElement = document.createElement('div');

        if (contacto.id_usuario !== undefined) {
            if (missatge.id_usuario_envia === contacto.id_usuario) {
                messageElement.classList.add('message', 'received');
            } else {
                messageElement.classList.add('message', 'sent');
            }
        } 
        else if (contacto.id_grupo !== undefined) {
            if (missatge.id_usuari === sessionStorage.getItem("user_id")) {
                messageElement.classList.add('message', 'sent');
            } else {
                messageElement.classList.add('message', 'received');
            }
        }

        messageElement.innerHTML = `<strong>${missatge.nom_usuari}:</strong> ${missatge.text}`;
        chatContainer.appendChild(messageElement);
    });

    sessionStorage.setItem('chat', JSON.stringify(contacto));

    document.getElementById('sendButton').addEventListener('click', () => enviarMensaje(contacto));


    let chatHeader = document.querySelector(".chat-header h5");
    chatHeader.textContent = response.destinatario;

    scrollToBottom();
}

function scrollToBottom() {
    let chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function comprobarToken() {
    let token = sessionStorage.getItem('token');
    if (!token) {
        window.location.href = "formulari.html";
    }
    
    return token;
}

function mostrarUsuarios(usuarios) {
    let userList = document.getElementById('contactsContainer');
    userList.innerHTML = '';

    if (!Array.isArray(usuarios) || usuarios.length === 0) {
        userList.innerHTML = "<p>No hay usuarios disponibles.</p>";
        return;
    }

    usuarios.forEach(contacto => {
        let listItem = document.createElement('li');
        listItem.classList.add('list-group-item');

        let userElement = document.createElement('span');
        if (contacto.id_grupo !== null) {
            userElement.id = `${contacto.id_grupo}`;
            userElement.textContent = `🔹 [GRUPO] ${contacto.nombre_grupo}`;
        } else if (contacto.id_usuario !== null) {
            userElement.id = `${contacto.id_usuario}`;
            userElement.textContent = `👤 ${contacto.nombre_usuario}`;
        } else {
            userElement.textContent = `Elemento desconocido`;
        }

        listItem.appendChild(userElement);
        listItem.addEventListener('click', () => {
            if (contacto.id_grupo || contacto.id_grupo === 0) {
                mostraChat({ id_grupo: contacto.id_grupo });
            } else if (contacto.id_usuario || contacto.id_usuario === 0) {
                mostraChat({ id_usuario: contacto.id_usuario });
            } else {
                console.error("Error: El objeto contacto no tiene un ID válido.", contacto);
            }
        });
        userList.appendChild(listItem);
    });
}

async function fetchUsuarios() {
    let token = comprobarToken();
    try {
        let response = await apiGet('/contactos', token);
        if (!response || !response.contactos) {
            throw new Error("Error cargando contactos.");
        }
        return response.contactos;
    } catch (error) {
        console.error("Error obteniendo usuarios:", error.message);
        alert("Error cargando la lista de contactos.");
        return [];
    }
}

window.onload = function () {
    const savedTheme = localStorage.getItem('theme');
    const body = document.getElementById('body-theme');
    if (savedTheme) {
        body.classList.add(savedTheme);
    }
};

async function enviarMensaje(destinatari) {
    let text = document.getElementById('messageInput').value.trim();
    if (!text) return;

    console.log("Enviar mensaje a:", destinatari);

    if (!destinatari || (destinatari.id_usuario === undefined && destinatari.id_grupo === undefined)) {
        console.error("Error: No se encontró el ID del destinatario.", destinatari);
        return;
    }

    let data = {};
    if (destinatari.id_usuario !== undefined) {
        data = {
            destinatario: destinatari.id_usuario,
            mensaje: text
        };
    } else if (destinatari.id_grupo !== undefined) {
        data = {
            id_grupo: destinatari.id_grupo,
            mensaje: text
        };
    } else {
        console.error("Error: El objeto destinatario no tiene un ID válido.", destinatari);
        return;
    }

    console.log("JSON enviat:", JSON.stringify(data));

    let token = sessionStorage.getItem('token');
    try {
        let response = await apiPostWithToken('/missatgesAmics', data, token);
        console.log("Respuesta del servidor:", response);

        if (!response || response.error) {
            alert("Error enviando el mensaje.");
            return;
        }

        document.getElementById('messageInput').value = '';
        mostraChat(destinatari);
    } catch (error) {
        console.error("Error enviant missatge:", error);
    }
}


async function crearGrupo(event) {
    let token = comprobarToken();
    event.preventDefault();

    let groupName = document.getElementById('groupName').value;
    let groupDescription = document.getElementById('groupDescription').value;
    let groupMembers = document.getElementById('groupMembers').value.split(',').map(id => parseInt(id.trim()));

    try {
        let response = await apiPostWithToken('/grupos', {
            nombre: groupName,
            descripcion: groupDescription,
            miembros: groupMembers
        }, token);

        if (response && response.id_grupo) {
            alert('Grupo creado correctamente');
            document.getElementById('groupForm').reset();
            document.getElementById('groupModal').style.display = 'none';
        } else {
            alert('Error al crear el grupo');
        }
    } catch (error) {
        console.error('Error al crear el grupo:', error);
        alert('Error al crear el grupo');
    }

    let usuaris = await fetchUsuarios();
    mostrarUsuarios(usuaris);
}