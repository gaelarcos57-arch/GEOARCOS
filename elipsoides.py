
# ============================================================
# GEOARCOS
# MÓDULO 1: CATÁLOGO DE ELIPSOIDES
# Ingeniería Topográfica y Geodesia
# ============================================================

# Catálogo de los 22 elipsoides
# Valores tomados de la tabla de Excel del proyecto

ELIPSOIDES = {

    "Airy 1830": {
        "a": 6377563.396,
        "b": 6356256.910
    },

    "Airy Modificado 1965": {
        "a": 6377340.189,
        "b": 6356034.4479
    },

    "Bessel 1841": {
        "a": 6377397.155,
        "b": 6356078.96284
    },

    "Clarke 1866": {
        "a": 6378206.400,
        "b": 6356583.800
    },

    "Clarke 1880": {
        "a": 6378249.145,
        "b": 6356514.86955
    },

    "Fischer 1960": {
        "a": 6378166.000,
        "b": 6356784.280
    },

    "Fischer 1968": {
        "a": 6378150.000,
        "b": 6356768.330
    },

    "GRS80": {
        "a": 6378137.000,
        "b": 6356752.31414
    },

    "Hayford 1909": {
        "a": 6378388.000,
        "b": 6356911.94613
    },

    "Helmert 1906": {
        "a": 6378200.000,
        "b": 6356818.170
    },

    "Hough 1960": {
        "a": 6378270.000,
        "b": 6356794.343479
    },

    "Internacional 1909": {
        "a": 6378388.000,
        "b": 6356911.94613
    },

    "Internacional 1924": {
        "a": 6378388.000,
        "b": 6356911.94613
    },

    "Krasovsky 1940": {
        "a": 6378245.000,
        "b": 6356863.01880
    },

    "Mercury 1960": {
        "a": 6378166.000,
        "b": 6356784.283666
    },

    "Mercury Modificado 1968": {
        "a": 6378150.000,
        "b": 6356768.337303
    },

    "Nuevo International 1967": {
        "a": 6378157.500,
        "b": 6356772.200
    },

    "Sudamericano 1969": {
        "a": 6378160.000,
        "b": 6356774.720
    },

    "Walbeck 1817": {
        "a": 6376896.000,
        "b": 6355834.84670
    },

    "WGS66": {
        "a": 6378145.000,
        "b": 6356759.769356
    },

    "WGS72": {
        "a": 6378135.000,
        "b": 6356750.519915
    },

    "WGS84": {
        "a": 6378137.000,
        "b": 6356752.314245
    }
}


# ============================================================
# FUNCIÓN 1: CALCULAR PARÁMETROS DEL ELIPSOIDE
# ============================================================

def calcular_parametros(a, b):

    if a <= 0 or b <= 0 or a <= b:
        raise ValueError("Los valores del elipsoide no son válidos.")

    # Primera excentricidad al cuadrado
    e2 = (a**2 - b**2) / a**2

    # Segunda excentricidad al cuadrado
    e_prime2 = (a**2 - b**2) / b**2

    # Parámetro c utilizado en el Excel
    c = a**2 / b

    return {
        "a": a,
        "b": b,
        "e2": e2,
        "e_prime2": e_prime2,
        "c": c
    }


# ============================================================
# FUNCIÓN 2: OBTENER LOS DATOS DE UN ELIPSOIDE
# ============================================================

def obtener_parametros(nombre):

    if nombre not in ELIPSOIDES:
        raise ValueError("El elipsoide seleccionado no existe.")

    datos = ELIPSOIDES[nombre]

    parametros = calcular_parametros(
        datos["a"],
        datos["b"]
    )

    parametros["nombre"] = nombre

    return parametros


# ============================================================
# FUNCIÓN 3: LISTAR LOS ELIPSOIDES DISPONIBLES
# ============================================================

def listar_elipsoides():

    return list(ELIPSOIDES.keys())


# ============================================================
# PRUEBA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("====================================")
    print("          GEOARCOS")
    print("       CATÁLOGO DE ELIPSOIDES")
    print("====================================")

    print("\nElipsoides disponibles:")

    for numero, nombre in enumerate(listar_elipsoides(), start=1):
        print(numero, "-", nombre)

    print("\nPRUEBA DE CÁLCULO: GRS80")

    resultado = obtener_parametros("GRS80")

    for parametro, valor in resultado.items():
        print(f"{parametro}: {valor}")

    print("\nMódulo ejecutado correctamente.")
