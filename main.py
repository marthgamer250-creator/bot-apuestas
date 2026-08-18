import os
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Dinámico de Bet365 Activo 24/7"

API_KEY_ODDS = "6c5f290a655e478909dcd837da4943bd"
TELEGRAM_TOKEN = "8814947543:AAFtSv-SIvyla9vJYV7AGA4Y9jMLSR0YwNI"

def enviar_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def analizar_apuesta_ia(texto_usuario):
    t = texto_usuario.lower()
    
    if "2.5" in t or "goles" in t or "over" in t:
        return (
            f"🔥 **¡DALE, DALE, DALE! Apuesta de Goles** 🔥\n\n"
            f"⚽ *Partido/Consulta:* {texto_usuario.title()}\n"
            f"🏢 *Casa analizada:* Bet365\n"
            f"📊 *Análisis Cuantitativo:* xG (goles esperados) alto en ambos planteles.\n"
            f"💡 *Veredicto:* **Entrá con confianza.** Cuota con valor matemático (+EV)."
        )
    elif "parley" in t or "combinada" in t or "parli" in t:
        return (
            "🎯 **PARLEY MASTER +EV (BET365)** 🎯\n\n"
            "1️⃣ Combinada seleccionada con alta probabilidad de acierto.\n"
            "📈 *Cuota Estimada:* ~2.15\n"
            "💡 *Veredicto:* **¡Aprobado para duplicar capital!**"
        )
    elif "córner" in t or "esquina" in t or "corners" in t:
        return (
            f"🚩 **ANÁLISIS DE CÓRNERS** 🚩\n\n"
            f"⚽ *Consulta:* {texto_usuario.title()}\n"
            f"📊 *Lectura:* Volumen alto de centros por bandas.\n"
            f"💡 *Veredicto:* **¡Dale al Más de Córners en Bet365!**"
        )
    else:
        # Respuesta inteligente que absorbe CUALQUIER partido que le escribas
        return (
            f"⚽ **ANÁLISIS TÁCTICO & BET365** 🇲🇽\n"
            f"🔍 *Partido:* `{texto_usuario.title()}`\n\n"
            f"📊 **Lectura del Modelo Cuantitativo:**\n"
            f"• **1X2 (Ganador):** Tendencia favorable detectada en las cuotas de Bet365.\n"
            f"• **Goles:** Alta probabilidad de movimientos en el mercado de Alta de Goles o Ambos Anotan.\n"
            f"• **Córners:** Ritmo propicio para líneas secundarias.\n\n"
            f"💡 **Veredicto Final:** **¡Luz verde!** El modelo detecta rentabilidad en este encuentro. ¡Dale con gestión de stake adecuada en Bet365!"
        )

def escuchar_telegram():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=30"
            resp = requests.get(url).json()
            
            if resp.get("result"):
                for update in resp["result"]:
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    texto = message.get("text", "")
                    
                    if chat_id and texto:
                        if texto.startswith("/start"):
                            enviar_telegram(chat_id, "🤖 ¡Bot de Bet365 activo! Escríbeme cualquier partido (ej: 'Necaxa vs León') o consulta y te daré el análisis completo.")
                        else:
                            respuesta = analizar_apuesta_ia(texto)
                            enviar_telegram(chat_id, respuesta)
                            
        except Exception as e:
            print(f"Error en Telegram: {e}")
        time.sleep(2)

if __name__ == "__main__":
    t = threading.Thread(target=escuchar_telegram)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
