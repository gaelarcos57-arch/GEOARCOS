
# ============================================================
# GEOARCOS
# MODULO 2: CONVERSIONES GEOGRAFICAS Y UTM
# Basado en las formulas del archivo Excel del proyecto
# ============================================================

import math
from elipsoides import obtener_parametros


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def gms_a_decimal(grados, minutos, segundos, hemisferio):
    """Convierte grados, minutos y segundos a grados decimales."""

    grados = float(grados)
    minutos = float(minutos)
    segundos = float(segundos)
    hemisferio = hemisferio.upper()

    if minutos < 0 or minutos >= 60:
        raise ValueError("Los minutos deben estar entre 0 y 59.")

    if segundos < 0 or segundos >= 60:
        raise ValueError("Los segundos deben ser mayores o iguales a 0 y menores que 60.")

    decimal = abs(grados) + minutos / 60 + segundos / 3600

    if hemisferio in ("S", "W", "O"):
        decimal = -decimal
    elif hemisferio not in ("N", "E"):
        raise ValueError("Hemisferio no valido. Utiliza N, S, E o W.")

    return decimal


def decimal_a_gms(valor, tipo):
    """Convierte grados decimales a grados, minutos y segundos."""

    hemisferio = ""

    if tipo == "latitud":
        hemisferio = "N" if valor >= 0 else "S"
    elif tipo == "longitud":
        hemisferio = "E" if valor >= 0 else "W"

    valor = abs(valor)

    grados = int(valor)
    minutos_completos = (valor - grados) * 60
    minutos = int(minutos_completos)
    segundos = (minutos_completos - minutos) * 60

    return (
        f"{grados}° {minutos}' "
        f"{segundos:.4f}'' {hemisferio}"
    )


def obtener_coeficientes_fourier(e_prime2):
    """Calcula los coeficientes F0 a F5 del Excel."""

    F0 = (
        1
        - (3 / 4) * e_prime2
        + (45 / 64) * e_prime2**2
        - (175 / 256) * e_prime2**3
        + (11025 / 16384) * e_prime2**4
        - (43659 / 65536) * e_prime2**5
    )

    F1 = (
        -(3 / 8) * e_prime2
        + (15 / 32) * e_prime2**2
        - (525 / 1024) * e_prime2**3
        + (2205 / 4096) * e_prime2**4
        - (72765 / 131072) * e_prime2**5
    )

    F2 = (
        (15 / 256) * e_prime2**2
        - (105 / 1024) * e_prime2**3
        + (2205 / 16384) * e_prime2**4
        - (10395 / 65536) * e_prime2**5
    )

    F3 = (
        -(35 / 3072) * e_prime2**3
        + (315 / 12288) * e_prime2**4
        - (31185 / 786432) * e_prime2**5
    )

    F4 = (
        (315 / 131072) * e_prime2**4
        - (3465 / 524288) * e_prime2**5
    )

    F5 = -(693 / 1310720) * e_prime2**5

    return {
        "F0": F0,
        "F1": F1,
        "F2": F2,
        "F3": F3,
        "F4": F4,
        "F5": F5
    }


def calcular_arco_meridiano(phi, c, coeficientes):
    """Calcula el arco de meridiano mediante la serie de Fourier."""

    F0 = coeficientes["F0"]
    F1 = coeficientes["F1"]
    F2 = coeficientes["F2"]
    F3 = coeficientes["F3"]
    F4 = coeficientes["F4"]
    F5 = coeficientes["F5"]

    B = c * (
        F0 * phi
        + F1 * math.sin(2 * phi)
        + F2 * math.sin(4 * phi)
        + F3 * math.sin(6 * phi)
        + F4 * math.sin(8 * phi)
        + F5 * math.sin(10 * phi)
    )

    return B


def calcular_convergencia(delta_lambda, phi):
    """Calcula la convergencia de meridianos."""

    termino1 = delta_lambda * math.sin(phi)

    termino2 = (
        (1 / 3)
        * delta_lambda**3
        * math.sin(phi)
        * math.cos(phi)**2
        * (1 + math.sin(phi)**0 * 0)
    )

    # Expresion del Excel: utiliza e'2.
    # El valor de e'2 se incorpora desde la funcion principal.
    return termino1, termino2


def calcular_estado_error(error):
    """Clasifica el error de cierre con los limites del Excel."""

    if error <= 0.01:
        return "MUY BUENO (<= 1 cm)"
    elif error <= 0.05:
        return "ACEPTABLE (<= 5 cm)"
    elif error <= 0.10:
        return "REVISAR"
    else:
        return "FUERA DE TOLERANCIA"


# ============================================================
# CONVERSION 1: GEOGRAFICAS A UTM
# ============================================================

def geograficas_a_utm(latitud, longitud, elipsoide, zona=None):

    # Obtener parametros del elipsoide seleccionado
    p = obtener_parametros(elipsoide)

    a = p["a"]
    b = p["b"]
    e2 = p["e2"]
    ep2 = p["e_prime2"]
    c = p["c"]

    # Validar coordenadas
    if not -90 <= latitud <= 90:
        raise ValueError("La latitud debe estar entre -90 y 90 grados.")

    if not -180 <= longitud <= 180:
        raise ValueError("La longitud debe estar entre -180 y 180 grados.")

    # Determinar hemisferio
    hemisferio = "N" if latitud >= 0 else "S"

    # Determinar zona UTM
    if zona is None:
        zona = min(60, max(1, int((longitud + 180) / 6) + 1))

    if not isinstance(zona, int) or not 1 <= zona <= 60:
        raise ValueError("La zona UTM debe ser un entero entre 1 y 60.")

    # Meridiano central
    lambda0_grados = 6 * zona - 183
    lambda0 = math.radians(lambda0_grados)

    # Coordenadas geograficas en radianes
    phi = math.radians(latitud)
    lam = math.radians(longitud)

    # Diferencia de longitud
    delta_lambda = lam - lambda0

    # Radio de curvatura del primer vertical
    N = a / math.sqrt(1 - e2 * math.sin(phi)**2)

    # Coeficientes de Fourier
    F = obtener_coeficientes_fourier(ep2)

    # Arco de meridiano
    B = calcular_arco_meridiano(phi, c, F)

    # Coeficientes de la serie directa
    a1 = N * math.cos(phi)

    a2 = (1 / 2) * a1 * math.sin(phi)

    a3 = (
        (1 / 6)
        * a1
        * (
            -1
            + 2 * math.cos(phi)**2
            + ep2 * math.cos(phi)**4
        )
    )

    a4 = (
        (1 / 12)
        * a2
        * (
            -1
            + 6 * math.cos(phi)**2
            + 9 * ep2 * math.cos(phi)**4
            + 4 * ep2**2 * math.cos(phi)**6
        )
    )

    a5 = (
        (1 / 120)
        * a1
        * (
            1
            - 20 * math.cos(phi)**2
            + (24 - 58 * ep2) * math.cos(phi)**4
            + 72 * ep2 * math.cos(phi)**6
        )
    )

    # Se conserva exactamente la expresion a6 del Excel.
    a6 = (
        (1 / 360)
        * a2
        * (
            1
            - 60 * math.cos(phi)**2
            + 120 * math.cos(phi)**4
            + 600 * ep2 * math.cos(phi)**6
            - 330 * ep2 * math.cos(phi)**4
        )
    )

    # Coordenadas TM
    x = (
        a1 * delta_lambda
        + a3 * delta_lambda**3
        + a5 * delta_lambda**5
    )

    y = (
        B
        + a2 * delta_lambda**2
        + a4 * delta_lambda**4
        + a6 * delta_lambda**6
    )

    # Parametros UTM
    k0 = 0.9996
    falso_este = 500000
    falso_norte = 10000000 if hemisferio == "S" else 0

    # Coordenadas UTM finales
    este = falso_este + k0 * x
    norte = falso_norte + k0 * y

    # Convergencia de meridianos
    gamma1 = delta_lambda * math.sin(phi)

    gamma2 = (
        (1 / 3)
        * delta_lambda**3
        * math.sin(phi)
        * math.cos(phi)**2
        * (1 + ep2 * math.cos(phi)**2)
    )

    gamma3 = (
        (1 / 15)
        * delta_lambda**5
        * math.sin(phi)
        * math.cos(phi)**4
        * (2 - math.tan(phi)**2 + 5 * ep2)
    )

    gamma_rad = gamma1 + gamma2 + gamma3
    gamma_deg = math.degrees(gamma_rad)

    # Factor de escala
    mt1 = 1 + (
        x**2 / (2 * N**2)
    ) * (1 + ep2 * math.cos(phi)**2)

    mt2 = (
        x**4 / (24 * N**4)
    ) * (
        5
        - 4 * math.tan(phi)**2
        + 14 * ep2 * math.cos(phi)**2
    )

    m_tm = mt1 + mt2
    k_utm = k0 * m_tm

    return {
        "direccion": "Geograficas a UTM",
        "elipsoide": elipsoide,
        "a": a,
        "b": b,
        "e2": e2,
        "e_prime2": ep2,
        "c": c,
        "latitud_decimal": latitud,
        "longitud_decimal": longitud,
        "latitud_gms": decimal_a_gms(latitud, "latitud"),
        "longitud_gms": decimal_a_gms(longitud, "longitud"),
        "zona": zona,
        "hemisferio": hemisferio,
        "meridiano_central": lambda0_grados,
        "N": N,
        "arco_meridiano": B,
        "coeficientes_fourier": F,
        "a1": a1,
        "a2": a2,
        "a3": a3,
        "a4": a4,
        "a5": a5,
        "a6": a6,
        "delta_lambda": delta_lambda,
        "x_tm": x,
        "y_tm": y,
        "falso_este": falso_este,
        "falso_norte": falso_norte,
        "k0": k0,
        "este": este,
        "norte": norte,
        "gamma1": gamma1,
        "gamma2": gamma2,
        "gamma3": gamma3,
        "convergencia_rad": gamma_rad,
        "convergencia_deg": gamma_deg,
        "convergencia_gms": decimal_a_gms(gamma_deg, "latitud"),
        "mt1": mt1,
        "mt2": mt2,
        "m_tm": m_tm,
        "k_utm": k_utm
    }


# ============================================================
# CONVERSION 2: UTM A GEOGRAFICAS
# ============================================================

def utm_a_geograficas(este, norte, zona, hemisferio, elipsoide):

    # Obtener parametros del elipsoide
    p = obtener_parametros(elipsoide)

    a = p["a"]
    b = p["b"]
    e2 = p["e2"]
    ep2 = p["e_prime2"]
    c = p["c"]

    hemisferio = hemisferio.upper()

    if not isinstance(zona, int) or not 1 <= zona <= 60:
        raise ValueError("La zona UTM debe ser un entero entre 1 y 60.")

    if hemisferio not in ("N", "S"):
        raise ValueError("El hemisferio debe ser N o S.")

    # Meridiano central
    lambda0_grados = 6 * zona - 183
    lambda0 = math.radians(lambda0_grados)

    # Recuperar coordenadas TM
    k0 = 0.9996

    x = (este - 500000) / k0

    falso_norte = 10000000 if hemisferio == "S" else 0
    y = (norte - falso_norte) / k0

    # Coeficientes de Fourier
    F = obtener_coeficientes_fourier(ep2)

    F0 = F["F0"]
    F1 = F["F1"]
    F2 = F["F2"]
    F3 = F["F3"]
    F4 = F["F4"]
    F5 = F["F5"]

    # Latitud aproximada inicial
    phi0 = y / c

    # Arco de meridiano B1
    B1 = calcular_arco_meridiano(phi0, c, F)

    # Primera iteracion
    phi1_aprox = phi0 + (
        (y - B1) /
        (c / (1 + ep2 * math.cos(phi0)**2)**(3 / 2))
    )

    # Arco de meridiano B2
    B2 = calcular_arco_meridiano(phi1_aprox, c, F)

    # Segunda iteracion
    phi1 = phi1_aprox + (
        (y - B2) /
        (c / (1 + ep2 * math.cos(phi1_aprox)**2)**(3 / 2))
    )

    # Radio de curvatura del primer vertical
    N1 = a / math.sqrt(1 - e2 * math.sin(phi1)**2)

    # Coeficientes de la serie inversa
    b1 = 1 / (N1 * math.cos(phi1))

    b2 = (
        -(1 / 2)
        * b1**2
        * math.sin(phi1)
        * math.cos(phi1)
        * (1 + ep2 * math.cos(phi1)**2)
    )

    b3 = (
        -(1 / 6)
        * b1**3
        * (
            2
            - math.cos(phi1)**2
            + ep2 * math.cos(phi1)**4
        )
    )

    b4 = (
        -(1 / 12)
        * b1**2
        * b2
        * (
            3
            + (2 - 9 * ep2) * math.cos(phi1)**2
            + 10 * ep2 * math.cos(phi1)**4
            - 4 * ep2**2 * math.cos(phi1)**6
        )
    )

    b5 = (
        (1 / 120)
        * b1**5
        * (
            24
            - 20 * math.cos(phi1)**2
            + (1 + 8 * ep2) * math.cos(phi1)**4
            - 2 * ep2 * math.cos(phi1)**6
        )
    )

    b6 = (
        (1 / 360)
        * b1**4
        * b2
        * (
            45 + 16 * math.cos(phi1)**4
        )
    )

    # Coordenadas geograficas en radianes
    phi = (
        phi1
        + b2 * x**2
        + b4 * x**4
        + b6 * x**6
    )

    lam = (
        lambda0
        + b1 * x
        + b3 * x**3
        + b5 * x**5
    )

    # Convertir a grados decimales
    latitud = math.degrees(phi)
    longitud = math.degrees(lam)

    # Convergencia de meridianos
    delta_lambda = lam - lambda0

    gamma1 = delta_lambda * math.sin(phi)

    gamma2 = (
        (1 / 3)
        * delta_lambda**3
        * math.sin(phi)
        * math.cos(phi)**2
        * (1 + ep2 * math.cos(phi)**2)
    )

    gamma3 = (
        (1 / 15)
        * delta_lambda**5
        * math.sin(phi)
        * math.cos(phi)**4
        * (2 - math.tan(phi)**2 + 5 * ep2)
    )

    gamma_rad = gamma1 + gamma2 + gamma3
    gamma_deg = math.degrees(gamma_rad)

    # Factor de escala
    mt1 = 1 + (
        x**2 / (2 * N1**2)
    ) * (1 + ep2 * math.cos(phi)**2)

    mt2 = (
        x**4 / (24 * N1**4)
    ) * (
        5
        - 4 * math.tan(phi)**2
        + 14 * ep2 * math.cos(phi)**2
    )

    m_tm = mt1 + mt2
    k_utm = k0 * m_tm

    return {
        "direccion": "UTM a Geograficas",
        "elipsoide": elipsoide,
        "a": a,
        "b": b,
        "e2": e2,
        "e_prime2": ep2,
        "c": c,
        "este_entrada": este,
        "norte_entrada": norte,
        "zona": zona,
        "hemisferio": hemisferio,
        "meridiano_central": lambda0_grados,
        "x_tm": x,
        "y_tm": y,
        "coeficientes_fourier": F,
        "phi0": phi0,
        "B1": B1,
        "phi1_aprox": phi1_aprox,
        "B2": B2,
        "phi1": phi1,
        "N1": N1,
        "b1": b1,
        "b2": b2,
        "b3": b3,
        "b4": b4,
        "b5": b5,
        "b6": b6,
        "latitud_rad": phi,
        "longitud_rad": lam,
        "latitud_decimal": latitud,
        "longitud_decimal": longitud,
        "latitud_gms": decimal_a_gms(latitud, "latitud"),
        "longitud_gms": decimal_a_gms(longitud, "longitud"),
        "delta_lambda": delta_lambda,
        "gamma1": gamma1,
        "gamma2": gamma2,
        "gamma3": gamma3,
        "convergencia_rad": gamma_rad,
        "convergencia_deg": gamma_deg,
        "convergencia_gms": decimal_a_gms(gamma_deg, "latitud"),
        "mt1": mt1,
        "mt2": mt2,
        "m_tm": m_tm,
        "k_utm": k_utm
    }


# ============================================================
# PRUEBA DEL MODULO
# ============================================================

if __name__ == "__main__":

    print("======================================")
    print("             GEOARCOS")
    print("       MODULO DE CONVERSIONES")
    print("======================================")

    # Datos de prueba del Excel
    resultado = geograficas_a_utm(
        latitud=33 + 38 / 60 + 58.589 / 3600,
        longitud=54 + 48 / 60 + 54.887 / 3600,
        elipsoide="GRS80",
        zona=40
    )

    print("\nPRUEBA: GEOGRAFICAS A UTM")
    print("Elipsoide:", resultado["elipsoide"])
    print("Zona:", resultado["zona"])
    print("Este UTM:", resultado["este"])
    print("Norte UTM:", resultado["norte"])

    print("\nModulo de conversiones ejecutado.")

    # =========================================
    # SEGUNDA PRUEBA: UTM A GEOGRAFICAS
    # =========================================

    resultado_inverso = utm_a_geograficas(
        este=resultado["este"],
        norte=resultado["norte"],
        zona=resultado["zona"],
        hemisferio=resultado["hemisferio"],
        elipsoide="GRS80"
    )

    print("\nPRUEBA: UTM A GEOGRAFICAS")

    print("Latitud decimal:",
          resultado_inverso["latitud_decimal"])

    print("Longitud decimal:",
          resultado_inverso["longitud_decimal"])

    print("Latitud GMS:",
          resultado_inverso["latitud_gms"])

    print("Longitud GMS:",
          resultado_inverso["longitud_gms"])

    # Comparacion con las coordenadas originales
    error_latitud = abs(
        resultado_inverso["latitud_decimal"]
        - resultado["latitud_decimal"]
    )

    error_longitud = abs(
        resultado_inverso["longitud_decimal"]
        - resultado["longitud_decimal"]
    )

    print("\nCOMPROBACION DE IDA Y VUELTA")
    print("Diferencia de latitud:", error_latitud)
    print("Diferencia de longitud:", error_longitud)

# =========================================
# PRUEBA 2: ELIPSOIDE WGS84 - HEMISFERIO SUR
# =========================================

print("\n======================================")
print("PRUEBA 2: HEMISFERIO SUR")
print("======================================")

prueba_sur = geograficas_a_utm(
    latitud=-33.9,
    longitud=18.4,
    elipsoide="WGS84",
    zona=34
)

print("Elipsoide:", prueba_sur["elipsoide"])
print("Hemisferio:", prueba_sur["hemisferio"])
print("Zona:", prueba_sur["zona"])
print("Este UTM:", prueba_sur["este"])
print("Norte UTM:", prueba_sur["norte"])

# Recuperar las coordenadas geograficas

recuperacion_sur = utm_a_geograficas(
    este=prueba_sur["este"],
    norte=prueba_sur["norte"],
    zona=prueba_sur["zona"],
    hemisferio=prueba_sur["hemisferio"],
    elipsoide="WGS84"
)

print("\nRECUPERACION DE COORDENADAS")

print("Latitud:", recuperacion_sur["latitud_decimal"])
print("Longitud:", recuperacion_sur["longitud_decimal"])

print("\nDIFERENCIAS")

print(
    "Latitud:",
    abs(recuperacion_sur["latitud_decimal"] - (-33.9))
)

print(
    "Longitud:",
    abs(recuperacion_sur["longitud_decimal"] - 18.4)
)

# =====================================================
# PRUEBA 3: COMPARACION INDEPENDIENTE CON EXCEL
# UTM -> GEOGRAFICAS -> UTM
# =====================================================

print("\n======================================")
print("PRUEBA 3: COMPARACION CON EXCEL")
print("======================================")

# Coordenadas UTM introducidas manualmente
este_excel = 297399.022845615
norte_excel = 3725447.31716203
zona_excel = 40
hemisferio_excel = "N"

# Primera conversion: UTM a geograficas
resultado_excel = utm_a_geograficas(
    este=este_excel,
    norte=norte_excel,
    zona=zona_excel,
    hemisferio=hemisferio_excel,
    elipsoide="GRS80"
)

print("\nRESULTADO GEOGRAFICO")

print("Latitud:", resultado_excel["latitud_decimal"])
print("Longitud:", resultado_excel["longitud_decimal"])

# Segunda conversion: geograficas a UTM
resultado_cierre = geograficas_a_utm(
    latitud=resultado_excel["latitud_decimal"],
    longitud=resultado_excel["longitud_decimal"],
    elipsoide="GRS80",
    zona=zona_excel
)

print("\nCOMPROBACION DE CIERRE UTM")

print("Este recuperado:", resultado_cierre["este"])
print("Norte recuperado:", resultado_cierre["norte"])

# Diferencias respecto a los datos originales
error_este = abs(
    resultado_cierre["este"] - este_excel
)

error_norte = abs(
    resultado_cierre["norte"] - norte_excel
)

print("\nERRORES DE CIERRE")

print("Error Este (m):", error_este)
print("Error Norte (m):", error_norte)

print("\nFIN DE LA PRUEBA 3")

