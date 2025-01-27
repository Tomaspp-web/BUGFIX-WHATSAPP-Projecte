// Excepció per errors d'autorització
export class ExcepcioNoAutoritzat extends Error {
    constructor(message = "No autoritzat") {
        super(message);
        this.name = "ExcepcioNoAutoritzat";
    }
}

// Excepció per errors de recursos no trobats
export class ExcepcioNoTrobat extends Error {
    constructor(message = "No trobat") {
        super(message);
        this.name = "ExcepcioNoTrobat";
    }
}

// Exemple d'un array local d'usuaris per utilitzar al teu codi
export const llistaUsuaris = [
    { id: 1, nom: "Sergi", cognom: "Tomas", email: "sergi@example.com" },
    { id: 2, nom: "Pepito", cognom: "Grillo", email: "pepito@example.com" },
    { id: 3, nom: "Maria", cognom: "Lopez", email: "maria@example.com" }
];
