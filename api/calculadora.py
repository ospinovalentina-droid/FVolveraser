from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from html import escape


# ACTIVIDADES Y COSTOS ORIGINALES
ACTIVIDADES = {
    "taller": {
        "nombre": "Taller comunitario de bienestar emocional",
        "costo": 500000
    },
    "jornada": {
        "nombre": "Jornada de bienestar en colegio",
        "costo": 850000
    },
    "circulo": {
        "nombre": "Círculo de apoyo para cuidadores",
        "costo": 300000
    },
    "biblioteca": {
        "nombre": "Kit impreso de la biblioteca digital",
        "costo": 200000
    },
}

WHATSAPP = "573002765220"
MAXIMO_PARTICIPANTES = 500


# CONVERTIR LOS DATOS DEL FORMULARIO A NÚMEROS
def convertir_a_numero(texto):
    limpio = (
        texto.replace("$", "")
        .replace(".", "")
        .replace(",", "")
        .replace(" ", "")
    )

    if limpio == "":
        return None

    if not limpio.isdigit():
        return None

    return int(limpio)


# MOSTRAR VALORES EN PESOS COLOMBIANOS
def formato_pesos(valor):
    return "$ " + f"{round(valor):,}".replace(",", ".")


# LÓGICA ORIGINAL DE LA CALCULADORA
def calcular(actividad, participantes, aporte, donacion):

    costo = ACTIVIDADES[actividad]["costo"]

    aporte_participantes = participantes * aporte

    total_disponible = aporte_participantes + donacion

    diferencia = total_disponible - costo

    porcentaje = (total_disponible / costo) * 100

    porcentaje_barra = min(porcentaje, 100)

    faltante_por_personas = max(costo - donacion, 0)

    # Redondear hacia arriba el aporte ideal por participante
    aporte_ideal = (
        faltante_por_personas + participantes - 1
    ) // participantes

    return {
        "nombre": ACTIVIDADES[actividad]["nombre"],
        "costo": costo,
        "aporte_participantes": aporte_participantes,
        "total_disponible": total_disponible,
        "diferencia": diferencia,
        "porcentaje": porcentaje,
        "porcentaje_barra": porcentaje_barra,
        "aporte_ideal": aporte_ideal
    }


# PLANTILLA GENERAL DE LAS PÁGINAS DE RESPUESTA
def pagina(titulo, contenido):

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>{escape(titulo)} | Fundación Volver a Ser</title>

        <link rel="stylesheet" href="/css/styles.css">

        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 30px 15px;
                background: #f5f7f6;
                color: #333;
            }}

            .respuesta-contenedor {{
                max-width: 700px;
                margin: 30px auto;
                padding: 30px;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 18px rgba(0,0,0,0.08);
            }}

            .respuesta-contenedor h1 {{
                color: #315c52;
                text-align: center;
            }}

            .respuesta-contenedor h2 {{
                color: #315c52;
            }}

            .dato {{
                display: flex;
                justify-content: space-between;
                gap: 15px;
                padding: 12px 0;
                border-bottom: 1px solid #eee;
            }}

            .total {{
                font-size: 1.3rem;
                font-weight: bold;
                color: #315c52;
            }}

            .mensaje {{
                margin: 20px 0;
                padding: 18px;
                background: #eef6f2;
                border-radius: 10px;
                line-height: 1.6;
            }}

            .barra-fondo {{
                width: 100%;
                height: 18px;
                background: #e5e5e5;
                border-radius: 20px;
                overflow: hidden;
                margin: 12px 0;
            }}

            .barra-progreso {{
                height: 100%;
                background: #6ba58d;
                border-radius: 20px;
            }}

            .botones {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 12px;
                margin-top: 25px;
            }}

            .botones a {{
                display: inline-block;
                padding: 13px 20px;
                border-radius: 8px;
                text-decoration: none;
                background: #315c52;
                color: white;
                text-align: center;
            }}

            .botones a:hover {{
                opacity: 0.9;
            }}

            .errores {{
                background: #fff0f0;
                padding: 15px 20px;
                border-radius: 10px;
                color: #9b3030;
                line-height: 1.7;
            }}
        </style>
    </head>

    <body>
        <main class="respuesta-contenedor">
            {contenido}
        </main>
    </body>
    </html>
    """


# MOSTRAR EL RESULTADO DEL CÁLCULO
def pagina_resultado(r):

    if r["diferencia"] >= 0:
        mensaje = (
            "¡La actividad cuenta con los recursos necesarios! "
            "El dinero restante podrá destinarse a apoyar otras actividades."
        )
    else:
        mensaje = (
            "Aún faltan recursos para cubrir el costo de esta actividad. "
            "Puedes revisar el aporte ideal por participante para alcanzar "
            "el valor necesario."
        )

    contenido = f"""
        <h1>Resumen del aporte</h1>

        <h2>{escape(r["nombre"])}</h2>

        <div class="mensaje">
            {mensaje}
        </div>

        <div class="dato">
            <span>Costo de la actividad</span>
            <strong>{formato_pesos(r["costo"])}</strong>
        </div>

        <div class="dato">
            <span>Aportes de los participantes</span>
            <strong>{formato_pesos(r["aporte_participantes"])}</strong>
        </div>

        <div class="dato">
            <span>Donaciones recibidas</span>
            <strong>{formato_pesos(
                r["total_disponible"] - r["aporte_participantes"]
            )}</strong>
        </div>

        <div class="dato total">
            <span>Total disponible</span>
            <strong>{formato_pesos(r["total_disponible"])}</strong>
        </div>

        <h2>Avance de financiación</h2>

        <div class="barra-fondo">
            <div class="barra-progreso"
                 style="width: {r["porcentaje_barra"]}%;">
            </div>
        </div>

        <p>
            <strong>{r["porcentaje"]:.1f}%</strong>
            del costo de la actividad está cubierto.
        </p>

        <div class="dato">
            <span>
                {"Dinero restante" if r["diferencia"] < 0 else "Dinero sobrante"}
            </span>
            <strong>{formato_pesos(abs(r["diferencia"]))}</strong>
        </div>

        <div class="mensaje">
            <h2>Aporte ideal por participante</h2>

            <p>
                Para cubrir el costo de la actividad, considerando las
                donaciones recibidas, cada participante debería aportar:
            </p>

            <p class="total">
                {formato_pesos(r["aporte_ideal"])}
            </p>
        </div>

        <div class="botones">
            <a href="/#calculadora">Volver a la calculadora</a>

            <a href="https://wa.me/{WHATSAPP}" target="_blank">
                Contactar por WhatsApp
            </a>
        </div>
    """

    return pagina("Resultado de la calculadora", contenido)


# MOSTRAR ERRORES DE VALIDACIÓN
def pagina_error(errores):

    lista_errores = "".join(
        f"<li>{escape(error)}</li>"
        for error in errores
    )

    contenido = f"""
        <h1>No se pudo realizar el cálculo</h1>

        <p>Por favor, revisa los siguientes datos:</p>

        <ul class="errores">
            {lista_errores}
        </ul>

        <div class="botones">
            <a href="/#calculadora">Volver a intentarlo</a>
        </div>
    """

    return pagina("Revisar datos", contenido)


# FUNCIÓN PRINCIPAL PARA VERCEL
class handler(BaseHTTPRequestHandler):

    def responder(self, contenido, estado=200):

        html = contenido.encode("utf-8")

        self.send_response(estado)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()

        self.wfile.write(html)

    def do_GET(self):

        self.send_response(303)
        self.send_header("Location", "/#calculadora")
        self.end_headers()

    def do_POST(self):

        try:
            longitud = int(self.headers.get("Content-Length", 0))

            cuerpo = self.rfile.read(longitud).decode("utf-8")

            formulario = parse_qs(
                cuerpo,
                keep_blank_values=True
            )

            actividad = formulario.get("actividad", [""])[0]

            participantes_texto = formulario.get(
                "participantes", [""]
            )[0]

            aporte_texto = formulario.get("aporte", [""])[0]

            donacion_texto = formulario.get("donacion", ["0"])[0]

            participantes = convertir_a_numero(participantes_texto)
            aporte = convertir_a_numero(aporte_texto)
            donacion = convertir_a_numero(donacion_texto)

            errores = []

            # VALIDAR ACTIVIDAD
            if actividad not in ACTIVIDADES:
                errores.append("Selecciona una actividad válida.")

            # VALIDAR PARTICIPANTES
            if participantes is None:
                errores.append("Ingresa el número de participantes.")
            elif participantes < 1:
                errores.append("Debe haber al menos un participante.")
            elif participantes > MAXIMO_PARTICIPANTES:
                errores.append(
                    f"El máximo permitido es de {MAXIMO_PARTICIPANTES} participantes."
                )

            # VALIDAR APORTE
            if aporte is None:
                errores.append("Ingresa el aporte por participante.")

            # VALIDAR DONACIÓN
            if donacion is None:
                errores.append(
                    "La donación debe ser un número válido. "
                    "Si no hay donaciones, ingresa 0."
                )

            if errores:
                self.responder(pagina_error(errores), 400)
                return

            # REALIZAR EL CÁLCULO
            resultado = calcular(
                actividad,
                participantes,
                aporte,
                donacion
            )

            self.responder(pagina_resultado(resultado))

        except Exception:
            self.responder(
                pagina_error([
                    "Ocurrió un inconveniente al procesar los datos. "
                    "Verifica la información e inténtalo nuevamente."
                ]),
                500
            )
