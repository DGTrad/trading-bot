from flask import Flask, request, jsonify
import MetaTrader5 as mt5
import telegram
import asyncio

app = Flask(__name__)

# Configuración
TELEGRAM_TOKEN = "8507091778:AAHIkQ7BVC6k7qXhUiLwnnv_xEPkVh-bodQ"
CHAT_ID = "1921096364"
LOTE = 0.01

def enviar_telegram(mensaje):
    async def _enviar():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=mensaje)
    asyncio.run(_enviar())

def ejecutar_orden(simbolo, direccion):
    if not mt5.initialize():
        return "Error al conectar MT5"
    
    tipo = mt5.ORDER_TYPE_BUY if direccion == "buy" else mt5.ORDER_TYPE_SELL
    precio = mt5.symbol_info_tick(simbolo).ask if direccion == "buy" else mt5.symbol_info_tick(simbolo).bid
    
    orden = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": simbolo,
        "volume": LOTE,
        "type": tipo,
        "price": precio,
        "deviation": 20,
        "magic": 123456,
        "comment": "TradingView Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    resultado = mt5.order_send(orden)
    mt5.shutdown()
    return resultado

@app.route('/webhook', methods=['POST'])
def webhook():
    datos = request.json
    simbolo = datos.get('symbol')
    direccion = datos.get('direction')
    
    resultado = ejecutar_orden(simbolo, direccion)
    
    mensaje = f"✅ Orden ejecutada\nSímbolo: {simbolo}\nDirección: {direccion}\nResultado: {resultado}"
    enviar_telegram(mensaje)
    
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=5000)