
# ============================================================
# GEOARCOS
# CALCULADORA GEODESICA
# INTERFAZ VISUAL - VERSION 1.0
# ============================================================

import streamlit as st
from io import BytesIO
from datetime import datetime

from elipsoides import ELIPSOIDES
from conversiones import (
    geograficas_a_utm,
    utm_a_geograficas,
    gms_a_decimal
)



# ============================================================
# GENERACION DEL REPORTE PDF
# ============================================================

def crear_reporte_pdf(resultado, tipo_conversion):
    """
    Genera un reporte de nivel intermedio: explicativo y tecnicamente verificable.
    Todos los resultados numericos proceden del modulo conversiones.py.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            KeepTogether, PageBreak
        )
    except ImportError as error:
        raise ImportError(
            "No esta instalada la biblioteca reportlab. "
            "Instalala en el entorno de Spyder con: "
            "python.exe -m pip install reportlab"
        ) from error

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1.55 * cm,
        leftMargin=1.55 * cm,
        topMargin=1.55 * cm,
        bottomMargin=1.55 * cm,
        title="Reporte de conversion geodesica - GEOARCOS",
        author="GEOARCOS"
    )

    azul = colors.HexColor("#17324F")
    azul_claro = colors.HexColor("#EAF2F8")
    gris = colors.HexColor("#5B6573")
    borde = colors.HexColor("#D7E0EA")

    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="GeoTitulo", parent=estilos["Title"],
        fontName="Helvetica-Bold", fontSize=20, leading=23,
        textColor=azul, alignment=TA_CENTER, spaceAfter=4
    ))
    estilos.add(ParagraphStyle(
        name="GeoSubtitulo", parent=estilos["Normal"],
        fontSize=8.5, leading=11, textColor=gris,
        alignment=TA_CENTER, spaceAfter=5
    ))
    estilos.add(ParagraphStyle(
        name="GeoSeccion", parent=estilos["Heading2"],
        fontSize=11.5, leading=14, textColor=azul,
        spaceBefore=9, spaceAfter=5, keepWithNext=True
    ))
    estilos.add(ParagraphStyle(
        name="GeoTexto", parent=estilos["BodyText"],
        fontSize=8.4, leading=11.3, textColor=colors.HexColor("#263445"),
        spaceAfter=4
    ))
    estilos.add(ParagraphStyle(
        name="GeoNota", parent=estilos["BodyText"],
        fontSize=7.3, leading=9.5, textColor=gris
    ))
    estilos.add(ParagraphStyle(
        name="GeoFormula", parent=estilos["Code"],
        fontName="Courier", fontSize=7.3, leading=9.2,
        textColor=azul, backColor=azul_claro,
        borderColor=borde, borderWidth=0.5, borderPadding=5,
        spaceBefore=2, spaceAfter=4
    ))

    elementos = []

    def agregar_tabla(titulo, filas, anchos=(6.5 * cm, 10.0 * cm)):
        elementos.append(Paragraph(titulo, estilos["GeoSeccion"]))
        datos = [["Parametro", "Valor"]] + [
            [str(nombre), str(valor)] for nombre, valor in filas
        ]
        tabla = Table(datos, colWidths=list(anchos), repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), azul),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.8),
            ("GRID", (0, 0), (-1, -1), 0.35, borde),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, azul_claro]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ]))
        elementos.append(tabla)

    def agregar_formula(texto):
        elementos.append(Paragraph(texto, estilos["GeoFormula"]))

    elementos.append(Paragraph("GEOARCOS", estilos["GeoTitulo"]))
    elementos.append(Paragraph(
        "REPORTE DE CONVERSION GEODESICA",
        estilos["GeoSubtitulo"]
    ))
    elementos.append(Paragraph(
        "Herramienta academica de calculo y transformacion de coordenadas",
        estilos["GeoSubtitulo"]
    ))
    elementos.append(Spacer(1, 5))

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    agregar_tabla("1. Identificacion del calculo", [
        ("Tipo de conversion", tipo_conversion),
        ("Elipsoide seleccionado", resultado.get("elipsoide", "No disponible")),
        ("Fecha de generacion", fecha),
    ])

    elementos.append(Paragraph(
        "2. Datos de entrada y resultados", estilos["GeoSeccion"]
    ))
    if tipo_conversion == "Geograficas a UTM":
        entrada = [
            ("Latitud", resultado.get("latitud_gms")),
            ("Latitud decimal", f'{resultado.get("latitud_decimal", 0):.10f} grados'),
            ("Longitud", resultado.get("longitud_gms", "").replace("W", "O")),
            ("Longitud decimal", f'{resultado.get("longitud_decimal", 0):.10f} grados'),
        ]
        salida = [
            ("Este UTM (X)", f'{resultado.get("este", 0):.4f} m'),
            ("Norte UTM (Y)", f'{resultado.get("norte", 0):.4f} m'),
        ]
    else:
        entrada = [
            ("Este UTM (X)", f'{resultado.get("este_entrada", 0):.4f} m'),
            ("Norte UTM (Y)", f'{resultado.get("norte_entrada", 0):.4f} m'),
        ]
        salida = [
            ("Latitud decimal", f'{resultado.get("latitud_decimal", 0):.10f} grados'),
            ("Longitud decimal", f'{resultado.get("longitud_decimal", 0):.10f} grados'),
            ("Latitud GMS", resultado.get("latitud_gms")),
            ("Longitud GMS", resultado.get("longitud_gms", "").replace("W", "O")),
        ]

    agregar_tabla("Coordenadas de entrada", entrada)
    agregar_tabla("Resultados obtenidos", salida)

    elementos.append(Paragraph(
        "3. Referencia geometrica y parametros geodesicos",
        estilos["GeoSeccion"]
    ))
    elementos.append(Paragraph(
        "El elipsoide define el modelo matematico aproximado de la forma de la "
        "Tierra mediante sus semiejes y excentricidades. La proyeccion UTM "
        "representa posiciones sobre una cuadrícula plana, organizada en zonas "
        "de seis grados de longitud. Por tanto, el elipsoide y la proyeccion "
        "son elementos distintos que se utilizan conjuntamente.",
        estilos["GeoTexto"]
    ))
    parametros = [
        ("Semieje mayor (a)", f'{resultado.get("a", 0):,.4f} m'),
        ("Semieje menor (b)", f'{resultado.get("b", 0):,.4f} m'),
        ("Primera excentricidad al cuadrado (e2)", f'{resultado.get("e2", 0):.12f}'),
        ("Segunda excentricidad al cuadrado (e_prime2)", f'{resultado.get("e_prime2", 0):.12f}'),
        ("Zona UTM", resultado.get("zona")),
        ("Hemisferio", resultado.get("hemisferio")),
        ("Meridiano central", f'{resultado.get("meridiano_central")} grados'),
        ("Factor de escala puntual (k)", f'{resultado.get("k_utm", 0):.10f}'),
        ("Convergencia de meridianos (gamma)", resultado.get("convergencia_gms")),
    ]
    agregar_tabla("Parametros utilizados y calculados", parametros)

    elementos.append(Paragraph(
        "4. Procedimiento matematico", estilos["GeoSeccion"]
    ))

    if tipo_conversion == "Geograficas a UTM":
        explicacion = (
            "La conversion directa parte de latitud y longitud. Se determina la "
            "zona UTM y su meridiano central; despues se calcula el arco de "
            "meridiano y los terminos de la serie Transversa de Mercator. Las "
            "coordenadas auxiliares X e Y se multiplican por el factor central "
            "k0 y se agregan los falsos origenes para obtener Este y Norte."
        )
        elementos.append(Paragraph(explicacion, estilos["GeoTexto"]))
        agregar_formula("X = 500000 + k0 * x_TM")
        agregar_formula("Y = falso_norte + k0 * y_TM")
        agregar_formula("x_TM = a1*dL + a3*dL^3 + a5*dL^5")
        agregar_formula("y_TM = B + a2*dL^2 + a4*dL^4 + a6*dL^6")
        operaciones = [
            ("Arco de meridiano (B)", f'{resultado.get("arco_meridiano", 0):.6f} m'),
            ("Diferencia de longitud (dL)", f'{resultado.get("delta_lambda", 0):.12f} rad'),
            ("Coordenada auxiliar x_TM", f'{resultado.get("x_tm", 0):.6f} m'),
            ("Coordenada auxiliar y_TM", f'{resultado.get("y_tm", 0):.6f} m'),
            ("Factor central (k0)", resultado.get("k0")),
            ("Falso Este", f'{resultado.get("falso_este", 500000)} m'),
            ("Falso Norte", f'{resultado.get("falso_norte", 0)} m'),
        ]
    else:
        explicacion = (
            "La conversion inversa parte de Este y Norte UTM, zona y hemisferio. "
            "Primero se retiran los falsos origenes y el factor central k0 para "
            "recuperar las coordenadas auxiliares. La latitud se aproxima a "
            "partir del arco de meridiano mediante las iteraciones incluidas "
            "en el programa. Finalmente, las series inversas permiten obtener "
            "latitud y longitud geograficas."
        )
        elementos.append(Paragraph(explicacion, estilos["GeoTexto"]))
        agregar_formula("x_TM = (Este - 500000) / k0")
        agregar_formula("y_TM = (Norte - falso_norte) / k0")
        agregar_formula("phi = phi1 + b2*x_TM^2 + b4*x_TM^4 + b6*x_TM^6")
        agregar_formula("lambda = lambda0 + b1*x_TM + b3*x_TM^3 + b5*x_TM^5")
        operaciones = [
            ("Coordenada auxiliar x_TM", f'{resultado.get("x_tm", 0):.6f} m'),
            ("Coordenada auxiliar y_TM", f'{resultado.get("y_tm", 0):.6f} m'),
            ("Latitud aproximada inicial (phi0)", f'{resultado.get("phi0", 0):.12f} rad'),
            ("Primera aproximacion (phi1_aprox)", f'{resultado.get("phi1_aprox", 0):.12f} rad'),
            ("Segunda aproximacion (phi1)", f'{resultado.get("phi1", 0):.12f} rad'),
            ("Radio de curvatura (N1)", f'{resultado.get("N1", 0):.4f} m'),
            ("Falso Este", "500000 m"),
            ("Falso Norte", f'{10000000 if resultado.get("hemisferio") == "S" else 0} m'),
        ]

    elementos.append(Paragraph(
        "Relaciones utilizadas para los parametros de proyeccion",
        estilos["GeoSeccion"]
    ))
    agregar_formula(
        "B = c * [F0*phi + F1*sin(2phi) + F2*sin(4phi) + ... + F5*sin(10phi)]"
    )
    agregar_formula("k = k0 * m_TM;   m_TM = mt1 + mt2")
    if tipo_conversion == "Geograficas a UTM":
        agregar_formula("mt1 = 1 + [x_TM^2 / (2*N^2)] * [1 + e_prime2*cos(phi)^2]")
        agregar_formula("mt2 = [x_TM^4 / (24*N^4)] * [5 - 4*tan(phi)^2 + 14*e_prime2*cos(phi)^2]")
    else:
        agregar_formula("mt1 = 1 + [x_TM^2 / (2*N1^2)] * [1 + e_prime2*cos(phi)^2]")
        agregar_formula("mt2 = [x_TM^4 / (24*N1^4)] * [5 - 4*tan(phi)^2 + 14*e_prime2*cos(phi)^2]")
    agregar_formula("gamma = gamma1 + gamma2 + gamma3")
    agregar_formula("gamma1 = dL*sin(phi)")
    agregar_formula("gamma2 = (1/3)*dL^3*sin(phi)*cos(phi)^2*[1 + e_prime2*cos(phi)^2]")
    agregar_formula("gamma3 = (1/15)*dL^5*sin(phi)*cos(phi)^4*[2 - tan(phi)^2 + 5*e_prime2]")
    agregar_tabla("Valores intermedios principales", operaciones)

    elementos.append(Paragraph(
        "5. Interpretacion de los parametros", estilos["GeoSeccion"]
    ))
    k = resultado.get("k_utm", 0)
    diferencia_k = (1 - k) * 1000
    if k < 1:
        texto_k = (
            f"Para este punto, k = {k:.10f}, valor menor que 1. En la escala "
            f"de la cuadrícula, esto representa aproximadamente "
            f"{diferencia_k:.4f} mm menos por cada metro respecto de la "
            "distancia sobre el elipsoide, en el entorno del punto."
        )
    elif k > 1:
        texto_k = (
            f"Para este punto, k = {k:.10f}, valor mayor que 1. La escala "
            "de la cuadrícula es ligeramente mayor que la distancia sobre "
            "el elipsoide en el entorno del punto."
        )
    else:
        texto_k = (
            "Para este punto, el factor de escala es igual a 1; localmente, "
            "la escala de la cuadrícula coincide con la del elipsoide."
        )

    elementos.append(Paragraph(
        "El factor de escala puntual k expresa la relacion entre una distancia "
        "infinitesimal en la cuadrícula proyectada y su correspondiente sobre "
        "el elipsoide. " + texto_k,
        estilos["GeoTexto"]
    ))
    elementos.append(Paragraph(
        "La convergencia de meridianos (gamma) es el angulo entre el norte "
        "geografico y el norte de la cuadrícula UTM. Su signo y sentido deben "
        "interpretarse conforme a la convención utilizada por el programa. "
        "Este factor de escala es puntual y no incluye por sí solo una "
        "corrección por altura para obtener un factor combinado de terreno.",
        estilos["GeoTexto"]
    ))

    elementos.append(Paragraph(
        "6. Variables principales", estilos["GeoSeccion"]
    ))
    variables = [
        ("a, b, c", "Semiejes del elipsoide y radio polar de curvatura."),
        ("e2, e_prime2", "Primera y segunda excentricidad al cuadrado."),
        ("F0 a F5", "Coeficientes de Fourier usados en la serie del arco de meridiano."),
        ("phi, lambda0", "Latitud del punto y meridiano central, en radianes."),
        ("dL", "Diferencia entre longitud del punto y meridiano central."),
        ("B", "Arco de meridiano calculado mediante la serie de Fourier."),
        ("N", "Radio de curvatura del primer vertical en la conversion directa."),
        ("N1", "Radio de curvatura del primer vertical en la conversion inversa."),
        ("k0", "Factor de escala central de UTM (0.9996)."),
        ("x_TM, y_TM", "Coordenadas auxiliares de la proyeccion Transversa de Mercator."),
        ("a1 a a6 / b1 a b6", "Coeficientes de las series directa e inversa."),
        ("gamma", "Convergencia de meridianos."),
    ]
    agregar_tabla("Glosario de simbolos", variables)

    elementos.append(Paragraph(
        "7. Alcance y observaciones", estilos["GeoSeccion"]
    ))
    elementos.append(Paragraph(
        "Los resultados y valores intermedios de este reporte proceden "
        "directamente del modulo de conversiones de GEOARCOS. Las formulas "
        "mostradas resumen las operaciones principales; el programa conserva "
        "los terminos y coeficientes de las series implementadas. El documento "
        "no sustituye una memoria de calculo completa ni una validacion "
        "independiente. Para trabajos de alta precision, se recomienda "
        "contrastar los resultados con puntos de control o software geodesico "
        "de referencia y documentar el sistema de referencia completo.",
        estilos["GeoTexto"]
    ))
    elementos.append(Spacer(1, 5))
    elementos.append(Paragraph(
        "GEOARCOS | Proyecto academico de Ingenieria Topografica y Geodesia",
        estilos["GeoNota"]
    ))

    def pie_pagina(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(borde)
        canvas.setLineWidth(0.5)
        canvas.line(1.55 * cm, 1.15 * cm, letter[0] - 1.55 * cm, 1.15 * cm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(gris)
        canvas.drawString(1.55 * cm, 0.8 * cm, "GEOARCOS | Reporte de conversion geodesica")
        canvas.drawRightString(letter[0] - 1.55 * cm, 0.8 * cm, f"Pagina {doc.page}")
        canvas.restoreState()

    documento.build(elementos, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# CONFIGURACION GENERAL
# ============================================================

st.set_page_config(
    page_title="GEOARCOS | Calculadora Geodesica",
    page_icon="🌎",
    layout="wide"
)

# ============================================================
# ESTILO VISUAL
# ============================================================

st.markdown("""
<style>
    :root {
        color-scheme: light;
        --geo-navy: #17324F;
        --geo-blue: #1677B8;
        --geo-cyan: #35A9D6;
        --geo-ink: #243447;
        --geo-muted: #64748B;
        --geo-border: #DCE5EF;
        --geo-bg: #F3F6FA;
        --geo-card: #FFFFFF;
    }

    /* Fondo y area de trabajo */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: var(--geo-bg) !important;
        color: var(--geo-ink) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(243, 246, 250, 0.92) !important;
    }

    [data-testid="stMain"] > div {
        padding-top: 1.6rem;
    }

    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Tipografia general */
    .stApp p, .stApp span, .stApp label,
    .stApp li, .stApp [data-testid="stMarkdownContainer"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: var(--geo-ink) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--geo-navy) !important;
        letter-spacing: -0.025em;
        font-weight: 700 !important;
    }

    h1 { font-size: 2.15rem !important; }
    h2 { font-size: 1.55rem !important; }
    h3 { font-size: 1.15rem !important; }

    [data-testid="stCaptionContainer"],
    .stCaption {
        color: var(--geo-muted) !important;
    }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid var(--geo-border);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: #FFFFFF !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--geo-ink) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--geo-navy) !important;
    }

    /* Encabezado GEOARCOS */
    .encabezado {
        background: linear-gradient(120deg, #FFFFFF 0%, #EAF3FA 100%);
        color: var(--geo-navy);
        padding: 30px 34px;
        border: 1px solid var(--geo-border);
        border-left: 6px solid var(--geo-blue);
        border-radius: 18px;
        margin-bottom: 30px;
        box-shadow: 0 8px 24px rgba(23, 50, 79, 0.06);
    }

    .encabezado h1 {
        color: var(--geo-navy) !important;
        font-size: 2.6rem !important;
        margin: 0 0 8px 0;
        letter-spacing: 0.015em;
    }

    .encabezado p {
        color: #52677D !important;
        margin: 3px 0;
        font-size: 1rem;
    }

    /* Metricas y resultados */
    div[data-testid="stMetric"] {
        background: var(--geo-card) !important;
        border: 1px solid var(--geo-border) !important;
        border-radius: 14px !important;
        padding: 18px 20px !important;
        box-shadow: 0 5px 16px rgba(23, 50, 79, 0.045);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] label p,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: var(--geo-muted) !important;
        font-size: 0.88rem !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] div {
        color: var(--geo-navy) !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #16805D !important;
    }

    /* Campos de captura */
    .stNumberInput input,
    .stTextInput input,
    .stTextArea textarea {
        background: #FFFFFF !important;
        color: var(--geo-ink) !important;
        border: 1px solid #C9D5E2 !important;
        border-radius: 9px !important;
    }

    .stNumberInput input:focus,
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--geo-blue) !important;
        box-shadow: 0 0 0 2px rgba(22, 119, 184, 0.12) !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        color: var(--geo-ink) !important;
        border-color: #C9D5E2 !important;
        border-radius: 9px !important;
    }

    .stSelectbox div[data-baseweb="select"] span {
        color: var(--geo-ink) !important;
    }

    /* Radio buttons y casillas */
    .stRadio label, .stCheckbox label {
        color: var(--geo-ink) !important;
    }

    /* Botones */
    .stButton button {
        background: var(--geo-blue) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--geo-blue) !important;
        border-radius: 10px !important;
        min-height: 2.8rem;
        font-weight: 650 !important;
        transition: background 0.18s ease, transform 0.18s ease;
    }

    .stButton button:hover {
        background: #125F94 !important;
        border-color: #125F94 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }

    /* Mensajes */
    [data-testid="stAlert"] {
        border-radius: 11px !important;
        border: 1px solid var(--geo-border) !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div {
        color: inherit;
    }

    /* Paneles desplegables y tablas */
    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid var(--geo-border) !important;
        border-radius: 12px !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: var(--geo-navy) !important;
        font-weight: 600;
    }

    [data-testid="stJson"] {
        background: #F8FAFC !important;
        color: var(--geo-ink) !important;
        border: 1px solid var(--geo-border);
        border-radius: 9px;
        padding: 12px;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        color: var(--geo-ink) !important;
    }

    hr {
        border-color: var(--geo-border) !important;
    }

    a {
        color: var(--geo-blue) !important;
    }

    /* Separacion visual entre secciones */
    [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {
        scroll-margin-top: 1rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .encabezado {
            padding: 22px;
        }
        .encabezado h1 {
            font-size: 2rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ENCABEZADO
# ============================================================

st.markdown("""
<div class="encabezado">
    <h1>GEOARCOS</h1>
    <p>Calculadora de conversion de coordenadas geodesicas</p>
    <p>Coordenadas geograficas | Sistema UTM | Elipsoides</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MENU PRINCIPAL
# ============================================================

st.sidebar.title("GEOARCOS")
st.sidebar.caption("Herramienta geodesica")

modo = st.sidebar.radio(
    "Selecciona el tipo de conversion:",
    [
        "Geograficas a UTM",
        "UTM a Geograficas"
    ]
)

elipsoide = st.sidebar.selectbox(
    "Selecciona el elipsoide:",
    list(ELIPSOIDES.keys())
)

parametros = ELIPSOIDES[elipsoide]

st.sidebar.divider()

st.sidebar.subheader("Parametros del elipsoide")

st.sidebar.write(f"Semieje mayor (a): {parametros['a']:,.4f} m")
st.sidebar.write(f"Semieje menor (b): {parametros['b']:,.4f} m")

# ============================================================
# CONVERSION GEOGRAFICAS A UTM
# ============================================================

if modo == "Geograficas a UTM":

    st.header("Conversion de coordenadas geograficas a UTM")

    tipo_entrada = st.radio(
        "Formato de coordenadas de entrada:",
        ["Grados decimales", "Grados, minutos y segundos"],
        horizontal=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Latitud")

        if tipo_entrada == "Grados decimales":

            latitud = st.number_input(
                "Latitud decimal",
                min_value=-90.0,
                max_value=90.0,
                value=19.6998403,
                format="%.10f"
            )

        else:
            lat_grados = st.number_input(
                "Grados de latitud",
                min_value=0,
                max_value=90,
                value=19
            )

            lat_minutos = st.number_input(
                "Minutos de latitud",
                min_value=0,
                max_value=59,
                value=41
            )

            lat_segundos = st.number_input(
                "Segundos de latitud",
                min_value=0.0,
                max_value=59.999999,
                value=59.425,
                format="%.6f"
            )

            lat_hemisferio = st.selectbox(
                "Hemisferio de latitud",
                ["N", "S"]
            )

            latitud = gms_a_decimal(
                lat_grados,
                lat_minutos,
                lat_segundos,
                lat_hemisferio
            )

    with col2:
        st.subheader("Longitud")

        if tipo_entrada == "Grados decimales":

            longitud = st.number_input(
                "Longitud decimal",
                min_value=-180.0,
                max_value=180.0,
                value=-105.4220961,
                format="%.10f"
            )

        else:
            lon_grados = st.number_input(
                "Grados de longitud",
                min_value=0,
                max_value=180,
                value=105
            )

            lon_minutos = st.number_input(
                "Minutos de longitud",
                min_value=0,
                max_value=59,
                value=25
            )

            lon_segundos = st.number_input(
                "Segundos de longitud",
                min_value=0.0,
                max_value=59.999999,
                value=19.546,
                format="%.6f"
            )

            lon_hemisferio = st.selectbox(
                "Hemisferio de longitud",
                ["W", "E"]
            )

            longitud = gms_a_decimal(
                lon_grados,
                lon_minutos,
                lon_segundos,
                lon_hemisferio
            )

    zona_manual = st.checkbox(
        "Introducir manualmente la zona UTM"
    )

    if zona_manual:
        zona = st.number_input(
            "Zona UTM",
            min_value=1,
            max_value=60,
            value=13,
            step=1
        )
        zona = int(zona)
    else:
        zona = None

    if st.button("CALCULAR COORDENADAS UTM", use_container_width=True):

        try:
            resultado = geograficas_a_utm(
                latitud=latitud,
                longitud=longitud,
                elipsoide=elipsoide,
                zona=zona
            )
            st.session_state["geoarc_resultado_pdf"] = resultado
            st.session_state["geoarc_tipo_pdf"] = "Geograficas a UTM"

            st.success("Conversion realizada correctamente.")

            st.subheader("Resultados UTM")

            r1, r2 = st.columns(2)

            r1.metric(
                "Este UTM (X)",
                f"{resultado['este']:,.4f} m"
            )

            r2.metric(
                "Norte UTM (Y)",
                f"{resultado['norte']:,.4f} m"
            )

            st.subheader("Informacion de la conversion")

            c1, c2, c3 = st.columns(3)

            c1.metric("Zona UTM", resultado["zona"])
            c2.metric("Hemisferio", resultado["hemisferio"])
            c3.metric(
                "Meridiano central",
                f"{resultado['meridiano_central']}°"
            )

            c4, c5 = st.columns(2)
            c4.metric(
                "Factor de escala (k)",
                f"{resultado['k_utm']:.8f}"
            )
            c5.metric(
                "Convergencia de meridianos (γ)",
                resultado["convergencia_gms"]
            )

            st.write("**Coordenadas geograficas de entrada**")

            st.write(
                "Latitud:",
                resultado["latitud_gms"]
            )

            st.write(
                "Longitud:",
                resultado["longitud_gms"]
            )

            st.subheader("Parametros calculados")

            with st.expander("Consultar parametros y operaciones intermedias"):

                st.json(resultado)

        except Exception as error:
            st.error(f"No fue posible realizar la conversion: {error}")


# ============================================================
# CONVERSION UTM A GEOGRAFICAS
# ============================================================

else:

    st.header("Conversion de coordenadas UTM a geograficas")

    st.write("Introduce las coordenadas proyectadas del punto.")

    col1, col2 = st.columns(2)

    with col1:
        este = st.number_input(
            "Este UTM (X), en metros",
            value=455763.141129,
            format="%.6f"
        )

    with col2:
        norte = st.number_input(
            "Norte UTM (Y), en metros",
            value=2178321.118994,
            format="%.6f"
        )

    col3, col4 = st.columns(2)

    with col3:
        zona = st.number_input(
            "Zona UTM",
            min_value=1,
            max_value=60,
            value=13,
            step=1
        )

    with col4:
        hemisferio = st.selectbox(
            "Hemisferio",
            ["N", "S"]
        )

    if st.button("CALCULAR COORDENADAS GEOGRAFICAS", use_container_width=True):

        try:
            resultado = utm_a_geograficas(
                este=este,
                norte=norte,
                zona=int(zona),
                hemisferio=hemisferio,
                elipsoide=elipsoide
            )
            st.session_state["geoarc_resultado_pdf"] = resultado
            st.session_state["geoarc_tipo_pdf"] = "UTM a Geograficas"

            st.success("Conversion realizada correctamente.")

            st.subheader("Resultados geograficos")

            r1, r2 = st.columns(2)

            r1.metric(
                "Latitud decimal",
                f"{resultado['latitud_decimal']:.10f}°"
            )

            r2.metric(
                "Longitud decimal",
                f"{resultado['longitud_decimal']:.10f}°"
            )

            st.subheader("Coordenadas en grados, minutos y segundos")

            c1, c2 = st.columns(2)

            c1.info(resultado["latitud_gms"])
            c2.info(resultado["longitud_gms"])

            st.subheader("Informacion de la conversion")

            c3, c4, c5 = st.columns(3)

            c3.metric("Zona UTM", resultado["zona"])
            c4.metric("Hemisferio", resultado["hemisferio"])
            c5.metric(
                "Meridiano central",
                f"{resultado['meridiano_central']}°"
            )

            c6, c7 = st.columns(2)
            c6.metric(
                "Factor de escala (k)",
                f"{resultado['k_utm']:.8f}"
            )
            c7.metric(
                "Convergencia de meridianos (γ)",
                resultado["convergencia_gms"]
            )

            with st.expander("Consultar parametros y operaciones intermedias"):

                st.json(resultado)

        except Exception as error:
            st.error(f"No fue posible realizar la conversion: {error}")


# ============================================================
# DESCARGA DEL REPORTE PDF
# ============================================================

if "geoarc_resultado_pdf" in st.session_state:
    st.divider()
    st.subheader("Reporte tecnico de la conversion")
    st.write(
        "Genera un documento con los datos de entrada, resultados, "
        "parametros geodesicos y una explicacion del procedimiento."
    )

    try:
        pdf_generado = crear_reporte_pdf(
            st.session_state["geoarc_resultado_pdf"],
            st.session_state["geoarc_tipo_pdf"]
        )
        st.download_button(
            label="DESCARGAR REPORTE PDF",
            data=pdf_generado,
            file_name="GEOARCOS_Reporte_Geodesico.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as error:
        st.error(f"No fue posible generar el reporte PDF: {error}")


# ============================================================
# INFORMACION GENERAL
# ============================================================

st.divider()

st.caption(
    "GEOARCOS | Calculadora geodesica | "
    "Proyecto academico de Ingenieria Topografica y Geodesia"
)

