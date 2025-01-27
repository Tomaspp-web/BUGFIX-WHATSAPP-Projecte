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
    allow_origins=["http://127.0.0.1:5500"],
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

class Mensaje(BaseModel):
    destinatario: int  # ID del destinatari
    mensaje: str

class MensajeGrup(BaseModel):
    id_grupo: int
    mensaje: str
    
    
def generar_token(username: str, id: int):
    expiracion = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": username, "id": id, "exp": expiracion}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/login")
def login(user: UserLogin):
    usuari = bd.obtener_usuari(user.username, user.password)
    if not usuari:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = generar_token(user.username, usuari["id"])
    return {"access_token": token}


# Helper functions
def verificar_token(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionat")
    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        request.state.username = payload["sub"]
        request.state.id = payload["id"]
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirat")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invàlid")


# Endpoint: Grupos
@app.post("/grupos")
def crear_grupo(grupo: Grupo, request: Request, miembros: list):
    verificar_token(request)
    id_grupo = bd.crear_grupo(request.state.id, grupo.nombre, grupo.descripcion, miembros)
    return {"id_grupo": id_grupo, "mensaje": "Grup creat correctament"}

@app.get("/grupos")
def llistar_grupos(request: Request):
    verificar_token(request)
    grupos = bd.llistar_grupos(request.state.id)
    return {"grupos": grupos}

# Endpoint: Missatges entre usuaris
@app.post("/missatgesAmics")
def enviar_missatge(missatge: Mensaje, request: Request):
    verificar_token(request)
    bd.enviar_missatge(request.state.id, missatge.destinatario, missatge.mensaje)  
    return {"mensaje": "Missatge enviat correctament"}

@app.get("/missatgesAmics")
def obtenir_missatges(destinatario: int, request: Request):
    verificar_token(request)
    missatges = bd.obtener_mensajes(request.state.id, destinatario)
    return {"missatges": missatges}

# Endpoint: Missatges en grups
@app.post("/missatgesGrup")
def enviar_missatge_grup(missatge: MensajeGrup, request: Request):
    verificar_token(request)
    bd.enviar_missatge_grup(request.state.id, missatge.id_grupo, missatge.mensaje)
    return {"mensaje": "Missatge enviat correctament al grup"}

@app.get("/missatgesGrup")
def obtenir_missatges_grup(id_grupo: int, request: Request):
    verificar_token(request)
    missatges = bd.obtenir_missatges_grup(id_grupo)
    return {"missatges": missatges}

# Endpoint: Canviar estat de missatge
@app.post("/check")
def canviar_estat(id_missatge: int, nou_estat: str, request: Request):
    verificar_token(request)
    bd.canviar_estat_missatge(id_missatge, nou_estat)
    return {"mensaje": f"Estat del missatge {id_missatge} actualitzat a {nou_estat}"}

@app.get("/usuarios")
def obtener_usuarios():
    usuarios = bd.obtener_todos_los_usuarios()
    return {"usuarios": usuarios}

