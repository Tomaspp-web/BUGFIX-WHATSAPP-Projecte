import { apiGet, apiPostWithToken } from "./connectivitat.js";

document.addEventListener('DOMContentLoaded', async () => {
    let usuaris = await fetchUsuarios();
    mostrarUsuarios(usuaris);
    document.getElementById('sendButton').addEventListener('click', () => enviarMensaje());
    document.getElementById('openGroupModal').addEventListener('click', () => {
        document.getElementById('groupModal').style.display = 'block';
        cargarContactosParaGrupo();
    });
    document.getElementById('closeGroupModal').addEventListener('click', () => {
        document.getElementById('groupModal').style.display = 'none';
    });
    document.getElementById('groupForm').addEventListener('submit', crearGrupo);
});

async function mostraChat(contacto) {
    console.log("📩 Click en usuario/grupo:", contacto);
    let token = sessionStorage.getItem('token');
    if (!contacto || !contacto.id === 0) {
        console.error("❌ Error: L'objecte contacte no té un ID vàlid.", contacto.id);
        return;
    }
    let id = contacto.id;
    console.log(`📡 Sol·licitant missatges de l'usuari/grup amb ID: ${id}`);
    let response;
    if (contacto.tipo === 'usuario') {
        response = await apiGet(`/missatgesAmics/${id}`, token);
    } else if (contacto.tipo === 'grupo') {
        response = await apiGet(`/missatgesGrup/${id}`, token);
    }
    console.log("📡 Resposta del servidor:", response);
    if (response.missatges === 0) {
        document.getElementById('chatContainer').innerHTML = '<p>No hi ha missatges en aquest xat.</p>';
    } else {
        if (contacto.tipo === 'usuario') {
            pintarMensajesUsuario(response.missatges, id);
        } else if (contacto.tipo === 'grupo') {
            pintarMensajesGrupo(response.missatges, response.id_usuario);
        }
    }
    console.log("📝 Pintant capçalera del xat:", response.destinatario);
    let chatHeader = document.querySelector(".chat-header h5");
    chatHeader.textContent = response.destinatario;
    sessionStorage.setItem('chat', JSON.stringify(contacto));
}

function pintarMensajesUsuario(mensajes, idUsuario) {
    let chatContainer = document.getElementById('chatContainer');
    chatContainer.innerHTML = '';

    mensajes.reverse().forEach(mensaje => {
        let messageElement = document.createElement('div');
        if (mensaje.id_usuario_envia === idUsuario) {
            messageElement.classList.add('message', 'received');
        } else {
            messageElement.classList.add('message', 'sent');
        }
        messageElement.textContent = `${mensaje.nom_usuari}: ${mensaje.text}`;
        chatContainer.appendChild(messageElement);
    });
    scrollToBottom();
}


function pintarMensajesGrupo(mensajes, id_usuario) {
    let chatContainer = document.getElementById('chatContainer');
    chatContainer.innerHTML = '';
    console.log("👤 Usuario actual:", id_usuario);
    mensajes.reverse().forEach(mensaje => {
        let messageElement = document.createElement('div');
        if (mensaje.id_usuari === id_usuario) {
            messageElement.classList.add('message', 'sent');
        } else {
            messageElement.classList.add('message', 'received');
        }
        messageElement.textContent = `${mensaje.nom}: ${mensaje.text}`;
        chatContainer.appendChild(messageElement);
    });
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
        userList.innerHTML = "<p>No hi ha usuaris disponibles.</p>";
        console.warn("⚠️ No hi ha usuaris disponibles.");
        return;
    }

    usuarios.forEach(contacto => {
        let listItem = document.createElement('li');
        listItem.classList.add('list-group-item');

        let userElement = document.createElement('span');

        if (contacto.id_grupo !== null && contacto.id_grupo !== undefined) {
            userElement.id = `${contacto.id_grupo}`;
            userElement.textContent = `🔹 ${contacto.nombre_grupo}`;
        } else if (contacto.id_usuario !== null && contacto.id_usuario !== undefined) {
            userElement.id = `${contacto.id_usuario}`;
            userElement.textContent = `👤 ${contacto.nombre_usuario}`;
        } else {
            userElement.textContent = `Elemento desconegut`;
        }

        listItem.appendChild(userElement);
        listItem.addEventListener('click', () => {
            if (Number.isInteger(contacto.id_grupo)) {
                mostraChat({ id: contacto.id_grupo, tipo: 'grupo' });
            } else if (Number.isInteger(contacto.id_usuario)) {
                mostraChat({ id: contacto.id_usuario, tipo: 'usuario' });
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

function eliminarDeGrupo(userSpan) {
    userSpan.remove();
}

async function enviarMensaje() {
    let text = document.getElementById('messageInput').value.trim();
    if (!text) return;

    let destinatario = JSON.parse(sessionStorage.getItem('chat'));

    console.log("Enviar mensaje a:", destinatario.id);
    if (!destinatario) {
        console.error("Error: No se encontró el ID del destinatario.");
        return;
    }

    let data = {};
    if (destinatario.tipo === 'usuario') {
        data = {
            destinatario: destinatario.id,
            mensaje: text
        };
    } else if (destinatario.tipo === 'grupo') {
        data = {
            id_grupo: destinatario.id,
            mensaje: text
        };
    } else {
        console.error("Error: El objeto destinatario no tiene un ID válido.", destinatario.id);
        return;
    }

    console.log("JSON enviat:", JSON.stringify(data));
    if (destinatario.tipo === 'usuario') {
        let token = sessionStorage.getItem('token');
        try {
            let response = await apiPostWithToken('/missatgesAmics', data, token);
            console.log("Respuesta del servidor:", response);

            if (!response || response.error) {
                alert("Error enviando el mensaje.");
                return;
            }

            document.getElementById('messageInput').value = '';
            mostraChat(destinatario); // ✅ Manté la mateixa estructura
        } catch (error) {
            console.error("Error enviant missatge:", error);
        }
    } else if (destinatario.tipo === 'grupo') {
        let token = sessionStorage.getItem('token');
        try {
            let response = await apiPostWithToken('/missatgesGrup', data, token);
            console.log("Respuesta del servidor:", response);

            if (!response || response.error) {
                alert("Error enviando el mensaje.");
                return;
            }

            document.getElementById('messageInput').value = '';
            mostraChat(destinatario); // ✅ Manté la mateixa estructura
        } catch (error) {
            console.error("Error enviant missatge:", error);
        }
    }
}
async function crearGrupo(event) {
    event.preventDefault();
    let token = comprobarToken();

    let groupName = document.getElementById('groupName').value;
    let groupDescription = document.getElementById('groupDescription').value;
    
    let selectedContacts = document.getElementById('selectedContactsContainer').querySelectorAll('span');
    let groupMembers = Array.from(selectedContacts).map(item => parseInt(item.dataset.id));

    if (groupMembers.length === 0) {
        alert("⚠️ Selecciona almenys un membre per crear el grup.");
        return;
    }

    try {
        let response = await apiPostWithToken('/grupos', {
            nombre: groupName,
            descripcion: groupDescription,
            miembros: groupMembers
        }, token);

        if (response && response.id_grupo) {
            alert('✅ Grup creat correctament!');
            document.getElementById('groupForm').reset();
            document.getElementById('groupModal').style.display = 'none';
        } else {
            alert('❌ Error al crear el grup.');
        }
    } catch (error) {
        console.error('Error al crear el grup:', error);
        alert('Error al crear el grup');
    }

    let usuaris = await fetchUsuarios();
    mostrarUsuarios(usuaris);
}

function agregarAGrupo(contacto) {
    let selectedContactsContainer = document.getElementById('selectedContactsContainer');
    
    if (document.querySelector(`#selectedContactsContainer span[data-id="${contacto.id_usuario}"]`)) {
        return;
    }

    let userSpan = document.createElement('span');
    userSpan.classList.add('badge', 'bg-primary', 'p-2', 'me-2', 'd-flex', 'align-items-center');
    userSpan.textContent = contacto.nombre_usuario;
    userSpan.dataset.id = contacto.id_usuario;
    
    let removeButton = document.createElement('button');
    removeButton.classList.add('btn', 'btn-sm', 'btn-danger', 'ms-2');
    removeButton.textContent = '-';
    removeButton.onclick = () => eliminarDeGrupo(userSpan);
    
    userSpan.appendChild(removeButton);
    selectedContactsContainer.appendChild(userSpan);
}

async function cargarContactosParaGrupo() {
    let token = comprobarToken();
    let response = await apiGet('/contactos', token);
    
    let availableContacts = document.getElementById('availableContacts');
    availableContacts.innerHTML = ''; 

    if (!response || !response.contactos) {
        console.error("❌ No s'han pogut carregar els contactes.");
        return;
    }

    response.contactos.forEach(contacto => {
        if (contacto.id_usuario) { 
            let listItem = document.createElement('li');
            listItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
            listItem.textContent = contacto.nombre_usuario;
            listItem.dataset.id = contacto.id_usuario;

            let addButton = document.createElement('button');
            addButton.classList.add('btn', 'btn-sm', 'btn-success');
            addButton.textContent = '+';
            addButton.onclick = () => agregarAGrupo(contacto);

            listItem.appendChild(addButton);
            availableContacts.appendChild(listItem);
        }
    });
}