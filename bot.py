import os
import re
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

# Servidor web dummy para mantener vivo el servicio gratuito de Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot activo")

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def procesar_metodo_fraude(t1_str: str, t2_str: str) -> str:
    t1_clean = re.sub(r'\D', '', t1_str)
    t2_clean = re.sub(r'\D', '', t2_str)

    if len(t1_clean) != 16 or len(t2_clean) != 16:
        return "❌ **Error:** Ambos números deben tener exactamente **16 dígitos**."

    g1_t1, g2_t1 = t1_clean[:8], t1_clean[8:]
    g1_t2, g2_t2 = t2_clean[:8], t2_clean[8:]

    multiplicaciones_detalle = []
    resultados_mult = []

    for d1, d2 in zip(g1_t2, g2_t2):
        n1, n2 = int(d1), int(d2)
        res = n1 * n2
        multiplicaciones_detalle.append(f"• `{n1} × {n2} = {res}`")
        resultados_mult.append(str(res))

    cadena_unida = "".join(resultados_mult)
    g2_r1 = cadena_unida[:8]
    r1_full = g1_t1 + g2_r1

    mascara = [d1 if d1 == d2 else "x" for d1, d2 in zip(t1_clean, r1_full)]
    mascara_parcial = "".join(mascara)
    mascara_final_list = list(mascara_parcial)
    regla_aplicada = False

    if mascara_final_list[-1] == 'x':
        mascara_final_list[-1] = '1'
        regla_aplicada = True

    mascara_final = "".join(mascara_final_list)
    mult_str = "\n".join(multiplicaciones_detalle)

    return f"""
🔒 **ANÁLISIS DE PREVENCIÓN DE FRAUDE**

**1️⃣ Números de Entrada:**
• **T1:** `{g1_t1}` `{g2_t1}`
• **T2:** `{g1_t2}` `{g2_t2}`

**2️⃣ Multiplicación Dígito a Dígito (T2):**
{mult_str}

**3️⃣ Cadena Resultante:**
• Cadena completa: `{cadena_unida}`
• Recorte a 8 dígitos: `{g2_r1}`
• **R1:** `{g1_t1}` `{g2_r1}`

**4️⃣ Comparación (T1 vs R1):**
• **T1:** `{t1_clean}`
• **R1:** `{r1_full}`
• **Máscara:** `{mascara_parcial}`

{"⚠️ *El último dígito era 'x', por lo que se reemplazó por '1'.*" if regla_aplicada else ""}

✨ **Resultado Final:**
`{mascara_final}`
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 **¡Hola! Bot de Prevención de Fraude.**\n\nEnvíame 2 números de 16 dígitos.", parse_mode="Markdown")

async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    numeros = re.findall(r'\b\d{16}\b', update.message.text)
    if len(numeros) < 2:
        await update.message.reply_text("⚠️ Envía **dos números de 16 dígitos**.", parse_mode="Markdown")
        return
    await update.message.reply_text(procesar_metodo_fraude(numeros[0], numeros[1]), parse_mode="Markdown")

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("Falta la variable BOT_TOKEN.")
    
    # Inicia servidor HTTP secundario
    Thread(target=run_web_server, daemon=True).start()
    
    # Inicia el bot de Telegram
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensaje))
    print("🤖 Bot activo...")
    app.run_polling()
