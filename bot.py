import os
import re
import logging
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

# Servidor web dummy para mantener vivo el servicio gratuito de Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot activo")
    
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Métodos de extrapolación
def metodo_basico_activacion(numero: str) -> str:
    """Método básico de activación - reemplaza últimos 6 dígitos con x"""
    num_clean = re.sub(r'\D', '', numero)
    if len(num_clean) != 16:
        return None
    return num_clean[:10] + "xxxxxx"

def metodo_basico_similitud(t1: str, t2: str) -> str:
    """Método básico de similitud - compara dos números de 16 dígitos"""
    t1_clean = re.sub(r'\D', '', t1)
    t2_clean = re.sub(r'\D', '', t2)
    
    if len(t1_clean) != 16 or len(t2_clean) != 16:
        return None
    
    prefijo1 = t1_clean[:6]
    sufijo1 = t1_clean[6:]
    sufijo2 = t2_clean[6:]
    
    resultado = []
    for d1, d2 in zip(sufijo1, sufijo2):
        resultado.append(d1 if d1 == d2 else 'x')
    
    return prefijo1 + ''.join(resultado)

def metodo_avanzado_b10sum(t1: str, t2: str) -> str:
    """Método avanzado b10*sum"""
    t1_clean = re.sub(r'\D', '', t1)
    t2_clean = re.sub(r'\D', '', t2)
    
    if len(t1_clean) != 16 or len(t2_clean) != 16:
        return None
    
    d1_t1 = int(t1_clean[9])
    d2_t1 = int(t1_clean[10])
    d1_t2 = int(t2_clean[9])
    d2_t2 = int(t2_clean[10])
    
    suma1 = d1_t1 + d1_t2
    suma2 = d2_t1 + d2_t2
    
    div1 = suma1 / 2
    div2 = suma2 / 2
    
    mult1 = div1 * 5
    mult2 = div2 * 5
    
    mult1 = int(mult1) if mult1 % 1 == 0 else int(mult1)
    mult2 = int(mult2) if mult2 % 1 == 0 else int(mult2)
    
    total = mult1 + mult2
    
    resultado = t1_clean[:10] + str(total).zfill(2) + "xxxx"
    return resultado

def metodo_indentacion_logica(numero: str) -> str:
    """Método de indentación lógica"""
    num_clean = re.sub(r'\D', '', numero)
    if len(num_clean) != 16:
        return None
    
    prefijo = num_clean[:6]
    sufijo = num_clean[6:]
    
    grupo1 = sufijo[:3]
    grupo2 = sufijo[3:7]
    grupo3 = sufijo[7:]
    
    grupo1_mod = grupo1[0] + 'x' + grupo1[2]
    grupo2_mod = grupo2[0] + 'xx' + grupo2[3]
    grupo3_mod = grupo3[0] + 'x' + grupo3[2]
    
    return prefijo + grupo1_mod + grupo2_mod + grupo3_mod

def metodo_materialdinverter(t1: str, t2: str) -> str:
    """Método MaterialDInVerter - el más complejo"""
    t1_clean = re.sub(r'\D', '', t1)
    t2_clean = re.sub(r'\D', '', t2)
    
    if len(t1_clean) != 16 or len(t2_clean) != 16:
        return None
    
    g1_t1, g2_t1 = t1_clean[:8], t1_clean[8:]
    g1_t2, g2_t2 = t2_clean[:8], t2_clean[8:]
    
    multiplicaciones = []
    for d1, d2 in zip(g1_t2, g2_t2):
        multiplicaciones.append(str(int(d1) * int(d2)))
    
    cadena_unida = ''.join(multiplicaciones)
    g2_r1 = cadena_unida[:8]
    r1_full = g1_t1 + g2_r1
    
    mascara = []
    for d1, d2 in zip(t1_clean, r1_full):
        mascara.append(d1 if d1 == d2 else 'x')
    
    mascara_final = ''.join(mascara)
    
    if mascara_final[-1] == 'x':
        mascara_final = mascara_final[:-1] + '1'
    
    return mascara_final

# Manejo de estados de conversación
USER_STATE = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de inicio elegante"""
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Usuario"
    
    USER_STATE[user_id] = {'method': None, 'step': 0, 'num1': None, 'num2': None}
    
    # Obtener hora actual
    now = datetime.now()
    hora_actual = now.strftime("%I:%M %p").lower()
    
    welcome_text = f"""
🌟 *Bienvenido a ExtraploradorKW* 🌟

━━━━━━━━━━━━━━━━━━━
👤 *Usuario:* {username}
🆔 *ID:* `{user_id}`
📊 *Plan:* Free User
💳 *Créditos:* 0
━━━━━━━━━━━━━━━━━━━

📌 *Comandos Rápidos:*
• /cmds - Ver comandos

⏰ {hora_actual}
━━━━━━━━━━━━━━━━━━━

🔐 *Selecciona una opción para comenzar:*
"""

    keyboard = [
        [InlineKeyboardButton("🚪 Gateways", callback_data="gateways")],
        [InlineKeyboardButton("📊 Estado", callback_data="estado")],
        [InlineKeyboardButton("ℹ️ Ayuda", callback_data="ayuda")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los botones del menú principal"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Usuario"
    
    if query.data == "gateways":
        keyboard = [
            [InlineKeyboardButton("📌 Activación", callback_data="basico_activacion")],
            [InlineKeyboardButton("📌 Similitud", callback_data="basico_similitud")],
            [InlineKeyboardButton("⚡ Avanzada (b10*sum)", callback_data="avanzado_b10sum")],
            [InlineKeyboardButton("🧠 Indentación Lógica", callback_data="indentacion_logica")],
            [InlineKeyboardButton("🔬 MaterialDInVerter", callback_data="materialdinverter")],
            [InlineKeyboardButton("🔙 Volver", callback_data="volver")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔐 *Métodos de Extrapolación*\n━━━━━━━━━━━━━━\nSelecciona un método para comenzar:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif query.data == "estado":
        await query.edit_message_text(
            f"""
📊 *Tu Estado*
━━━━━━━━━━━━━━
👤 *Usuario:* {username}
🆔 *ID:* `{user_id}`
📊 *Plan:* Free User
💳 *Créditos:* 0
📈 *Consultas:* 0

🔄 *Estado:* Activo
━━━━━━━━━━━━━━
""",
            parse_mode="Markdown"
        )
        # Crear botón para volver
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="volver")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    
    elif query.data == "ayuda":
        await query.edit_message_text(
            f"""
ℹ️ *Ayuda - ExtraploradorKW*
━━━━━━━━━━━━━━━━━━━

🎯 *¿Qué es ExtraploradorKW?*
Es una herramienta de extrapolación de números que utiliza diversos métodos matemáticos para generar patrones.

📌 *Métodos Disponibles:*

1️⃣ *Activación* - Reemplaza últimos 6 dígitos
2️⃣ *Similitud* - Compara dos números de 16 dígitos
3️⃣ *Avanzada b10*sum* - Operaciones matemáticas
4️⃣ *Indentación Lógica* - Reorganización en grupos
5️⃣ *MaterialDInVerter* - Método más complejo

💡 *Cómo usar:*
1. Selecciona un método
2. Ingresa los números solicitados
3. Obtén el resultado

🔐 *Seguridad:* Todos los datos son procesados localmente
━━━━━━━━━━━━━━━━━━━
""",
            parse_mode="Markdown"
        )
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="volver")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    
    elif query.data == "volver":
        keyboard = [
            [InlineKeyboardButton("🚪 Gateways", callback_data="gateways")],
            [InlineKeyboardButton("📊 Estado", callback_data="estado")],
            [InlineKeyboardButton("ℹ️ Ayuda", callback_data="ayuda")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🏠 *Menú Principal*\n━━━━━━━━━━━━━━\nSelecciona una opción:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif query.data in ["basico_activacion", "basico_similitud", "avanzado_b10sum", "indentacion_logica", "materialdinverter"]:
        USER_STATE[user_id]['method'] = query.data
        USER_STATE[user_id]['step'] = 1
        USER_STATE[user_id]['num1'] = None
        USER_STATE[user_id]['num2'] = None
        
        method_names = {
            "basico_activacion": "Activación",
            "basico_similitud": "Similitud",
            "avanzado_b10sum": "b10*sum",
            "indentacion_logica": "Indentación Lógica",
            "materialdinverter": "MaterialDInVerter"
        }
        
        method_name = method_names.get(query.data, query.data)
        
        if query.data in ["basico_activacion", "indentacion_logica"]:
            await query.edit_message_text(
                f"""
📌 *Método: {method_name}*
━━━━━━━━━━━━━━━━━━━

📝 *Instrucciones:*
Ingresa un número de *16 dígitos*.

📌 *Ejemplo:*
`4915110176928790`

⏳ Esperando tu número...
━━━━━━━━━━━━━━━━━━━
""",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"""
📌 *Método: {method_name}*
━━━━━━━━━━━━━━━━━━━

📝 *Instrucciones:*
Ingresa el *PRIMER* número de 16 dígitos.

📌 *Ejemplo:*
`4915110176928790`

⏳ Esperando tu primer número...
━━━━━━━━━━━━━━━━━━━
""",
                parse_mode="Markdown"
            )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes de texto"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Si el usuario no tiene estado o no está en medio de un proceso, ignorar silenciosamente
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {'method': None, 'step': 0, 'num1': None, 'num2': None}
        # No responder, solo crear el estado
        return
    
    state = USER_STATE[user_id]
    
    # Si no hay método activo, ignorar silenciosamente
    if state['method'] is None:
        return
    
    # Limpiar el número
    numero_clean = re.sub(r'\D', '', text)
    
    # Verificar si es un número válido
    if len(numero_clean) != 16:
        await update.message.reply_text(
            "⚠️ *Error:* Debes ingresar exactamente 16 dígitos.\n\n📌 *Ejemplo:* `4915110176928790`",
            parse_mode="Markdown"
        )
        return
    
    if state['step'] == 1:
        state['num1'] = numero_clean
        state['step'] = 2
        
        if state['method'] in ["basico_activacion", "indentacion_logica"]:
            # Métodos que solo necesitan 1 número
            resultado = procesar_metodo_unico(state['method'], state['num1'])
            if resultado:
                await update.message.reply_text(resultado, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Error en el procesamiento. Por favor, intenta de nuevo.")
            state['method'] = None
            state['step'] = 0
            state['num1'] = None
            state['num2'] = None
        else:
            await update.message.reply_text(
                "✅ *Primer número recibido*\n━━━━━━━━━━━━━━\nAhora, ingresa el *SEGUNDO* número de 16 dígitos:",
                parse_mode="Markdown"
            )
    
    elif state['step'] == 2:
        state['num2'] = numero_clean
        resultado = procesar_metodo_doble(state['method'], state['num1'], state['num2'])
        if resultado:
            await update.message.reply_text(resultado, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Error en el procesamiento. Por favor, intenta de nuevo.")
        state['method'] = None
        state['step'] = 0
        state['num1'] = None
        state['num2'] = None

def procesar_metodo_unico(method: str, num: str) -> str:
    """Procesa métodos que solo requieren un número"""
    if method == "basico_activacion":
        resultado = metodo_basico_activacion(num)
        if resultado:
            return f"""
📌 *Resultado - Activación*
━━━━━━━━━━━━━━━━━━━

📥 *Número Original:*
`{num}`

🔄 *Proceso:*
1️⃣ Tomar primeros 10 dígitos: `{num[:10]}`
2️⃣ Reemplazar últimos 6 dígitos con `x`

✨ *Resultado Final:*
`{resultado}`
━━━━━━━━━━━━━━━━━━━
"""
    elif method == "indentacion_logica":
        resultado = metodo_indentacion_logica(num)
        if resultado:
            prefijo = num[:6]
            sufijo = num[6:]
            grupo1 = sufijo[:3]
            grupo2 = sufijo[3:7]
            grupo3 = sufijo[7:]
            
            return f"""
🧠 *Resultado - Indentación Lógica*
━━━━━━━━━━━━━━━━━━━

📥 *Número Original:*
`{num}`

🔄 *Proceso:*
1️⃣ Separar primeros 6 dígitos: `{prefijo}`
2️⃣ Separar resto en grupos (3-4-3): `[{grupo1}] [{grupo2}] [{grupo3}]`
3️⃣ Reemplazar centro de cada grupo con `x`

✨ *Resultado Final:*
`{resultado}`
━━━━━━━━━━━━━━━━━━━
"""
    return None

def procesar_metodo_doble(method: str, num1: str, num2: str) -> str:
    """Procesa métodos que requieren dos números"""
    if method == "basico_similitud":
        resultado = metodo_basico_similitud(num1, num2)
        if resultado:
            return f"""
📌 *Resultado - Similitud*
━━━━━━━━━━━━━━━━━━━

📥 *Números de Entrada:*
• T1: `{num1}`
• T2: `{num2}`

🔄 *Proceso:*
1️⃣ Separar primeros 6 dígitos de cada número
2️⃣ Comparar los dígitos restantes
3️⃣ Mantener iguales, marcar diferencias con `x`

✨ *Resultado Final:*
`{resultado}`
━━━━━━━━━━━━━━━━━━━
"""
    
    elif method == "avanzado_b10sum":
        resultado = metodo_avanzado_b10sum(num1, num2)
        if resultado:
            d1_1 = int(num1[9])
            d2_1 = int(num1[10])
            d1_2 = int(num2[9])
            d2_2 = int(num2[10])
            
            suma1 = d1_1 + d1_2
            suma2 = d2_1 + d2_2
            div1 = suma1 / 2
            div2 = suma2 / 2
            mult1 = div1 * 5
            mult2 = div2 * 5
            
            return f"""
⚡ *Resultado - b10*sum*
━━━━━━━━━━━━━━━━━━━

📥 *Números de Entrada:*
• T1: `{num1}`
• T2: `{num2}`

🔄 *Proceso:*
1️⃣ Tomar dígitos centrales (posición 10-11)
   • T1: `{d1_1}{d2_1}`
   • T2: `{d1_2}{d2_2}`
2️⃣ Sumar: `{d1_1}+{d1_2}={suma1}`, `{d2_1}+{d2_2}={suma2}`
3️⃣ Dividir entre 2: `{div1:.1f}`, `{div2:.1f}`
4️⃣ Multiplicar por 5: `{mult1:.1f}`, `{mult2:.1f}`
5️⃣ Sumar resultados: `{int(mult1) + int(mult2)}`

✨ *Resultado Final:*
`{resultado}`
━━━━━━━━━━━━━━━━━━━
"""
    
    elif method == "materialdinverter":
        resultado = metodo_materialdinverter(num1, num2)
        if resultado:
            g1_t1, g2_t1 = num1[:8], num1[8:]
            g1_t2, g2_t2 = num2[:8], num2[8:]
            
            multiplicaciones = []
            for d1, d2 in zip(g1_t2, g2_t2):
                multiplicaciones.append(f"• `{d1} × {d2} = {int(d1)*int(d2)}`")
            
            return f"""
🔬 *Resultado - MaterialDInVerter*
━━━━━━━━━━━━━━━━━━━

📥 *Números de Entrada:*
• T1: `{num1}`
• T2: `{num2}`

🔄 *Proceso:*
1️⃣ Separar en grupos de 8 dígitos
   • T1: `{g1_t1}` | `{g2_t1}`
   • T2: `{g1_t2}` | `{g2_t2}`

2️⃣ Multiplicar dígito a dígito:
{chr(10).join(multiplicaciones)}

3️⃣ Concatenar resultados y tomar primeros 8 dígitos
4️⃣ Aplicar similitud con T1
5️⃣ Si último dígito es `x`, reemplazar por 1

✨ *Resultado Final:*
`{resultado}`
━━━━━━━━━━━━━━━━━━━
"""
    return None

async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /cmds - Solo muestra los comandos disponibles"""
    await update.message.reply_text("""
📋 *Comandos Disponibles*
━━━━━━━━━━━━━━━━━━━

/start - Iniciar el bot
/cmds - Mostrar este mensaje

🔐 *Métodos Disponibles:*
• Activación - Reemplaza últimos 6 dígitos
• Similitud - Compara dos números
• b10*sum - Operaciones matemáticas
• Indentación Lógica - Reorganización en grupos
• MaterialDInVerter - Método más complejo

💡 Usa /start para acceder al menú
━━━━━━━━━━━━━━━━━━━
""", parse_mode="Markdown")

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("Falta la variable BOT_TOKEN.")
    
    # Inicia servidor HTTP secundario
    Thread(target=run_web_server, daemon=True).start()
    
    # Inicia el bot de Telegram
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmds", cmds))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot ExtraploradorKW activo...")
    app.run_polling()
