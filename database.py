import pymysql.cursors
import scrypt


class BaseDeDatos:
    def __init__(self):
        self.conexion = pymysql.connect(
            host="192.168.193.133",
            user="miquelgarcia",
            password="78222286E",
            db="bugfix",
            charset="utf8mb4",
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.conexion.cursor()

    def cerrar(self):
        self.conexion.close()

    def verificar_password(self, password, hashed_password):
        salt, key = hashed_password.split("$")[1], hashed_password.split("$")[2]
        hashed_input_password = scrypt.hash(password, salt, N=32768, r=8, p=1).hex()
        return hashed_input_password == key

    def obtener_usuario(self, username):
        sql = "SELECT * FROM usuarisclase WHERE username = %s"
        self.cursor.execute(sql, (username,))
        usuario = self.cursor.fetchone()
        return usuario

    def obtener_amigos(self, username):
        sql = "SELECT * FROM amics WHERE username = %s"
        self.cursor.execute(sql, (username))
        return self.cursor.fetchall()

    def llistar_grupos(self, id_usuario):
        sql = """
        SELECT g.id, g.nombre, g.descripcion
        FROM GRUPOS g
        JOIN Usuarios_grupo ug ON g.id = ug.id_grupos
        WHERE ug.id_usuario = %s
        """
        self.cursor.execute(sql, (id_usuario,))
        return self.cursor.fetchall()

    def crear_grupo(self, id_usuario, nombre, descripcion, miembros):
        try:
            sql = "INSERT INTO GRUPOS (nombre, descripcion, id_usuario) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (nombre, descripcion, id_usuario))

            sql = "SELECT id FROM GRUPOS WHERE nombre = %s ORDER BY id DESC LIMIT 1"
            self.cursor.execute(sql, (nombre,))
            resultado = self.cursor.fetchone()

            if not resultado:
                raise Exception("No se pudo obtener el ID del grupo recién creado")

            id_grupo = resultado["id"]

            sql = "INSERT INTO Usuarios_grupo (id_grupos, id_usuario) VALUES (%s, %s)"
            self.cursor.execute(sql, (id_grupo, id_usuario))

            for miembro in miembros:
                self.añadir_miembro(id_usuario, id_grupo, miembro)

            self.conexion.commit()
            return id_grupo

        except Exception as e:
            print(f"Error al crear el grupo: {e}")
            self.conexion.rollback()
            return None

    def añadir_miembro(self, id_usuario, id_grupo, miembro):
        sql = "SELECT COUNT(*) FROM Usuarios_grupo WHERE id_grupos = %s AND id_usuario = %s"
        self.cursor.execute(sql, (id_grupo, miembro))
        cuenta = self.cursor.fetchone()

        if cuenta and cuenta["COUNT(*)"] > 0:
            return "Este usuario ya es miembro del grupo"

        sql = "SELECT id_usuario FROM GRUPOS WHERE id = %s"
        self.cursor.execute(sql, (id_grupo,))

        grupo = self.cursor.fetchone()

        if grupo and grupo["id_usuario"] == id_usuario:
            sql = "INSERT INTO Usuarios_grupo (id_grupos, id_usuario) VALUES (%s, %s)"
            self.cursor.execute(sql, (id_grupo, miembro))
            return "Miembro añadido"
        else:
            return "No tienes permisos para añadir a este usuario"

    def eliminar_miembro(self, id_usuario, id_grupo, id_miembro):
        sql = "SELECT id_grupo FROM GRUPOS WHERE id = %s"
        self.cursor.execute(sql, (id_usuario))
        if self.cursor.fetchone()["id_grupo"] == id_grupo:
            sql = "DELETE FROM Usuarios_grupo WHERE id_grupo = %s AND id_usuario = %s"
            self.cursor.execute(sql, (id_grupo, id_miembro))
            return "Miembro eliminado"
        else:
            return "No tienes permisos para eliminar a este usuario"

    def enviar_missatge_U(self, id_emisor, id_receptor, missatge):
        sql = "INSERT INTO MISSATGES_U (id_usuario_envia, id_usuario_recibe, text, estat) VALUES (%s, %s, %s, 'enviado')"
        self.cursor.execute(sql, (id_emisor, id_receptor, missatge))

    def obtener_mensajes(self, id_usuario, destinatario, pagina, limit=15):
        offset = pagina * limit
        sql = """
        SELECT mu.id_usuario_envia, u.username AS nom_usuari, mu.text, mu.estat, mu.date
    FROM MISSATGES_U mu JOIN usuarisclase u ON mu.id_usuario_envia = u.id WHERE (mu.id_usuario_envia = %s AND mu.id_usuario_recibe = %s) 
    OR (mu.id_usuario_envia = %s AND mu.id_usuario_recibe = %s) ORDER BY mu.date DESC LIMIT %s OFFSET %s;
        """
        self.cursor.execute(
            sql, (id_usuario, destinatario, destinatario, id_usuario, limit, offset)
        )
        mensajes = self.cursor.fetchall()
        return mensajes

    def enviar_missatge_G(self, id_grup, id_usuari, missatge):
        sql = "INSERT INTO MISSATGES_G (id_grup, id_usuari, text, estat) VALUES (%s, %s, %s, 'enviado')"
        self.cursor.execute(sql, (id_grup, id_usuari, missatge))

    def obtenir_missatges_G(self, id_grupo, pagina, limit=15):
        offset = pagina * limit
        sql = """SELECT id_usuari, u.username as nom, text, estat, date FROM MISSATGES_G g
    INNER JOIN usuarisclase u ON u.id = g.id_usuari WHERE id_grup = %s ORDER BY date DESC LIMIT %s OFFSET %s;"""
        self.cursor.execute(sql, (id_grupo, limit, offset))
        mensajes = self.cursor.fetchall()
        sql = "UPDATE MISSATGES_G SET estat = 'leido' WHERE id_grup = %s"
        self.cursor.execute(sql, (id_grupo))
        return mensajes

    def obtener_usuarios(self, id_usuario):
        sql = """SELECT u.id AS id_usuario, u.username AS nombre_usuario,
                COALESCE(MAX(mu.date), '1900-01-01') AS ultima_actividad
                FROM usuarisclase u
                LEFT JOIN MISSATGES_U mu 
                    ON (u.id = mu.id_usuario_envia OR u.id = mu.id_usuario_recibe)
                    AND (mu.id_usuario_envia = %s OR mu.id_usuario_recibe = %s)
                WHERE u.id != %s
                GROUP BY u.id
                ORDER BY ultima_actividad desc;"""
        self.cursor.execute(sql, (id_usuario, id_usuario, id_usuario))
        return self.cursor.fetchall()

    def cambiar_estado_U(self, estado, id_contacto, id_usuario):
        sql = "UPDATE MISSATGES_U SET estat = %s WHERE id_usuario_envia = %s and id_usuario_recibe = %s;"
        self.cursor.execute(sql, (estado, id_contacto, id_usuario))

    def cambiar_estado_G(self, id_mensaje, estado):
        sql = "UPDATE MISSATGES_G SET estat = %s WHERE id = %s"
        self.cursor.execute(sql, (estado, id_mensaje))

    def get_username(self, id_usuario):
        sql = "SELECT username FROM usuarisclase WHERE id = %s"
        self.cursor.execute(sql, (id_usuario))
        return self.cursor.fetchone()["username"]

    def get_nom_grup(self, id_grup):
        sql = "SELECT nombre FROM GRUPOS WHERE id = %s"
        self.cursor.execute(sql, (id_grup))
        return self.cursor.fetchone()["nombre"]

    def obtener_contactos(self, id_usuario):
        sql = """(
            SELECT g.id AS id_grupo, g.nombre AS nombre_grupo, 
                NULL AS id_usuario, NULL AS nombre_usuario,
                COALESCE(MAX(mg.date), g.fecha_creacion) AS ultima_actividad
            FROM GRUPOS g
            INNER JOIN Usuarios_grupo ug ON g.id = ug.id_grupos
            LEFT JOIN MISSATGES_G mg ON g.id = mg.id_grup
            WHERE ug.id_usuario = %s
            GROUP BY g.id
            )
            UNION
            (
            SELECT NULL AS id_grupo, NULL AS nombre_grupo, 
                u.id AS id_usuario, u.username AS nombre_usuario,
                COALESCE(MAX(mu.date), '1900-01-01') AS ultima_actividad
            FROM usuarisclase u
            LEFT JOIN MISSATGES_U mu 
            ON (u.id = mu.id_usuario_envia OR u.id = mu.id_usuario_recibe)
            AND (mu.id_usuario_envia = %s OR mu.id_usuario_recibe = %s)
            WHERE u.id != %s
            GROUP BY u.id
            )
            ORDER BY ultima_actividad DESC;

            """
        self.cursor.execute(sql, (id_usuario, id_usuario, id_usuario, id_usuario))
        return self.cursor.fetchall()
