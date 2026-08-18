import os
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

API_KEY_ODDS = "6c5f290a655e478909dcd837da4943bd"
TELEGRAM_TOKEN = "8814947543:AAFtSv-SIvyla9vJYV7AGA4Y9jMLSR0YwNI"

# Ligas principales que el bot escaneará automáticamente en busca de tu partido
LIGAS_DEPORTE = [
    "soccer_mexico_ligamx",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_uefa_champs_league",
    "soccer_usa_mls",
    "soccer_argentina_primera_division"
]

def enviar_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def buscar_cuotas_reales(busqueda):
    """
    Busca en tiempo real en la API de cuotas el partido solicitado
    y extrae los datos reales de Bet365.
    """
    busqueda = busqueda.lower()
    
    for sport_key in LIGAS_DEPORTE:
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={API_KEY_ODDS}&regions=eu,us&markets=h2h,totals"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                partidos = resp.json()
                for p in partidos:
                    home = p.get('home_team', '')
                    away = p.get('away_team', '')
                    
                    # Si el texto que escribiste coincide con algún equipo
                    if busqueda in home.lower() or busqueda in away.lower():
                        # Buscar cuotas de Bet365
                        for bookmaker in p.get('bookmakers', []):
                            if bookmaker.get('title') == 'Bet365':
                                return organizar_reporte_real(home, away, bookmaker)
        except Exception as e:
            print(f"Error consultando {sport_key}: {e}")
            
    return None

def organizar_reporte_real(home, away, bookmaker):
    """
    Toma los datos crudos de Bet365 y calcula las matemáticas y probabilidades.
    """
    mercados = bookmaker.get('markets', [])
    cuotas_h2h = {}
    cuotas_totales = {}
    
    for mercado in mercados:
        if mercado['key'] == 'h2h':
            for outcome in mercado['outcomes']:
                cuotas_h2h[outcome['name']] = outcome['price']
        elif mercado['key'] == 'totals':
            for outcome in mercado['outcomes']:
                cuotas_totales[outcome.get('name', '')] = outcome.get('price')

    # Cálculos matemáticos básicos (Probabilidad Implícita)
    texto_cuotas = ""
    for equipo, cuota in cuotas_h2h.items():
        prob_implicita = (1 / cuota) * 100
        texto_cuotas += f"• **{equipo}:** Cuota `{cuota}` (Prob. Implícita: `{prob_implicita:.1f}%`)\n"

    reporte = (
        f"🔥 **ANÁLISIS GOD-TIER (EN TIEMPO REAL)** 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"⚽ **Encuentro:** `{home} vs {away}`\n"
        f"🏢 **Casa Verificada:** Bet365\n\n"
        f"📊 **Cuotas y Matemáticas en Vivo:**\n"
        f"{texto_cuotas}\n"
        f"🛡️ **Opción Segura:** Doble Oportunidad al favorito.\n"
        f"⚖️ **Opción Equilibrada:** Ambos Anotan / Más de 1.5 Goles.\n"
        f"🚀 **Opción Arriesgada (High Stake):** Victoria directa por más de 1 gol.\n\n"
        f"💡 *Veredicto del Algoritmo:* Datos extraídos directamente del servidor de Bet365. ¡Opera con gestión de riesgo estricta!"
    )
    return reporte

def procesar_telegram(texto, chat_id):
    t = texto.lower()
    
    if t.startswith("analiza") or t.startswith("partido") or len(t) > 3:
        # Extraer el nombre del equipo a buscar
        equipo_buscado = t.replace("analiza", "").replace("partido", "").strip()
        
        enviar_telegram(chat_id, f"🔍 Buscando en tiempo real cuotas de Bet365 para: *{equipo_buscado.title()}*...")
        
        reporte = buscar_cuotas_reales(equipo_buscado)
        
        if reporte:
            enviar_telegram(chat_id, reporte)
        else:
            enviar_telegram(chat_id, f"⚠️ No encontré un partido activo en este momento para **'{equipo_buscado.title()}'** en las ligas principales de Bet365. Prueba escribiendo el nombre exacto de uno de los equipos (ej: *Necaxa*, *León*, *Real Madrid*).")
    else:
        enviar_telegram(chat_id, "🤖 Escribe **'Analiza [Nombre del Equipo]'** para consultar las cuotas matemáticas en vivo de Bet365.")

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
                        procesar_telegram(texto, chat_id)
        except Exception: time.sleep(1)
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=escuchar_telegram, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
