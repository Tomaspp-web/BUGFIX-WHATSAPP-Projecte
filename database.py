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
        FROM grupos g
        JOIN usuarios_grupo ug ON g.id = ug.id_grupos
        WHERE ug.id_usuario = %s
        """
        self.cursor.execute(sql, (id_usuario,))
        return self.cursor.fetchall()

    def crear_grupo(self, id_usuario, nombre, descripcion, miembros):
        try:
            sql = "INSERT INTO grupos (nombre, descripcion) VALUES (%s, %s)"
            self.cursor.execute(sql, (nombre, descripcion))

            sql = "SELECT id FROM grupos WHERE nombre = %s ORDER BY id DESC LIMIT 1"
            self.cursor.execute(sql, (nombre))
            resultado = self.cursor.fetchone()

            if not resultado:
                raise Exception("No se pudo obtener el ID del grupo recién creado")

            id_grupo = resultado["id"]

            self.nuevo_admin(id_usuario, id_grupo)

            sql = "INSERT INTO usuarios_grupo (id_grupos, id_usuario) VALUES (%s, %s)"
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
        sql = "SELECT COUNT(*) FROM usuarios_grupo WHERE id_grupos = %s AND id_usuario = %s"
        self.cursor.execute(sql, (id_grupo, miembro))
        cuenta = self.cursor.fetchone()

        if cuenta and cuenta["COUNT(*)"] > 0:
            return "Este usuario ya es miembro del grupo"

        admins = self.obtener_admins(id_grupo)

        if id_usuario in [admin["id_usuario"] for admin in admins]:
            sql = "INSERT INTO usuarios_grupo (id_grupos, id_usuario) VALUES (%s, %s)"
            self.cursor.execute(sql, (id_grupo, miembro))
            return "Miembro añadido"
        else:
            return "No tienes permisos para añadir a este usuario"

    def eliminar_miembro(self, id_usuario, id_grupo, id_miembro):
        admins = self.obtener_admins(id_grupo)
        if id_usuario in [admin["id_usuario"] for admin in admins]:
            sql = "DELETE FROM usuarios_grupo WHERE id_grupos = %s AND id_usuario = %s"
            self.cursor.execute(sql, (id_grupo, id_miembro))
            self.eliminar_admin(id_grupo, id_miembro)
            return "Miembro eliminado"
        else:
            return "No tienes permisos para eliminar a este usuario"
        
    def eliminar_admin(self, id_grupo, id_admin):
        sql = "DELETE FROM grupos_administradores WHERE id_grupo = %s AND id_usuario = %s"
        self.cursor.execute(sql, (id_grupo, id_admin))
        return "Admin eliminado"
    
        
    def obtener_miembros(self, id_grupo):
        sql = """SELECT ug.id_usuario, u.username, 
       CASE 
           WHEN ga.id_usuario IS NOT NULL THEN 1 
           ELSE 0 
       END AS es_admin
        FROM usuarios_grupo ug
        INNER JOIN usuarisclase u ON ug.id_usuario = u.id
        LEFT JOIN grupos_administradores ga 
       ON ga.id_usuario = ug.id_usuario 
       AND ga.id_grupo = ug.id_grupos
        WHERE ug.id_grupos = %s
        ORDER BY es_admin DESC, u.username ASC;
        """
        self.cursor.execute(sql, (id_grupo))
        return self.cursor.fetchall()

    def enviar_missatge_U(self, id_emisor, id_receptor, missatge):
        sql = "INSERT INTO missatges_u (id_usuario_envia, id_usuario_recibe, text, estat) VALUES (%s, %s, %s, 'enviado')"
        self.cursor.execute(sql, (id_emisor, id_receptor, missatge))

    def obtener_mensajes(self, id_usuario, destinatario, pagina, limit=15):
        offset = pagina * limit
        sql = """
        SELECT mu.id_usuario_envia, u.username AS nom_usuari, mu.text, mu.estat, mu.date
    FROM missatges_u mu JOIN usuarisclase u ON mu.id_usuario_envia = u.id WHERE (mu.id_usuario_envia = %s AND mu.id_usuario_recibe = %s) 
    OR (mu.id_usuario_envia = %s AND mu.id_usuario_recibe = %s) ORDER BY mu.date DESC LIMIT %s OFFSET %s;
        """
        self.cursor.execute(
            sql, (id_usuario, destinatario, destinatario, id_usuario, limit, offset)
        )
        mensajes = self.cursor.fetchall()
        return mensajes

    def enviar_missatge_G(self, id_grup, id_usuari, missatge):
        sql = "INSERT INTO missatges_g (id_grup, id_usuari, text, estat) VALUES (%s, %s, %s, 'enviado')"
        self.cursor.execute(sql, (id_grup, id_usuari, missatge))

    def obtenir_missatges_G(self, id_usuario, id_grupo, pagina, limit=15):
        offset = pagina * limit
        
        sql = """SELECT g.id_usuari, u.username AS nom, g.text, 
    CASE 
        WHEN (
            SELECT COUNT(*) 
            FROM usuarios_grupo gu 
            WHERE gu.id_grupos = g.id_grup AND gu.id_usuario != %s
        ) = (
            SELECT COUNT(*) 
            FROM estado_lectura_mensajes e 
            WHERE e.id_mensaje = g.id AND e.id_usuario != %s
        ) 
        THEN 'leido' 
        ELSE 'enviado' 
    END AS estat, 
    g.date 
    FROM missatges_g g
    INNER JOIN usuarisclase u ON u.id = g.id_usuari
    WHERE g.id_grup = %s 
    ORDER BY g.date DESC 
    LIMIT %s OFFSET %s;"""

        self.cursor.execute(sql, (id_usuario, id_usuario, id_grupo, limit, offset))
        mensajes = self.cursor.fetchall()
        return mensajes

    def obtener_usuarios(self, id_usuario):
        sql = """SELECT u.id AS id_usuario, u.username AS nombre_usuario,
                COALESCE(MAX(mu.date), '1900-01-01') AS ultima_actividad
                FROM usuarisclase u
                LEFT JOIN missatges_u mu 
                    ON (u.id = mu.id_usuario_envia OR u.id = mu.id_usuario_recibe)
                    AND (mu.id_usuario_envia = %s OR mu.id_usuario_recibe = %s)
                WHERE u.id != %s
                GROUP BY u.id
                ORDER BY ultima_actividad desc;"""
        self.cursor.execute(sql, (id_usuario, id_usuario, id_usuario))
        return self.cursor.fetchall()

    def cambiar_estado_U(self, estado, id_contacto, id_usuario):
        sql = "UPDATE missatges_u SET estat = %s WHERE id_usuario_envia = %s and id_usuario_recibe = %s;"
        self.cursor.execute(sql, (estado, id_contacto, id_usuario))

    def cambiar_estado_G(self, id_grupo, id_usuario):
        sql = """INSERT INTO estado_lectura_mensajes (id_mensaje, id_usuario, fecha_lectura)
        SELECT mg.id, %s, CURRENT_TIMESTAMP
        FROM missatges_g mg
        LEFT JOIN estado_lectura_mensajes e 
        ON mg.id = e.id_mensaje AND e.id_usuario = %s
        WHERE mg.id_grup = %s AND e.id_mensaje IS NULL;
        """
        self.cursor.execute(sql, (id_usuario, id_usuario, id_grupo))

    def cambiar_estado_mensajes(self, ids_mensajes, id_usuario):
        sql = """
        INSERT INTO estado_lectura_mensajes (id_mensaje, id_usuario) 
        VALUES (%s, %s) 
        ON DUPLICATE KEY UPDATE fecha_lectura = CURRENT_TIMESTAMP;
        """
        for id_mensaje in ids_mensajes:
            self.cursor.execute(sql, (id_mensaje, id_usuario))
        self.conexion.commit()

    def get_username(self, id_usuario):
        sql = "SELECT username FROM usuarisclase WHERE id = %s"
        self.cursor.execute(sql, (id_usuario))
        return self.cursor.fetchone()["username"]

    def get_nom_grup(self, id_grup):
        sql = "SELECT nombre FROM grupos WHERE id = %s"
        self.cursor.execute(sql, (id_grup))
        return self.cursor.fetchone()["nombre"]
    
    def obtener_admins(self, id_grupo):
        sql = """SELECT ga.id_usuario, u.username as username FROM grupos_administradores ga
                inner join grupos g on g.id = ga.id_grupo
                inner join usuarisclase u on ga.id_usuario = u.id
                WHERE g.id = %s;"""
        self.cursor.execute(sql, (id_grupo))
        return self.cursor.fetchall()
    
    def nuevo_admin(self, id_usuario, id_grupo):
        sql = "INSERT INTO grupos_administradores (id_usuario, id_grupo) VALUES (%s, %s)"
        self.cursor.execute(sql, (id_usuario, id_grupo))

    def obtener_contactos(self, id_usuario):
        sql = """(
    SELECT g.id AS id_grupo, g.nombre AS nombre_grupo, 
           NULL AS id_usuario, NULL AS nombre_usuario,
           COALESCE(MAX(mg.date), g.fecha_creacion) AS ultima_actividad,
           (
               SELECT COUNT(*) 
               FROM missatges_g mg2
               WHERE mg2.id_grup = g.id 
               AND mg2.id NOT IN (
                   SELECT e.id_mensaje 
                   FROM estado_lectura_mensajes e 
                   WHERE e.id_usuario = %s
               )
           ) AS mensajes_nuevos
    FROM grupos g
    INNER JOIN usuarios_grupo ug ON g.id = ug.id_grupos
    LEFT JOIN missatges_g mg ON g.id = mg.id_grup
    WHERE ug.id_usuario = %s
    GROUP BY g.id
    )
    UNION ALL
    (
        SELECT NULL AS id_grupo, NULL AS nombre_grupo, 
           u.id AS id_usuario, u.username AS nombre_usuario,
           COALESCE(MAX(mu.date), '1900-01-01') AS ultima_actividad,
           (
               SELECT COUNT(*) 
               FROM missatges_u mu2
               WHERE mu2.id_usuario_envia = u.id 
               AND mu2.id_usuario_recibe = %s
               AND mu2.estat = 'enviado'
            ) AS mensajes_nuevos
    FROM usuarisclase u
    LEFT JOIN missatges_u mu 
    ON (u.id = mu.id_usuario_envia OR u.id = mu.id_usuario_recibe)
    AND (mu.id_usuario_envia = %s OR mu.id_usuario_recibe = %s)
    WHERE u.id != %s
    GROUP BY u.id
    )
    ORDER BY ultima_actividad DESC;

            """
        self.cursor.execute(
            sql, (id_usuario, id_usuario, id_usuario, id_usuario, id_usuario, id_usuario)
        )
        return self.cursor.fetchall()
