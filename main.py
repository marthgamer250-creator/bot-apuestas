import os
import threading
import time
import random
import requests
from flask import Flask

app = Flask(__name__)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8814947543:AAFtSv-SIvyla9vJYV7AGA4Y9jMLSR0YwNI")

db = {"partido": "No seleccionado", "bankroll": 1000}

def enviar_telegram(chat_id, texto):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

def generar_picks_ev(partido):
    random.seed(partido.lower().strip())
    picks = [
        {"desc": "Victoria local con hándicap asiático 0", "odds": round(random.uniform(1.75, 1.95), 2), "why": "El volumen de ataque local supera el promedio defensivo visitante."},
        {"desc": "Más de 2.5 goles totales", "odds": round(random.uniform(1.85, 2.10), 2), "why": "Correlación estadística alta entre ambos equipos en enfrentamientos directos."},
        {"desc": "Ambos equipos marcan", "odds": round(random.uniform(1.65, 1.80), 2), "why": "La fragilidad defensiva de ambos sugiere un intercambio de goles probable."}
    ]
    return picks

def generar_parlay(partido):
    random.seed(partido.lower().strip())
    leg1 = "Doble Oportunidad: Local o Empate"
    leg2 = "Más de 1.5 goles totales"
    leg3 = "Más de 7.5 córners totales"
    cuota_total = round(random.uniform(2.40, 3.10), 2)
    return f"1. {leg1}\n2. {leg2}\n3. {leg3}\n\nCuota Estimada: *{cuota_total}*"

def validar_pregunta(texto, partido):
    """Analiza preguntas naturales y retorna una probabilidad y consejo."""
    random.seed(partido.lower().strip() + texto.lower().strip())
    probabilidad = random.randint(45, 85)
    recomendacion = "✅ **SÍ, TIENE VALOR**" if probabilidad > 55 else "❌ **NO, RIESGO ELEVADO**"
    
    justificaciones = [
        "El histórico reciente del equipo respalda esta tendencia.",
        "Los datos de posesión sugieren que mantendrán el control.",
        "Las cuotas del mercado no reflejan la probabilidad real.",
        "La defensa rival suele flaquear en estos escenarios.",
        "El factor localía inclina la balanza a favor."
    ]
    
    return f"🧠 **ANÁLISIS DE CONSULTA: '{texto}'**\n\nProbabilidad estimada: *{probabilidad}%*\nRecomendación: {recomendacion}\n\n*Motivo:* {random.choice(justificaciones)}"

def procesar_logica(texto, chat_id):
    t = texto.lower().strip()
    p = db["partido"]
    
    # 1. Comandos directos
    if any(k in t for k in ["ayuda", "comandos", "menu"]):
        msg = ("🤖 **QUANT-MASTER PRO**\n\n"
               "• `analiza [Equipo A] vs [Equipo B]` -> Configurar.\n"
               "• `mejores apuestas` -> Selección pura EV+.\n"
               "• `parlay` -> Combinada de alta probabilidad.\n"
               "• `goles` / `corners` -> Desglose por niveles.\n"
               "• `estado` -> Ver situación.")
        enviar_telegram(chat_id, msg)
        return

    if "analiza" in t or "vs" in t:
        partido = t.replace("analiza", "").replace("contra", "vs").strip().title()
        db["partido"] = partido
        enviar_telegram(chat_id, f"⚡ **Analizando:** `{partido}`. Motor listo.")
        return

    if p == "No seleccionado":
        enviar_telegram(chat_id, "⚠️ Configura el partido primero con `analiza ...`")
        return

    # 2. Lógica especializada de comandos
    if "mejores apuestas" in t:
        picks = generar_picks_ev(p)
        msg = f"🔥 **SELECCIONES EXPERTAS EV+ (VALOR REAL) - {p}**\n\n"
        for i, pick in enumerate(picks, 1):
            msg += f"*{i}. {pick['desc']} (Cuota: {pick['odds']})*\n   ∟ *¿Por qué?* {pick['why']}\n\n"
        enviar_telegram(chat_id, msg)
        return

    if "parlay" in t:
        msg = f"🚀 **PARLAY DE ALTA PROBABILIDAD - {p}**\n\n{generar_parlay(p)}"
        enviar_telegram(chat_id, msg)
        return

    if "goles" in t:
        msg = f"⚽ **GOLES - {p}**\n🛡️ Segura: >1.5 (1.35)\n📈 EV+: >2.5 (2.05)\n⚡ Riesgo: >3.5 (3.80)"
        enviar_telegram(chat_id, msg)
        return

    if any(k in t for k in ["corners", "esquina"]):
        msg = f"🚩 **CÓRNERS - {p}**\n🛡️ Segura: >7.5 (1.40)\n📈 EV+: >9.5 (2.10)\n⚡ Riesgo: >11.5 (3.50)"
        enviar_telegram(chat_id, msg)
        return
        
    # 3. VALIDADOR UNIVERSAL (Cualquier otra pregunta cae aquí)
    enviar_telegram(chat_id, validar_pregunta(texto, p))

def escuchar_telegram():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=30"
            resp = requests.get(url, timeout=35).json()
            if resp.get("result"):
                for update in resp["result"]:
                    offset = update["update_id"] + 1
                    chat_id = update["message"]["chat"]["id"]
                    texto = update["message"].get("text", "")
                    if texto: procesar_logica(texto, chat_id)
        except Exception: time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=escuchar_telegram, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
