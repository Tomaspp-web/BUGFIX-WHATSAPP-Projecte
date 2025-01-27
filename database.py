import pymysql.cursors
import scrypt 

class BaseDeDatos:
    def __init__(self):
        self.conexion = pymysql.connect(
            host='192.168.193.133',
            user='miquelgarcia',
            password='78222286E',
            db='bugfix',
            charset='utf8mb4',
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conexion.cursor()

    def cerrar(self):
        self.conexion.close()
        
    
    def verificar_password(self, password, hashed_password):
        salt, key = hashed_password.split('$')[1], hashed_password.split('$')[2]
        hashed_input_password = scrypt.hash(password, salt, N=32768, r=8, p=1).hex()
        return hashed_input_password == key
        
    def obtener_usuari(self, username, password):
        sql = "SELECT id, username, password FROM usuarisclase WHERE username = %s"
        self.cursor.execute(sql, (username,))
        usuario = self.cursor.fetchone()
        if usuario and self.verificar_password(password, usuario['password']):
            return usuario
        return None



    def obtener_amigos(self, username):
        sql = "SELECT * FROM amics WHERE username = %s"
        self.cursor.execute(sql, (username))
        return self.cursor.fetchall()
    
    def llistar_grupos(self, id_usuario):
        sql = "SELECT * FROM Usuarios_grupo WHERE id_usuario = %s"
        self.cursor.execute(sql, (id_usuario))
        return self.cursor.fetchall()
    
    def crear_grupo(self, id_usuari, nom, descripcion, miembros):
        sql = "INSERT INTO GRUPOS (nombre, id_usuario, descripcion) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (nom, id_usuari, descripcion))
        sql = "SELECT id FROM GRUPOS WHERE nombre = %s ORDER BY id DESC LIMIT 1"
        self.cursor.execute(sql, (nom))
        id_grupo = self.cursor.fetchone()['id']
        sql = "INSERT INTO Usuarios_grupo (id_grupo, id_usuario) VALUES (%s, %s)"
        self.cursor.execute(sql, (id_grupo, id_usuari))
        if (miembros):
            for miembro in miembros:
                self.añadir_miembro(id_usuari, id_grupo, miembro)

    def añadir_miembro(self, id_usuario, id_grupo, miembro):
        sql = "SELECT id_grupo FROM GRUPOS WHERE id = %s"
        self.cursor.execute(sql, (id_usuario))
        if self.cursor.fetchone()['id_grupo'] == id_grupo:
            sql = "INSERT INTO Usuarios_grupo (id_grupo, id_usuario) VALUES (%s, %s)"
            self.cursor.execute(sql, (id_grupo, miembro))
            return "Miembro añadido"
        else:
            return "No tienes permisos para añadir a este usuario"
    
    def eliminar_miembro(self, id_usuario, id_grupo, id_miembro):
        sql = "SELECT id_grupo FROM GRUPOS WHERE id = %s"
        self.cursor.execute(sql, (id_usuario))
        if self.cursor.fetchone()['id_grupo'] == id_grupo:
            sql = "DELETE FROM Usuarios_grupo WHERE id_grupo = %s AND id_usuario = %s"
            self.cursor.execute(sql, (id_grupo, id_miembro))
            return "Miembro eliminado"
        else:
            return "No tienes permisos para eliminar a este usuario"

    def enviar_missatge(self, id_emisor, username_receptor, missatge):
        sql = "INSERT INTO MISSATGES_U (id_usuario_envia, id_usuario_recibe, text, estat) VALUES (%s, %s, %s, 'enviado')"
        self.cursor.execute(sql, (id_emisor, username_receptor, missatge))
    
    def obtener_todos_los_usuarios(self):
        sql = "SELECT id, username FROM usuarisclase"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def obtener_mensajes(self, id_usuario, destinatario):
        sql = "SELECT * from MISSATGES_U WHERE id_usuario_envia = %s and id_usuario_recibe = %s or id_usuario_envia = %s and id_usuario_recibe = %s ORDER BY date;"
        self.cursor.execute(sql, (id_usuario, destinatario, destinatario, id_usuario))
        mensajes = self.cursor.fetchall()
        sql = "UPDATE missatges SET estat = 'leido' WHERE id_usuario_recibe = %s and id_usuario_envia = %s"
        self.cursor.execute(sql, (id_usuario, destinatario))
        return mensajes

    def cambiar_estado_mensaje(self, id_mensaje, estado):
        sql = "UPDATE missatges SET estat = %s WHERE id = %s"
        self.cursor.execute(sql, (estado, id_mensaje))

    def get_username(self, id_usuario):
        sql = "SELECT username FROM usuarisclase WHERE id = %s"
        self.cursor.execute(sql, (id_usuario))
        return self.cursor.fetchone()['username']
    
    
    


    

    
