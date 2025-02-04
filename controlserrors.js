
export function validarUsuari(idUsuari) {
    let usuari = llistaUsuaris.find((usuari) => usuari.id === idUsuari);

    if (!usuari) {
        throw new ExcepcioNoTrobat(`Usuari amb ID ${idUsuari} no trobat.`);
    }

    if (usuari.nom === "Pepito") {
        throw new ExcepcioNoAutoritzat(`Usuari ${usuari.nom} no té permisos.`);
    }

    return usuari;
}

export function gestionarError(error) {
    if (error instanceof ExcepcioNoTrobat) {
        console.error("Error de tipus 'No trobat':", error.message);
    } else if (error instanceof ExcepcioNoAutoritzat) {
        console.error("Error de tipus 'No autoritzat':", error.message);
    } else {
        console.error("Error desconegut:", error.message);
    }
}

export class ExcepcioNoAutoritzat extends Error {
    constructor(message = "No autoritzat") {
        super(message);
        this.name = "ExcepcioNoAutoritzat";
    }
}

export class ExcepcioNoTrobat extends Error {
    constructor(message = "No trobat") {
        super(message);
        this.name = "ExcepcioNoTrobat";
    }
}


