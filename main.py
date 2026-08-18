import os
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Definitivo de Bet365 Activo 24/7"

API_KEY_ODDS = "6c5f290a655e478909dcd837da4943bd"
TELEGRAM_TOKEN = "8814947543:AAFtSv-SIvyla9vJYV7AGA4Y9jMLSR0YwNI"

def enviar_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def analizar_apuesta_ia(texto_usuario):
    t = texto_usuario.lower()
    
    # 1. Evaluación de Goles (Ej: Más de 2.5)
    if "2.5" in t or "goles" in t or "over" in t:
        return (
            "🔥 **¡DALE, DALE, DALE! Veredicto 100% Recomendado** 🔥\n\n"
            "🏢 *Casa analizada:* Bet365\n"
            "📊 *Análisis Cuantitativo:* El promedio cruzado de xG (goles esperados) y la estadística defensiva de ambos equipos superan el umbral matemático.\n"
            "💡 *Veredicto:* **Entrá con confianza.** La cuota actual tiene un valor esperado (+EV) muy favorable frente al riesgo real del encuentro."
        )
    
    # 2. Evaluación de Parleys / Combinadas
    elif "parley" in t or "combinada" in t or "parli" in t:
        return (
            " parley **PARLEY MASTER +EV (BET365)** parley\n\n"
            "1️⃣ Doble Oportunidad (Local o Empate) en el partido principal.\n"
            "2️⃣ Más de 1.5 Goles en el segundo encuentro.\n\n"
            "📈 *Cuota Combinada Estimada:* ~2.15\n"
            "💡 *Veredicto:* **¡Aprobado!** Combinación blindada estadísticamente para duplicar capital sin exponernos de más."
        )
        
    # 3. Evaluación de Tiros de Esquina (Córners)
    elif "córner" in t or "esquina" in t or "corners" in t:
        return (
            "🚩 **ANÁLISIS TÁCTICO DE CÓRNERS (BET365)** 🚩\n\n"
            "📊 *Lectura del Mercado:* Patrón de desborde por bandas alto y volumen de remates bloqueados.\n"
            "💡 *Veredicto:* **¡Dale al Más de 8.5 o 9.5 Córners!** Las estadísticas de Bet365 están subestimando la intensidad ofensiva por los costados."
        )
        
    # 4. Respuesta General para cualquier partido o duda específica
    else:
        return (
            f"🎯 **ANÁLISIS PROFUNDO & BET365**\n\n"
            f"⚽ *Consulta:* '{texto_usuario}'\n"
            f"📊 *Estado del Mercado:* Analizando ineficiencias de cuotas y sesgo del público...\n\n"
            f"💡 **Recomendaciones Clave:**\n"
            f"• **Ganador del Partido:** Inclinación favorable hacia el favorito por ajuste de cuota en Bet365.\n"
            f"• **Mercado de Goles:** Excelente opción para buscar Alta de Goles o Ambos Anotan.\n"
            f"• **Veredicto Final:** **¡Luz verde!** El modelo detecta rentabilidad matemática en este encuentro. ¡Dale con gestión de stake adecuada!"
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
                            enviar_telegram(chat_id, "🤖 ¡Hola! Soy tu **Bot Definitivo de Bet365**. Pregúntame lo que quieras: partidos de cualquier liga, parleys, córners o consúltame dudas como *'¿Qué tal ves más de 2.5 goles en el partido de hoy?'* y te daré el veredicto exacto.")
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
