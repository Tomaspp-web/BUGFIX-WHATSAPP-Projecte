// controls_errors.js: Fitxer per a la gestió de controls d'errors

import { ExcepcioNoAutoritzat, ExcepcioNoTrobat, llistaUsuaris } from './excepcions.js';

// Funció per validar si un usuari existeix i està autoritzat
export function validarUsuari(idUsuari) {
    const usuari = llistaUsuaris.find((usuari) => usuari.id === idUsuari);

    if (!usuari) {
        throw new ExcepcioNoTrobat(`Usuari amb ID ${idUsuari} no trobat.`);
    }

    if (usuari.nom === "Pepito") {
        throw new ExcepcioNoAutoritzat(`Usuari ${usuari.nom} no té permisos.`);
    }

    return usuari;
}

// Funció per gestionar els errors de manera centralitzada
export function gestionarError(error) {
    if (error instanceof ExcepcioNoTrobat) {
        console.error("Error de tipus 'No trobat':", error.message);
    } else if (error instanceof ExcepcioNoAutoritzat) {
        console.error("Error de tipus 'No autoritzat':", error.message);
    } else {
        console.error("Error desconegut:", error.message);
    }
}
