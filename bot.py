import os
import re
import logging
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

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Métodos de extrapolación
def metodo_basico_activacion(numero: str) -> str:
    """Método básico de activación - reemplaza últimos 6 dígitos con X"""
    num_clean = re.sub(r'\D', '', numero)
    if len(num_clean) != 16:
        return None
    return num_clean[:10] + "XXXXXX"

def metodo_basico_similitud(t1: str, t2: str) -> str:
    """Método básico de similitud - compara dos números de 16 dígitos"""
    t1_clean = re.sub(r'\D', '', t1)
    t2_clean = re.sub(r'\D', '', t2)
    
    if len(t1_clean) != 16 or len(t2_clean) != 16:
        return None
    
    # Separar primeros 6 dígitos
    prefijo1 = t1_clean[:6]
    prefijo2 = t2_clean[:6]
    sufijo1 = t1_clean[6:]
    sufijo2 = t2_clean[6:]
    
    # Comparar sufijos
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
    
    # Tomar los dígitos de la mitad (posición 10 y 11, índice 9 y 10)
    d1_t1 = int(t1_clean[9])
    d2_t1 = int(t1_clean[10])
    d1_t2 = int(t2_clean[9])
    d2_t2 = int(t2_clean[10])
    
    # Sumar
    suma1 = d1_t1 + d1_t2
    suma2 = d2_t1 + d2_t2
    
    # Dividir entre 2
    div1 = suma1 / 2
    div2 = suma2 / 2
    
    # Multiplicar por 5
    mult1 = div1 * 5
    mult2 = div2 * 5
    
    # Si tiene decimal, eliminar y redondear
    if mult1 % 1 != 0:
        mult1 = int(mult1)
    else:
        mult1 = int(mult1)
    
    if mult2 % 1 != 0:
        mult2 = int(mult2)
    else:
        mult2 = int(mult2)
    
    # Sumar resultados
    total = mult1 + mult2
    
    # Construir resultado
    resultado = t1_clean[:10] + str(total).zfill(2) + "XXXX"
    return resultado

def metodo_indentacion_logica(numero: str) -> str:
    """Método de indentación lógica"""
    num_clean = re.sub(r'\D', '', numero)
    if len(num_clean) != 16:
        return None
    
    prefijo = num_clean[:6]
    sufijo = num_clean[6:]
    
    # Separar en 3-4-3
    grupo1 = sufijo[:3]
    grupo2 = sufijo[3:7]
    grupo3 = sufijo[7:]
    
    # Reemplazar el centro de cada grupo con X
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
    
    # Separar en grupos de 8
    g1_t1, g2_t1 = t1_clean[:8], t1_clean[8:]
    g1_t2, g2_t2 = t2_clean[:8], t2_clean[8:]
    
    # Multiplicar dígito a dígito
    multiplicaciones = []
    for d1, d2 in zip(g1_t2, g2_t2):
        multiplicaciones.append(str(int(d1) * int(d2)))
    
    cadena_unida = ''.join(multiplicaciones)
    g2_r1 = cadena_unida[:8]  # Tomar primeros 8 dígitos
    r1_full = g1_t1 + g2_r1
    
    # Aplicar similitud
    mascara = []
    for d1, d2 in zip(t1_clean, r1_full):
        mascara.append(d1 if d1 == d2 else 'x')
    
    mascara_final = ''.join(mascara)
    
    # Si el último dígito es X, reemplazar por 1
    if mascara_final[-1] == 'x':
        mascara_final = mascara_final[:-1] + '1'
    
    return mascara_final

# Manejo de estados de conversación
USER_STATE = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de inicio con la interfaz de la imagen"""
    user_id = update.effective_user.id
    USER_STATE[user_id] = {'method': None, 'step': 0, 'num1': None, 'num2': None}
    
    welcome_text = """
*Bienvenido a AkiBotChk!*

- **Tu Información:**
  - Username: - 8755749385
  - Plan: Free User
  - Créditos: 0

- **Panel de Comandos:**
  - Comandos: /cmds
  - Precios: /buy

10:57 p.
"""

    keyboard = [
        [InlineKeyboardButton("🚪 Gateways", callback_data="gateways")],
        [InlineKeyboardButton("👥 Group", callback_data="group")],
        [InlineKeyboardButton("🔧 Tools", callback_data="tools")],
        [InlineKeyboardButton("📊 Referencias", callback_data="referencias")],
        [InlineKeyboardButton("💰 Precios", callback_data="precios")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los botones del menú principal"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "gateways":
        keyboard = [
            [InlineKeyboardButton("📌 Básica (Activación)", callback_data="basico_activacion")],
            [InlineKeyboardButton("📌 Básica (Similitud)", callback_data="basico_similitud")],
            [InlineKeyboardButton("⚡ Avanzada (b10*sum)", callback_data="avanzado_b10sum")],
            [InlineKeyboardButton("🧠 Indentación Lógica", callback_data="indentacion_logica")],
            [InlineKeyboardButton("🔬 MaterialDInVerter", callback_data="materialdinverter")],
            [InlineKeyboardButton("🔙 Volver", callback_data="volver")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🔐 *Métodos de Extrapolación Ética*\n\nSelecciona un método:", parse_mode="Markdown", reply_markup=reply_markup)
    
    elif query.data == "volver":
        keyboard = [
            [InlineKeyboardButton("🚪 Gateways", callback_data="gateways")],
            [InlineKeyboardButton("👥 Group", callback_data="group")],
            [InlineKeyboardButton("🔧 Tools", callback_data="tools")],
            [InlineKeyboardButton("📊 Referencias", callback_data="referencias")],
            [InlineKeyboardButton("💰 Precios", callback_data="precios")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🏠 *Menú Principal*", parse_mode="Markdown", reply_markup=reply_markup)
    
    elif query.data in ["basico_activacion", "basico_similitud", "avanzado_b10sum", "indentacion_logica", "materialdinverter"]:
        USER_STATE[user_id]['method'] = query.data
        USER_STATE[user_id]['step'] = 1
        
        if query.data == "basico_activacion":
            await query.edit_message_text("📌 *Método Básico - Activación*\n\nEste método reemplaza los últimos 6 dígitos por X.\n\nPor favor, ingresa un número de 16 dígitos:", parse_mode="Markdown")
        elif query.data == "indentacion_logica":
            await query.edit_message_text("🧠 *Método de Indentación Lógica*\n\nEste método reorganiza los dígitos en grupos.\n\nPor favor, ingresa un número de 16 dígitos:", parse_mode="Markdown")
        else:
            await query.edit_message_text(f"📌 *Método seleccionado*\n\nPor favor, ingresa el PRIMER número de 16 dígitos:", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes de texto"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {'method': None, 'step': 0, 'num1': None, 'num2': None}
        await update.message.reply_text("Por favor, usa /start para comenzar.")
        return
    
    state = USER_STATE[user_id]
    
    # Limpiar el número (eliminar espacios, guiones, etc.)
    numero_clean = re.sub(r'\D', '', text)
    
    if state['method'] is None:
        await update.message.reply_text("Por favor, usa /start para comenzar.")
        return
    
    # Verificar si es un número válido
    if len(numero_clean) != 16:
        await update.message.reply_text("⚠️ *Error:* Debes ingresar exactamente 16 dígitos.\n\nEjemplo: `4915110176928790`", parse_mode="Markdown")
        return
    
    if state['step'] == 1:
        state['num1'] = numero_clean
        state['step'] = 2
        
        if state['method'] in ["basico_activacion", "indentacion_logica"]:
            # Métodos que solo necesitan 1 número
            resultado = procesar_metodo_unico(state['method'], state['num1'])
            await update.message.reply_text(resultado, parse_mode="Markdown")
            state['method'] = None
            state['step'] = 0
        else:
            await update.message.reply_text("✅ Primer número recibido.\n\nAhora, ingresa el SEGUNDO número de 16 dígitos:")
    
    elif state['step'] == 2:
        state['num2'] = numero_clean
        resultado = procesar_metodo_doble(state['method'], state['num1'], state['num2'])
        await update.message.reply_text(resultado, parse_mode="Markdown")
        state['method'] = None
        state['step'] = 0

def procesar_metodo_unico(method: str, num: str) -> str:
    """Procesa métodos que solo requieren un número"""
    if method == "basico_activacion":
        resultado = metodo_basico_activacion(num)
        if resultado:
            return f"""
🔐 *Método Básico - Activación*

**Número Original:**
`{num}`

**Pasos:**
1. Tomar los primeros 10 dígitos: `{num[:10]}`
2. Reemplazar los últimos 6 dígitos con X

✨ *Resultado:*
`{resultado}`
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
🧠 *Método de Indentación Lógica*

**Número Original:**
`{num}`

**Pasos:**
1. Separar primeros 6 dígitos: `{prefijo}`
2. Separar resto en grupos (3-4-3): `[{grupo1}] [{grupo2}] [{grupo3}]`
3. Reemplazar centro de cada grupo con X

✨ *Resultado:*
`{resultado}`
"""
    return "❌ Error en el procesamiento."

def procesar_metodo_doble(method: str, num1: str, num2: str) -> str:
    """Procesa métodos que requieren dos números"""
    if method == "basico_similitud":
        resultado = metodo_basico_similitud(num1, num2)
        if resultado:
            return f"""
🔐 *Método Básico - Similitud*

**Números de Entrada:**
• T1: `{num1}`
• T2: `{num2}`

**Pasos:**
1. Separar primeros 6 dígitos de cada número
2. Comparar los dígitos restantes
3. Mantener iguales, marcar diferencias con X

✨ *Resultado:*
`{resultado}`
"""
    
    elif method == "avanzado_b10sum":
        resultado = metodo_avanzado_b10sum(num1, num2)
        if resultado:
            # Extraer los dígitos centrales para mostrar
            d1_1 = int(num1[9])
            d2_1 = int(num1[10])
            d1_2 = int(num2[9])
            d2_2 = int(num2[10])
            
            return f"""
⚡ *Método Avanzado - b10*sum*

**Números de Entrada:**
• T1: `{num1}`
• T2: `{num2}`

**Pasos:**
1. Tomar dígitos centrales (posición 10-11)
   • T1: `{d1_1}{d2_1}`
   • T2: `{d1_2}{d2_2}`
2. Sumar: `{d1_1}+{d1_2}={d1_1+d1_2}`, `{d2_1}+{d2_2}={d2_1+d2_2}`
3. Dividir entre 2: `{(d1_1+d1_2)/2}`, `{(d2_1+d2_2)/2}`
4. Multiplicar por 5: `{((d1_1+d1_2)/2)*5}`, `{((d2_1+d2_2)/2)*5}`
5. Sumar resultados

✨ *Resultado:*
`{resultado}`
"""
    
    elif method == "materialdinverter":
        resultado = metodo_materialdinverter(num1, num2)
        if resultado:
            g1_t1, g2_t1 = num1[:8], num1[8:]
            g1_t2, g2_t2 = num2[:8], num2[8:]
            
            # Mostrar multiplicaciones
            multiplicaciones = []
            for d1, d2 in zip(g1_t2, g2_t2):
                multiplicaciones.append(f"`{d1} × {d2} = {int(d1)*int(d2)}`")
            
            return f"""
🔬 *Método MaterialDInVerter*

**Números de Entrada:**
• T1: `{num1}`
• T2: `{num2}`

**Pasos:**
1. Separar en grupos de 8 dígitos
   • T1: `{g1_t1}` | `{g2_t1}`
   • T2: `{g1_t2}` | `{g2_t2}`

2. Multiplicar dígito a dígito:
{chr(10).join(multiplicaciones)}

3. Concatenar resultados y tomar primeros 8 dígitos
4. Aplicar similitud con T1
5. Si último dígito es X, reemplazar por 1

✨ *Resultado:*
`{resultado}`
"""
    return "❌ Error en el procesamiento."

async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /cmds"""
    await update.message.reply_text("""
📋 *Comandos Disponibles:*

/start - Iniciar el bot
/cmds - Mostrar este mensaje
/buy - Información de precios

*Métodos de Extrapolación:*
• Básica (Activación) - Reemplaza últimos 6 dígitos
• Básica (Similitud) - Compara dos números
• Avanzada (b10*sum) - Usa operaciones matemáticas
• Indentación Lógica - Reorganiza dígitos
• MaterialDInVerter - Método más complejo

Usa /start para acceder al menú principal.
""", parse_mode="Markdown")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /buy"""
    await update.message.reply_text("""
💰 *Planes y Precios:*

🔹 *Free User* - $0
• Créditos: 0
• Métodos básicos disponibles

🔸 *Premium* - $19.99/mes
• Todos los métodos disponibles
• Sin límite de consultas
• Soporte prioritario

🔹 *Pro* - $49.99/mes
• Todo lo de Premium
• Acceso a herramientas avanzadas
• Asesoría personalizada

*Pago:*
Aceptamos tarjetas de crédito y criptomonedas.

Contacta a @soporte para más información.
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
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot activo...")
    app.run_polling()
