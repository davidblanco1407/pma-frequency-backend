# 🎧 PMA Frequency – Backend

Este es el backend del sistema **PMA Frequency**, una plataforma para la gestión de miembros, sanciones y solicitudes en una comunidad de producción musical con enfoque en accesibilidad para personas con discapacidad visual.

Construido con **Django + Django REST Framework**, este backend se encarga de la lógica, seguridad, autenticación y conexión con base de datos.

---

## ⚙️ Tecnologías utilizadas

- [Python 3.11+](https://www.python.org/)
- [Django 4.x](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [MySQL](https://www.mysql.com/) (puede usarse SQLite en desarrollo)
- [django-cors-headers](https://pypi.org/project/django-cors-headers/)

---

## 🚀 Instalación y configuración

1. Clona este repositorio:

```bash
git clone https://github.com/davidblanco1407/pma-frequency-backend.git
cd pma-frequency-backend
````

2. Crea y activa un entorno virtual:

```bash
python -m venv env
source env/bin/activate  # o env\Scripts\activate en Windows
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Crea y configura el archivo `.env`:

```env
DEBUG=True
SECRET_KEY=tu_clave_secreta
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:5173
DEFAULT_FROM_EMAIL=no-reply@pmafrequency.com
EMAIL_HOST=smtp.tudominio.com
EMAIL_PORT=587
EMAIL_HOST_USER=usuario@tudominio.com
EMAIL_HOST_PASSWORD=clave
EMAIL_USE_TLS=True
```

5. Configura la base de datos en `settings.py` o vía `.env`.

6. Ejecuta migraciones:

```bash
python manage.py migrate
```

7. Crea un superusuario:

```bash
python manage.py createsuperuser
```

8. Levanta el servidor:

```bash
python manage.py runserver
```

---

## 📚 Estructura general

```
pma_frequency/
│
├── miembros/            # App principal: modelos, vistas, serializers
│   ├── models.py        # Modelos: Miembro, Sancion, SolicitudCorreccion
│   ├── views.py         # Lógica principal: CRUD, autenticación, filtros
│   ├── serializers.py   # Serializadores para API
│   ├── urls.py          # Endpoints personalizados y con router
│   └── utils.py         # Funciones auxiliares (crear usuario, correos)
│
├── pma_frequency/       # Configuración principal del proyecto
│   ├── settings.py      # Configuración de Django y JWT
│   └── urls.py          # Enrutamiento global
│
└── requirements.txt     # Dependencias
```

---

## 🔐 Autenticación

La API utiliza **JWT** con `SimpleJWT`.

* Inicio de sesión: `/api/token/`
* Refresh: `/api/token/refresh/`

Solo los **miembros activos** pueden autenticarse. Los bloqueados o inactivos no podrán ingresar, a menos que un administrador los reactive.

---

## 📡 Endpoints principales

| Método | Endpoint                            | Descripción                                | Rol requerido     |
| ------ | ----------------------------------- | ------------------------------------------ | ----------------- |
| POST   | `/api/token/`                       | Autenticación con JWT                      | Todos             |
| GET    | `/api/miembros/mi-perfil/`          | Ver perfil del miembro autenticado         | Miembro           |
| POST   | `/api/miembros/`                    | Crear nuevo miembro                        | Solo superusuario |
| GET    | `/api/miembros/`                    | Listado de miembros                        | Admin             |
| PUT    | `/api/miembros/{id}/`               | Editar miembro                             | Admin             |
| GET    | `/api/miembros/sanciones/`          | Listado de sanciones                       | Admin             |
| POST   | `/api/miembros/sanciones/`          | Crear sanción                              | Admin             |
| GET    | `/api/miembros/solicitudes/`        | Ver solicitudes (propias o todas si admin) | Todos             |
| PATCH  | `/api/miembros/solicitudes/{id}`    | Actualizar respuesta/estado (solo admin)   | Admin             |
| POST   | `/api/miembros/cambiar-password/`   | Cambiar contraseña                         | Todos             |
| POST   | `/api/miembros/recuperar-password/` | Enviar correo para reset                   | Todos             |

---

## ✉️ Correos automáticos

El sistema puede enviar:

* Correo de bienvenida con credenciales
* Recuperación de contraseña (token y link)
* (Futuro) Notificaciones de sanciones o respuestas

---

## 📌 Objetivo del proyecto

Este sistema nació con la misión de facilitar la inclusión de personas con discapacidad visual en el ecosistema de producción musical. Más que código, **es una herramienta de empoderamiento y comunidad**.

---

## 📄 Licencia

MIT — Libre para usar, mejorar y compartir.

---
