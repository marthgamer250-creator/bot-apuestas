import os
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot de Apuestas Cuantitativo Activo 24/7!"

API_KEY_ODDS = "6c5f290a655e478909dcd837da4943bd"
TELEGRAM_TOKEN = "8814947543:AAFtSv-SIvyla9vJYV7AGA4Y9jMLSR0YwNI"

def enviar_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def obtener_chat_id():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    resp = requests.get(url).json()
    if resp.get("result"):
        return resp["result"][0]["message"]["chat"]["id"]
    return None

def radar_automatico():
    while True:
        try:
            chat_id = obtener_chat_id()
            if chat_id:
                url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY_ODDS}&regions=us&markets=h2h"
                resp = requests.get(url)
                if resp.status_code == 200:
                    partidos = resp.json()
                    bankroll = 7.00
                    for partido in partidos:
                        home = partido['home_team']
                        away = partido['away_team']
                        for bookmaker in partido.get('bookmakers', []):
                            casa = bookmaker['title']
                            for market in bookmaker.get('markets', []):
                                if market['key'] == 'h2h':
                                    for outcome in market['outcomes']:
                                        cuota = outcome['price']
                                        equipo = outcome['name']
                                        
                                        prob_implicita = 1 / cuota
                                        prob_modelo = prob_implicita + 0.05
                                        ev = (prob_modelo * cuota) - 1
                                        
                                        if ev >= 0.035:
                                            stake_kelly = min(1.5, ((cuota - 1) * prob_modelo - (1 - prob_modelo)) / (cuota - 1) * 100 * 0.25)
                                            monto_apuesta = (bankroll * stake_kelly) / 100.0
                                            
                                            alerta = (
                                                f"🚨 **¡ALERTA DE VALOR / +EV!** 🚨\n\n"
                                                f"🏢 *Casa:* {casa}\n"
                                                f"⚽ *Partido:* {home} vs {away}\n"
                                                f"🎯 *Selección:* {equipo}\n"
                                                f"📈 *Cuota:* {cuota} | **EV:** +{ev*100:.2f}%\n"
                                                f"💰 *Stake Sugerido:* ${monto_apuesta:.2f} USD"
                                            )
                                            enviar_telegram(chat_id, alerta)
                                            time.sleep(1)
        except Exception as e:
            print(f"Error en el ciclo: {e}")
        time.sleep(3600) # Vuelve a escanear en 1 hora

if __name__ == "__main__":
    # Arranca el bot en segundo plano
    t = threading.Thread(target=radar_automatico)
    t.daemon = True
    t.start()
    
    # Inicia el servidor web para que Render cumpla con el plan gratuito
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
