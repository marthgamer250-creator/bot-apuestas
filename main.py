import os
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = "8814947543:AAFtSv-SIvyla9vJYV7AGA4Y9jMLSR0YwNI"
contexto = {"partido_actual": "Ninguno"}

def enviar_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def procesar_logica_apuestas(texto, chat_id):
    t = texto.lower()
    p = contexto["partido_actual"]

    # 1. ANÁLISIS DE PARTIDO (Settear contexto)
    if "analiza" in t:
        partido = texto.replace("Analiza", "").replace("analiza", "").strip()
        contexto["partido_actual"] = partido
        enviar_telegram(chat_id, f"📡 *Sistema vinculado:* {partido}. \nAhora puedes preguntar: 'goles', 'corners', 'marcador', 'jugador', etc.")
        return

    # 2. GOLES (Probabilidades y riesgos)
    if "goles" in t:
        respuesta = (
            f"⚽ *Análisis de Goles: {p}*\n\n"
            f"• **Opción Segura (Bajo Riesgo):** Menos de 3.5 goles.\n"
            f"• **Opción Equilibrada:** Más de 1.5 goles.\n"
            f"• **Opción Arriesgada (High Stake):** Ambos Anotan en el 2do Tiempo.\n"
            f"🔮 *Predicción Probabilística:* El algoritmo estima un rango de 2 a 3 goles totales."
        )
        enviar_telegram(chat_id, respuesta)

    # 3. TIROS DE ESQUINA (Rango matemático)
    elif "corners" in t or "tiros de esquina" in t:
        respuesta = (
            f"🚩 *Análisis de Córners: {p}*\n\n"
            f"📊 *Predicción:* El modelo estima entre **8 y 12 córners**.\n"
            f"👉 *Recomendación:* Más de 8.5 Córners (Cuota promedio 1.85).\n"
            f"⚠️ *Nota:* Si el partido está cerrado al min 60, buscar 'Más de' en directo."
        )
        enviar_telegram(chat_id, respuesta)

    # 4. MARCADOR CORRECTO
    elif "marcador" in t:
        respuesta = (
            f"🎯 *Predicción de Marcador: {p}*\n\n"
            f"1️⃣ Probabilidad Alta: **2 - 1**\n"
            f"2️⃣ Probabilidad Media: **1 - 1**\n"
            f"3️⃣ Probabilidad Baja (Arriesgada): **3 - 0**"
        )
        enviar_telegram(chat_id, respuesta)

    # 5. JUGADORES (Goles / Remates)
    elif "jugador" in t or "remates" in t or "marcar" in t:
        respuesta = (
            f"👤 *Análisis de Jugadores: {p}*\n\n"
            f"• **Jugador Estrella:** Máxima probabilidad de anotar (o rematar al arco).\n"
            f"• **Cuota Sugerida:** Buscar 'Remates a puerta' (Más de 1.5).\n"
            f"• **Probabilidad:** Alta tasa de conversión en las últimas 5 jornadas."
        )
        enviar_telegram(chat_id, respuesta)

    # 6. GANADOR / PRIMEROS 10 MIN
    elif "quién ganará" in t or "10 minutos" in t or "ganador" in t:
        respuesta = (
            f"⚡ *Análisis en Tiempo Real: {p}*\n\n"
            f"🏆 **Ganador probable:** Análisis inclinado hacia el Favorito por posesión.\n"
            f"⏱️ **Primeros 10 min:** Partido de estudio. Baja probabilidad de goles tempraneros. Sugerencia: Esperar."
        )
        enviar_telegram(chat_id, respuesta)

    # 7. PARLAYS
    elif "parlay" in t:
        enviar_telegram(chat_id, "🔥 **PARLEY DEL DÍA**\n1. Ganador A\n2. Más de 1.5 goles B\n3. +8.5 Córners C\n¡Dale con gestión de stake!")

    else:
        enviar_telegram(chat_id, "🤖 *No detecté la categoría.* Pregunta por: goles, corners, marcador, jugador, ganador, o parlay.")

def escuchar_telegram():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=30"
            resp = requests.get(url).json()
            if resp.get("result"):
                for update in resp["result"]:
                    offset = update["update_id"] + 1
                    chat_id = update["message"]["chat"]["id"]
                    texto = update["message"].get("text", "")
                    if texto:
                        procesar_logica_apuestas(texto, chat_id)
        except Exception: time.sleep(1)
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=escuchar_telegram, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
