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

# Servidor web dummy
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
    num_clean = re.sub(r'\D', '', numero)
    if len(num_clean) != 16:
        return None
    return num_clean[:10] + "xxxxxx"

def metodo_basico_similitud(t1: str, t2: str) -> str:
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

USER_STATE = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Usuario"
    
    USER_STATE[user_id] = {'method': None, 'step': 0, 'num1': None, 'num2': None}
    
    now = datetime.now()
    hora_actual = now.strftime("%I:%M %p").lower()
    
    # Intentar enviar imagen
    try:
        with open('rico.png', 'rb') as photo:
            await update.message.reply_photo(photo, caption=f"""
🌟 *¡Bienvenido a ExtraploradorKW!* 🌟

━━━━━━━━━━━━━━━━━━━
👤 *{username}* · ID: `{user_id}`
📊 *Plan:* Free · 💳 *Créditos:* 0
━━━━━━━━━━━━━━━━━━━

⚡ *¿Qué deseas hacer hoy?*

Usa los botones de abajo o escribe /cmds para ver los comandos.

⏰ {hora_actual}
""", parse_mode="Markdown")
    except:
        # Si no encuentra la imagen, enviar solo texto
        await update.message.reply_text(f"""
🌟 *¡Bienvenido a ExtraploradorKW!* 🌟

━━━━━━━━━━━━━━━━━━━
👤 *{username}* · ID: `{user_id}`
📊 *Plan:* Free · 💳 *Créditos:* 0
━━━━━━━━━━━━━━━━━━━

⚡ *¿Qué deseas hacer hoy?*

Usa los botones de abajo o escribe /cmds para ver los comandos.

⏰ {hora_actual}
""", parse_mode="Markdown")
    
    keyboard = [
        [InlineKeyboardButton("🚪 Gateways", callback_data="gateways")],
        [InlineKeyboardButton("📊 Estado", callback_data="estado")],
        [InlineKeyboardButton("ℹ️ Ayuda", callback_data="ayuda")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🔽 *Selecciona una opción:*", parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Usuario"
    
    if query.data == "gateways":
        keyboard = [
            [InlineKeyboardButton("📌 Activación", callback_data="basico_activacion")],
            [InlineKeyboardButton("📌 Similitud", callback_data="basico_similitud")],
            [InlineKeyboardButton("⚡ b10*sum", callback_data="avanzado_b10sum")],
            [InlineKeyboardButton("🧠 Indentación", callback_data="indentacion_logica")],
            [InlineKeyboardButton("🔬 MaterialDInVerter", callback_data="materialdinverter")],
            [InlineKeyboardButton("🔙 Volver", callback_data="volver")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔐 *Métodos de Extrapolación*\n━━━━━━━━━━━━━━\nElige el que mejor se adapte a lo que buscas:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif query.data == "estado":
        await query.edit_message_text(
            f"""
📊 *Tu Estado Actual*
━━━━━━━━━━━━━━
👤 *Usuario:* {username}
🆔 *ID:* `{user_id}`
📊 *Plan:* Free User
💳 *Créditos:* 0
📈 *Consultas:* 0

✅ *Estado:* Activo y listo para usar
━━━━━━━━━━━━━━
""",
            parse_mode="Markdown"
        )
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="volver")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    
    elif query.data == "ayuda":
        await query.edit_message_text(
            f"""
ℹ️ *Ayuda Rápida*
━━━━━━━━━━━━━━━━━━━

🎯 *ExtraploradorKW* te ayuda a generar patrones numéricos usando diferentes métodos.

📌 *Métodos disponibles:*

1️⃣ *Activación* - Reemplaza los últimos 6 dígitos
2️⃣ *Similitud* - Compara dos números y marca diferencias
3️⃣ *b10*sum* - Usa operaciones matemáticas
4️⃣ *Indentación* - Reorganiza en grupos de 3-4-3
5️⃣ *MaterialDInVerter* - El más completo y complejo

💡 *Cómo usar:*
1. Elige un método
2. Ingresa los números que pide
3. Obtén tu resultado al instante

🔐 *Seguro y privado*
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
            "🏠 *Menú Principal*\n━━━━━━━━━━━━━━\n¿Qué quieres hacer ahora?",
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
            "indentacion_logica": "Indentación",
            "materialdinverter": "MaterialDInVerter"
        }
        
        method_name = method_names.get(query.data, query.data)
        
        if query.data in ["basico_activacion", "indentacion_logica"]:
            await query.edit_message_text(
                f"""
📌 *{method_name}*

✅ *Fácil y rápido.* Solo necesitas un número de 16 dígitos.

📝 *Ingresa tu número:*
`4915110176928790`

⏳ *Esperando...*
━━━━━━━━━━━━━━━━━━━
""",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"""
📌 *{method_name}*

✅ *Este método necesita 2 números.* Ingresa el primero.

📝 *Primer número:*
`4915110176928790`

⏳ *Esperando tu primer número...*
━━━━━━━━━━━━━━━━━━━
""",
                parse_mode="Markdown"
            )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Si el usuario escribe /cmds, mostrar el menú
    if text == '/cmds':
        keyboard = [
            [InlineKeyboardButton("🚪 Gateways", callback_data="gateways")],
            [InlineKeyboardButton("📊 Estado", callback_data="estado")],
            [InlineKeyboardButton("ℹ️ Ayuda", callback_data="ayuda")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📋 *Menú Principal*\n━━━━━━━━━━━━━━\nSelecciona una opción:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return
    
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {'method': None, 'step': 0, 'num1': None, 'num2': None}
        return
    
    state = USER_STATE[user_id]
    
    if state['method'] is None:
        return
    
    numero_clean = re.sub(r'\D', '', text)
    
    if len(numero_clean) != 16:
        await update.message.reply_text(
            "⚠️ *Error:* El número debe tener 16 dígitos.\n\n📌 *Ejemplo:* `4915110176928790`",
            parse_mode="Markdown"
        )
        return
    
    if state['step'] == 1:
        state['num1'] = numero_clean
        state['step'] = 2
        
        if state['method'] in ["basico_activacion", "indentacion_logica"]:
            resultado = procesar_metodo_unico(state['method'], state['num1'])
            if resultado:
                await update.message.reply_text(resultado, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Algo salió mal. Intenta de nuevo.")
            state['method'] = None
            state['step'] = 0
            state['num1'] = None
            state['num2'] = None
        else:
            await update.message.reply_text(
                "✅ *Primero listo.* Ahora el segundo número:",
                parse_mode="Markdown"
            )
    
    elif state['step'] == 2:
        state['num2'] = numero_clean
        resultado = procesar_metodo_doble(state['method'], state['num1'], state['num2'])
        if resultado:
            await update.message.reply_text(resultado, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Algo salió mal. Intenta de nuevo.")
        state['method'] = None
        state['step'] = 0
        state['num1'] = None
        state['num2'] = None

def procesar_metodo_unico(method: str, num: str) -> str:
    if method == "basico_activacion":
        resultado = metodo_basico_activacion(num)
        if resultado:
            return f"""
📌 *Activación - Resultado*

📥 *Número original:*
`{num}`

🔧 *Proceso:*
1️⃣ Tomé los primeros 10 dígitos: `{num[:10]}`
2️⃣ Los últimos 6 los cambié por `x`

✨ *Resultado:*
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
🧠 *Indentación Lógica - Resultado*

📥 *Número original:*
`{num}`

🔧 *Proceso:*
1️⃣ Separé los primeros 6: `{prefijo}`
2️⃣ El resto en grupos (3-4-3): `{grupo1} | {grupo2} | {grupo3}`
3️⃣ Puse `x` en el centro de cada grupo

✨ *Resultado:*
`{resultado}`
━━━━━━━━━━━━━━━━━━━
"""
    return None

def procesar_metodo_doble(method: str, num1: str, num2: str) -> str:
    if method == "basico_similitud":
        resultado = metodo_basico_similitud(num1, num2)
        if resultado:
            return f"""
📌 *Similitud - Resultado*

📥 *Números:*
• T1: `{num1}`
• T2: `{num2}`

🔧 *Proceso:*
1️⃣ Comparé los primeros 6 dígitos
2️⃣ Los que coinciden los dejé igual
3️⃣ Los que no, los marqué con `x`

✨ *Resultado:*
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
⚡ *b10*sum - Resultado*

📥 *Números:*
• T1: `{num1}`
• T2: `{num2}`

🔧 *Proceso matemático:*
• Dígitos centrales: `{d1_1}{d2_1}` y `{d1_2}{d2_2}`
• Suma: `{suma1}` y `{suma2}`
• /2: `{div1:.1f}` y `{div2:.1f}`
• *5: `{mult1:.1f}` y `{mult2:.1f}`
• Total: `{int(mult1) + int(mult2)}`

✨ *Resultado:*
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
🔬 *MaterialDInVerter - Resultado*

📥 *Números:*
• T1: `{num1}`
• T2: `{num2}`

🔧 *Proceso completo:*
1️⃣ Grupos de 8: `{g1_t1}|{g2_t1}` y `{g1_t2}|{g2_t2}`
2️⃣ Multiplicaciones:
{chr(10).join(multiplicaciones)}
3️⃣ Uní resultados y tomé los primeros 8
4️⃣ Comparé con T1
5️⃣ Si terminaba en `x`, lo cambié por 1

✨ *Resultado final:*
`{resultado}`
━━━━━━━━━━━━━━━━━━━
"""
    return None

async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /cmds - Muestra el menú principal"""
    keyboard = [
        [InlineKeyboardButton("🚪 Gateways", callback_data="gateways")],
        [InlineKeyboardButton("📊 Estado", callback_data="estado")],
        [InlineKeyboardButton("ℹ️ Ayuda", callback_data="ayuda")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📋 *Menú Principal*\n━━━━━━━━━━━━━━\nSelecciona una opción:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("Falta la variable BOT_TOKEN.")
    
    Thread(target=run_web_server, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmds", cmds))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 ExtraploradorKW activo...")
    app.run_polling()
