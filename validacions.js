import { apiPost, apiGet, API_URL } from "./connectivitat.js";

document.addEventListener('DOMContentLoaded', () => {
    let loginForm = document.getElementById('login');
    let usernameInput = document.getElementById('nameuser');
    let passwordInput = document.getElementById('password');
    let postLoginContainer = document.getElementById('postLoginContainer');
    let userListContainer = document.getElementById('userListContainer');
    let chatContainer = document.getElementById('chatContainer');
    let usuariosGlobal = [];

    async function loginUser(username, password) {
        console.log(`📡 Enviant petició de login a ${API_URL}/login amb username: ${username}`);
        let response = await apiPost('/login', { username, password });

        console.log(`🔎 Resposta crua del servidor:`, response);

        if (!response || !response.access_token) {
            throw new Error("Credencials incorrectes.");
        }
        return response.access_token;
    }

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        let username = usernameInput.value;
        let password = passwordInput.value;

        try {
            let token = await loginUser(username, password);
            sessionStorage.setItem('token', token);
            window.location.href = "chat.html";

        } catch (error) {
            alert('Error al iniciar sessió: ' + error.message);
        }
    });


});