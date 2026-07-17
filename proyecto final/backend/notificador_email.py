"""
Envío de notificaciones por correo cuando a alguien le superan una puja y no
tiene la app abierta en esta sesión (ver main.py: procesar_notificaciones_pendientes).

Usa smtplib con la configuración en backend/data/config_email.json. Ese
archivo NO se versiona con credenciales reales -- lo que se entrega es
backend/data/config_email.example.json como plantilla; hay que copiarlo a
config_email.json y completarlo con credenciales propias (por ejemplo una
"contraseña de aplicación" de Gmail, no la contraseña normal de la cuenta)
para que el envío funcione de verdad. Sin ese archivo, la app sigue
funcionando normal: las notificaciones igual se generan y se pueden ver en
el panel de notificaciones / el badge de Subastas Activas, simplemente nadie
recibe el correo.

TODO (diferido, mismo criterio que la generación del Excel en sistema.py):
este envío es SINCRÓNICO y bloquea el hilo de la UI mientras dura la
conexión SMTP. Tiene un timeout corto para no colgar la app por mucho
tiempo si el servidor no responde, pero lo correcto a futuro es moverlo a
un hilo aparte.
"""

import json
import smtplib
from email.mime.text import MIMEText

TIMEOUT_SEGUNDOS = 5

CAMPOS_REQUERIDOS = ("smtp_host", "smtp_port", "remitente", "password")


def cargar_configuracion_email(ruta):
    """Devuelve el dict de configuración, o None si el archivo no existe o
    le falta algún campo requerido -- mismo criterio tolerante que
    cargar_sesion()/cargar_preferencias() en main.py: nunca rompe la app,
    solo hace que enviar_correo_notificacion() se salte silenciosamente."""
    try:
        with open(ruta, encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    if not all(config.get(campo) for campo in CAMPOS_REQUERIDOS):
        return None
    return config


def enviar_correo_notificacion(config, destinatario_email, asunto, cuerpo):
    """Intenta mandar un correo simple de texto plano. Nunca lanza
    excepciones hacia afuera: cualquier problema de red o de credenciales se
    devuelve como (False, mensaje) para que el llamador lo loguee sin romper
    el resto del flujo de la app (ver main.py: procesar_notificaciones_pendientes)."""
    if not config:
        return False, "No hay configuración de correo cargada (backend/data/config_email.json)."
    if not destinatario_email:
        return False, "El usuario destino no tiene correo registrado."

    mensaje = MIMEText(cuerpo, "plain", "utf-8")
    mensaje["Subject"] = asunto
    mensaje["From"] = config["remitente"]
    mensaje["To"] = destinatario_email

    try:
        with smtplib.SMTP(config["smtp_host"], int(config["smtp_port"]), timeout=TIMEOUT_SEGUNDOS) as servidor:
            if config.get("usar_tls", True):
                servidor.starttls()
            servidor.login(config["remitente"], config["password"])
            servidor.sendmail(config["remitente"], [destinatario_email], mensaje.as_string())
        return True, "Correo enviado."
    except Exception as e:
        return False, f"No se pudo enviar el correo: {e}"
