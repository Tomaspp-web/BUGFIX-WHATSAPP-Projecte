from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import BaseDeDatos
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta

app = FastAPI()
bd = BaseDeDatos()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "clau_secreta"
ALGORITHM = "HS256"


class UserLogin(BaseModel):
    username: str   
    password: str


class Grupo(BaseModel):
    nombre: str
    descripcion: str
    miembros: list[int]


class Mensaje(BaseModel):
    destinatario: int
    mensaje: str


class MensajeGrup(BaseModel):
    id_grupo: int
    mensaje: str


class EstadoUpdate(BaseModel):
    id_contacto: int
    nou_estat: str


def generar_token(username: str, user_id: int):
    expiracion = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": username, "id": user_id, "exp": expiracion}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/login")
def login(user: UserLogin):
    try:
        usuari = bd.obtener_usuario(user.username)
        if not usuari:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        hashed_password = usuari.get("password")
        if not bd.verificar_password(user.password, hashed_password):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")

        token = generar_token(user.username, usuari["id"])
        return {"access_token": token}
    except Exception as e:
        print(f"Error en /login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


def verificar_token(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionat")

    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token mal formatat")

    token = token.split(" ")[1]  # Només agafem el token sense el "Bearer"

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.username = payload["sub"]
        request.state.id = payload["id"]  # Guardar también el id
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirat")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invàlid")


@app.post("/grupos")
def crear_grupo(grupo: Grupo, request: Request):
    verificar_token(request)
    miembros = [request.state.id] + grupo.miembros
    id_grupo = bd.crear_grupo(
        request.state.id, grupo.nombre, grupo.descripcion, miembros
    )

    if id_grupo:
        return {"id_grupo": id_grupo, "mensaje": "Grupo creado correctamente"}
    else:
        raise HTTPException(status_code=500, detail="Error al crear el grupo")


@app.get("/grupos")
def llistar_grupos(request: Request):
    verificar_token(request)
    usuario = bd.obtener_usuario(request.state.username)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    grupos = bd.llistar_grupos(usuario["id"])
    return {"grupos": grupos}


@app.post("/missatgesAmics")
def enviar_missatge(missatge: Mensaje, request: Request):
    verificar_token(request)
    bd.enviar_missatge_U(request.state.id, missatge.destinatario, missatge.mensaje)
    return {"mensaje": "Missatge enviat correctament"}


@app.get("/missatgesAmics/{destinatario}")
def obtenir_missatges(destinatario, request: Request, pagina: int):
    verificar_token(request)
    missatges = bd.obtener_mensajes(request.state.id, destinatario, pagina)
    contacto = bd.get_username(destinatario)

    if not missatges:
        return {"missatges": 0, "destinatario": contacto}

    return {"missatges": missatges, "destinatario": contacto}


@app.post("/missatgesGrup")
def enviar_missatge_G(missatge: MensajeGrup, request: Request):
    verificar_token(request)
    bd.enviar_missatge_G(missatge.id_grupo, request.state.id, missatge.mensaje)
    return {"mensaje": "Missatge enviat correctament al grup"}


@app.get("/missatgesGrup/{id_grupo}")
def obtenir_missatges_G(id_grupo, request: Request, pagina: int):
    verificar_token(request)
    missatges = bd.obtenir_missatges_G(request.state.id, id_grupo, pagina)
    chat = bd.get_nom_grup(id_grupo)

    if not missatges:
        return {"missatges": 0, "destinatario": chat, "id_usuario": request.state.id}

    return {
        "missatges": missatges,
        "destinatario": chat,
        "id_usuario": request.state.id,
    }


@app.put("/check")
def cambiar_estado(estado_update: EstadoUpdate, request: Request):
    verificar_token(request)
    bd.cambiar_estado_U(
        estado_update.nou_estat, estado_update.id_contacto, request.state.id
    )
    return {
        "mensaje": f"Estat dels missatges enviats per {estado_update.id_contacto} actualitzats a {estado_update.nou_estat}"
    }


@app.put("/checkGrupo/{id_grupo}")
def cambiar_estado_grupo(id_grupo, request: Request):
    verificar_token(request)
    bd.cambiar_estado_G(id_grupo, request.state.id)
    return {
        "mensaje": "Estat dels missatges del grup actualitzats a leido"
    }


@app.get("/usuarios")
def obtener_usuarios(request: Request):
    verificar_token(request)
    usuarios = bd.obtener_usuarios(request.state.id)
    return {"usuarios": usuarios}


@app.get("/usuario/{id_usuario}")
def obtener_usuarios(id_usuario: int):
    usuario = bd.get_username(id_usuario)
    return usuario

@app.get("/contactos")
def obtener_contactos(request: Request):
    verificar_token(request)
    contactos = bd.obtener_contactos(request.state.id)
    return {"contactos": contactos}


@app.get("/adminGrupo/{id_grupo}")
def obtener_admin_grupo(id_grupo: int, request: Request):
    verificar_token(request)
    admin = bd.obtener_admins(id_grupo)
    return admin

@app.get("/miembrosGrupo/{id_grupo}")
def obtener_miembros_grupo(id_grupo, request: Request):
    verificar_token(request)
    miembros = bd.obtener_miembros(id_grupo)
    admin = bd.obtener_admins(id_grupo)
    infoGrupo = bd.get_info_grupo(id_grupo)
    return {"miembros": miembros, "id_usuario": request.state.id, "admin": admin, "infoGrupo": infoGrupo}

@app.put("/añadirMiembro/{id_grupo}/{id_usuario}")
def añadir_miembro(id_grupo, id_usuario, request: Request):
    verificar_token(request)
    bd.añadir_miembro(request.state.id, id_grupo, id_usuario)
    return {"mensaje": "Miembro añadido correctamente"}

@app.delete("/eliminarMiembro/{id_grupo}/{id_usuario}")
def eliminar_miembro(id_grupo, id_usuario, request: Request):
    verificar_token(request)
    bd.eliminar_miembro(request.state.id, id_grupo, id_usuario)
    return {"mensaje": "Miembro eliminado correctamente"}

@app.delete("/salirGrupo/{id_grupo}")
def salir_grupo(id_grupo, request: Request):
    verificar_token(request)
    bd.eliminar_miembro(request.state.id, id_grupo, request.state.id)
    return {"mensaje": "Has salido del grupo correctamente"}

@app.delete("/eliminarAdmin/{id_grupo}/{id_usuario}")
def eliminar_admin(id_grupo, id_usuario, request: Request):
    verificar_token(request)
    bd.eliminar_admin(id_grupo, id_usuario)
    return {"mensaje": "Admin eliminado correctamente"}

@app.put("/asignarAdmin/{id_grupo}/{id_usuario}")
def asignar_admin(id_grupo, id_usuario, request: Request):
    verificar_token(request)
    bd.nuevo_admin(id_usuario, id_grupo)
    return {"mensaje": "Admin asignado correctamente"}


class NombreGrupo(BaseModel):
    nombre: str

@app.put("/cambiaNombreGrupo/{id_grupo}")
def cambiar_nombre_grupo(id_grupo: int, datos: NombreGrupo, request: Request):
    verificar_token(request)
    bd.cambiar_nombre_grupo(id_grupo, datos.nombre)
    return {"mensaje": "Nombre del grupo cambiado correctamente"}


class DescripcionGrupo(BaseModel):
    descripcion: str

@app.put("/cambiaDescripcionGrupo/{id_grupo}")
def cambiar_descripcion_grupo(id_grupo: int, descripcion_data: DescripcionGrupo, request: Request):
    verificar_token(request)
    bd.cambiar_descripcion_grupo(id_grupo, descripcion_data.descripcion)
    return {"mensaje": "Descripción del grupo cambiada correctamente"}


