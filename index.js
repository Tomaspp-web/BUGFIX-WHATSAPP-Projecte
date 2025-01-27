import { apiGet, apiPost } from './connectivitat.js';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login');
    const usernameInput = document.getElementById('nameuser');
    const passwordInput = document.getElementById('password');
    const userListContainer = document.getElementById('userListContainer');

    usernameInput.addEventListener('input', () => {
        usernameInput.value = usernameInput.value.toLowerCase();
    });

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = usernameInput.value;
        const password = passwordInput.value;

        if (!validateUsername(username)) {
            alert('El nombre de usuario debe estar en minúsculas y no contener caracteres especiales o se ha superado el maximo de caracteres(50).');
            return;
        }

        if (!validatePassword(password)) {
            alert('La contraseña debe ser un DNI válido o un NIE válido.');
            return;
        }

        try {
            const accessToken = await loginUser(username, password);
            const usuarios = await fetchUsuarios(accessToken);
            mostrarUsuarios(usuarios);
            alert('Form submitted successfully');
        } catch (error) {
            alert('Error al iniciar sesión: ' + error.message);
        }
    });

    function validateUsername(username) {
        const usernameRegex = /^[a-z0-9]{1,50}$/;
        return usernameRegex.test(username);
    }

    function validatePassword(password) {
        const dniRegex = /^\d{8}[A-Z]?$/;
        const nieRegex = /^[XYZ]\d{7}?$/;
        return dniRegex.test(password) || nieRegex.test(password);
    }

    async function loginUser(username, password) {
        const { access_token } = await apiPost('/login', { username, password });
        sessionStorage.setItem('token', access_token);
        return access_token;
    }

    async function fetchUsuarios(accessToken) {
        const { usuarios } = await apiGet('/usuarios', accessToken);
        return usuarios;
    }

    function mostrarUsuarios(usuarios) {
        userListContainer.innerHTML = '';
        const userList = document.createElement('ul');
        usuarios.forEach(({ id, username }) => {
            const listItem = document.createElement('li');
            listItem.textContent = `ID: ${id}, Username: ${username}`;
            userList.appendChild(listItem);
        });
        userListContainer.appendChild(userList);
    }
});