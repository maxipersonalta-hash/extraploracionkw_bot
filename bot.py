import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración básica de logs para ver errores en consola
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def procesar_metodo_fraude(t1_str: str, t2_str: str) -> str:
    """Aplica la lógica del método paso a paso y devuelve un reporte en Markdown."""
    
    # Limpiar espacios o caracteres extra
    t1_clean = re.sub(r'\D', '', t1_str)
    t2_clean = re.sub(r'\D', '', t2_str)

    if len(t1_clean) != 16 or len(t2_clean) != 16:
        return "❌ **Error:** Ambos números deben tener exactamente **16 dígitos**."

    # Paso 1: Grupos de 8
    g1_t1, g2_t1 = t1_clean[:8], t1_clean[8:]
    g1_t2, g2_t2 = t2_clean[:8], t2_clean[8:]

    # Paso 2 y 3: Multiplicación posición por posición de T2
    multiplicaciones_detalle = []
    resultados_mult = []

    for d1, d2 in zip(g1_t2, g2_t2):
        n1, n2 = int(d1), int(d2)
        res = n1 * n2
        multiplicaciones_detalle.append(f"• `{n1} × {n2} = {res}`")
        resultados_mult.append(str(res))

    # Paso 4: Unir y recortar a 8 dígitos
    cadena_unida = "".join(resultados_mult)
    g2_r1 = cadena_unida[:8]
    r1_full = g1_t1 + g2_r1

    # Paso 5: Comparación entre T1 y R1
    mascara = []
    for d1, d2 in zip(t1_clean, r1_full):
        if d1 == d2:
            mascara.append(d1)
        else:
            mascara.append("x")

    mascara_parcial = "".join(mascara)

    # Paso 6: Regla del último dígito
    mascara_final_list = list(mascara_parcial)
    regla_aplicada = False
    if mascara_final_list[-1] == 'x':
        mascara_final_list[-1] = '1'
        regla_aplicada = True

    mascara_final = "".join(mascara_final_list)

    # Construcción de la respuesta visual e intuitiva
    mult_str = "\n".join(multiplicaciones_detalle)
    
    reporte = f"""
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
    return reporte

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "👋 **¡Hola! Bienvenido al Bot de Prevención de Fraude.**\n\n"
        "Envíame dos números de 16 dígitos separados por una coma, un salto de línea o un espacio.\n\n"
        "**Ejemplo de uso:**\n"
        "`4345591312446812, 4345591312472677`"
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")

# Manejador de mensajes de texto
async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    # Buscar secuencias de 16 dígitos en el mensaje
    numeros = re.findall(r'\b\d{16}\b', texto)

    if len(numeros) < 2:
        await update.message.reply_text(
            "⚠️ Por favor, ingresa **dos números válidos de 16 dígitos**.\n\n"
            "Ejemplo:\n`4345591312446812 4345591312472677`",
            parse_mode="Markdown"
        )
        return

    # Procesar los primeros 2 números encontrados
    t1, t2 = numeros[0], numeros[1]
    respuesta = procesar_metodo_fraude(t1, t2)
    
    await update.message.reply_text(respuesta, parse_mode="Markdown")

if __name__ == '__main__':
    # Sustituye 'TU_TOKEN_AQUI' por el token otorgado por @BotFather en Telegram
    TOKEN = "8625756667:AAGPvsGM-_FywOhmk6i_NIgvVE8K7LCzFlw"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensaje))

    print("🤖 Bot en ejecución...")
    app.run_polling()
