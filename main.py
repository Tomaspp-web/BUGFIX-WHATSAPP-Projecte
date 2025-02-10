from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import BaseDeDatos
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
app = FastAPI() 
bd = BaseDeDatos()

from fastapi.middleware.cors import CORSMiddleware

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

def generar_token(username: str, user_id: int):
    expiracion = datetime.utcnow() + timedelta(hours=1)
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
    id_usuario = bd.obtener_usuario(request.state.username)
    if not id_usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    miembros = [id_usuario['id']] + grupo.miembros
    id_grupo = bd.crear_grupo(id_usuario['id'], grupo.nombre, grupo.descripcion, miembros)
    
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

    grupos = bd.llistar_grupos(usuario['id'])
    return {"grupos": grupos}

# Endpoint: Missatges entre usuaris
@app.post("/missatgesAmics")
def enviar_missatge(missatge: Mensaje, request: Request):
    verificar_token(request)
    
    try:
        json_data = request.json()
        print(f"💾 Rebent JSON: {json_data}") 
    except Exception as e:
        print(f"❌ Error llegint JSON: {e}")
    
    bd.enviar_missatge_U(request.state.id, missatge.destinatario, missatge.mensaje)  
    return {"mensaje": "Missatge enviat correctament"}


@app.get("/missatgesAmics/{destinatario}")
def obtenir_missatges(destinatario, request: Request,pagina:int):
    verificar_token(request)
    missatges = bd.obtener_mensajes(request.state.id, destinatario)
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
def obtenir_missatges_G(id_grupo, request: Request):
    verificar_token(request)
    missatges = bd.obtenir_missatges_G(id_grupo)
    chat = bd.get_nom_grup(id_grupo)
    
    if not missatges:
        return {"missatges": 0, "destinatario": chat, "id_usuario": request.state.id}
    
    return {"missatges": missatges, "destinatario": chat, "id_usuario": request.state.id}

# Endpoint: Canviar estat de missatge
@app.put("/check")
def cambiar_estado(id_missatge: int, nou_estat: str, request: Request):
    verificar_token(request)
    bd.cambiar_estado(id_missatge, nou_estat)
    return {"mensaje": f"Estat del missatge {id_missatge} actualitzat a {nou_estat}"}

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
