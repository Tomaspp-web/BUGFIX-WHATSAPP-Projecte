export let API_URL = 'http://localhost:8000';

export async function apiGet(endpoint, token = '') {
    try {
        console.log(`📡 Enviando petición GET a ${API_URL}${endpoint} con token:`, token);

        let response = await fetch(`${API_URL}${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
            },
        });

        console.log(`🔎 Respuesta cruda de ${API_URL}${endpoint}:`, response);

        // Verificar si la respuesta es JSON antes de intentar parsearla
        let contentType = response.headers.get("content-type");
        if (!response.ok) {
            console.error(`❌ Error HTTP ${response.status}: ${response.statusText}`);
            return null;
        }

        if (contentType && contentType.includes("application/json")) {
            let data = await response.json();
            console.log(`✅ Respuesta JSON de ${API_URL}${endpoint}:`, data);
            return data;
        } else {
            console.warn(`⚠ La respuesta no es JSON:`, await response.text());
            return null;
        }
    } catch (error) {
        console.error(`❌ Error en apiGet(${endpoint}):`, error.message);
        return null;
    }
}


export async function apiPost(endpoint, data) {
    try {
        let response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        return await response.json();
    } catch (error) {
        console.error(`POST ${endpoint} - ${error.message}`);
        throw error;
    }
}

export async function apiPostWithToken(endpoint, data, token) {
    try {
        let response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        console.log(`📡 JSON enviat a ${endpoint}:`, JSON.stringify(data));

        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        return await response.json();
    } catch (error) {
        console.error(`POST ${endpoint} - ${error.message}`);
        throw error;
    }
}



