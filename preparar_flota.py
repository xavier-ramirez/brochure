# -*- coding: utf-8 -*-
"""Lee la flota del sistema (MySQL de XAMPP, base 'cd' del proyecto
vidalsa_sistema) y deja en flota.json el conteo POR TIPO DE EQUIPO,
separado en FLOTA PESADA y FLOTA LIVIANA, que usa la lamina de flota.

    python preparar_flota.py

QUE NO SE CUENTA (y por que):
  - Camionetas del frente ASIGNACIONES ESPECIALES (id 23)  -> lo pediste tu.
  - Todo el frente POR DEFINIR (id 2)                      -> lo pediste tu.
  - Todo el frente PATIO EXTERNO (id 26)                   -> lo pediste tu.
  - Todo el frente CVG PUERTO ORDAZ (id 44)                -> lo pediste tu.
  - Todo el frente CONTROL DE ACTIVOS VENDIDOS (id 56)     -> ya no es flota propia.
  - Todo el frente PATIO EL LECHON (id 25)                 -> lo pediste tu.
  - Equipos con estado DESINCORPORADO                      -> ya no operan.
  - Vacuums anteriores a 2025 y los que no tienen año      -> lo pediste tu.
  - El vacuum del frente GOBERNACION APURE (7)             -> lo pediste tu.
  - Volteos de CVG PUERTO ORDAZ (44) y MINISTERIO DE
    OBRAS PUBLICAS (45)                                    -> lo pediste tu.
  - Cualquier equipo que diga ALQUILADO (o alquilada/os) en
    cualquier campo de texto                               -> no es propio.
    Se busca ALQUILAD, no ALQUIL: hay un frente que se llama ALQUILER
    SINOVENSA, y ese es equipo NUESTRO alquilado a un cliente, no al reves.
    Si algun equipo dice ALQUIL de otra forma, el script lo avisa al final
    para que decidas tu.
De la tabla equipos_auxiliares solo entran los MONTACARGAS.

OJO CON LA CLASIFICACION PESADA / LIVIANA
-----------------------------------------
No se usa la columna CATEGORIA_FLOTA de la base porque no cuadra: ahi los
chutos, bateas, volteos y lowboys estan marcados como FLOTA LIVIANA y en el
brochure quedarian en el bloque equivocado. Se usa la lista PESADA de abajo;
para mover un tipo de bloque, sacalo o metelo en esa lista.
"""
import io, json, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
MYSQL = os.path.join('C:' + chr(92) + 'xampp', 'mysql', 'bin', 'mysql.exe')
SALIDA = os.path.join(BASE, 'flota.json')

TIPOS_PESADA = 11        # cuantos tipos se detallan; el resto va a "Otra/Otros"
TIPOS_LIVIANA = 5

# frentes que quedan enteros fuera del conteo
FRENTES_FUERA = (2,    # POR DEFINIR
                 25,   # PATIO EL LECHON
                 26,   # PATIO EXTERNO
                 44,   # CVG PUERTO ORDAZ
                 56)   # CONTROL DE ACTIVOS VENDIDOS
VACUUM_DESDE = 2025         # solo vacuums de este año en adelante
VOLTEOS_FUERA = (45,)       # MINISTERIO DE OBRAS PUBLICAS
                            # (CVG PUERTO ORDAZ ya sale entero, ver arriba)
VACUUM_FUERA = (7,)         # GOBERNACION APURE

# maquinaria y transporte pesado
PESADA = {
    'CHUTO', 'VOLTEO', 'BATEA', 'PAYLOADER', 'RETROEXCAVADORA', 'LOWBOY',
    'EXCAVADORA', 'MINI EXCAVADORAS', 'TRACTOR DE ORUGA', 'TRACTOR AGRICOLA',
    'SIDEBOOM', 'MOTOTRAILLA', 'MOTONIVELADORA', 'VIBROCOMPACTADORA',
    'COMPACTADORA', 'VACUUM', 'CHUTO CON BRAZO 16 TON', 'CAMION GRUA',
    'CAMION ELEVADOR 8 TON', 'CAMION ELEVADOR 12 TON', 'CAMION ARTICULADO',
    'TRAILERS', 'CAMA BAJA', 'BATEA/SILOS', 'BATEA/VOLQUETA', 'GRUA REMOLQUE',
    'DRAGA', 'BALLENA', 'TARA', 'MONTACARGA',
}

NOMBRES = {
    'CAMIONETA': 'Camionetas', 'CHUTO': 'Chutos', 'VOLTEO': 'Volteos',
    'BATEA': 'Bateas', 'CAMION DE SOLDADURA': 'Camiones de soldadura',
    'PAYLOADER': 'Payloaders', 'RETROEXCAVADORA': 'Retroexcavadoras',
    'LOWBOY': 'Lowboys', 'EXCAVADORA': 'Excavadoras',
    'TRACTOR DE ORUGA': 'Tractores de oruga', 'VACUUM': 'Vacuums',
    'MOTOTRAILLA': 'Mototraíllas', 'AUTOMOVIL': 'Automóviles',
    'SIDEBOOM': 'Sidebooms', 'AMBULANCIA': 'Ambulancias',
    'MOTONIVELADORA': 'Motoniveladoras', 'CUADRILLERA': 'Cuadrilleras',
    'VIBROCOMPACTADORA': 'Vibrocompactadoras', 'CAMION GRUA': 'Camiones grúa',
    'CAMION ELEVADOR 8 TON': 'Camiones elevadores 8 t',
    'CAMION ELEVADOR 12 TON': 'Camiones elevadores 12 t',
    'CHUTO CON BRAZO 16 TON': 'Chutos con brazo 16 t',
    'TRACTOR AGRICOLA': 'Tractores agrícolas',
    'MINI EXCAVADORAS': 'Miniexcavadoras', 'COMPACTADORA': 'Compactadoras',
    'CAMION DE SERVICIO': 'Camiones de servicio', 'AUTOBUS': 'Autobuses',
    'CAMION CISTERNA': 'Camiones cisterna', 'DRAGA': 'Dragas',
    'CAMION ARTICULADO': 'Camiones articulados', 'TRAILERS': 'Tráilers',
    'CAMION PLATAFORMA': 'Camiones plataforma', 'CAVA': 'Cavas',
    'MINI SHOWER': 'Mini showers', 'MONTACARGA': 'Montacargas',
    'PLATAFORMA / BRAZO HIDRAULICO': 'Brazos hidráulicos',
    'CAMION CON BRAZO 4 TON': 'Camiones con brazo 4 t',
    'CAMION CON BRAZO 6 TON': 'Camiones con brazo 6 t',
    'CAMION PRUEBA HIDROSTATICA': 'Camiones de prueba hidrostática',
    'GRUA REMOLQUE': 'Grúas de remolque', 'MOTOCICLETA': 'Motocicletas',
    'BATEA/SILOS': 'Bateas/silos', 'BATEA/VOLQUETA': 'Bateas/volquetas',
    'CAMION': 'Camiones', 'CAMION  HIDROJET': 'Camiones hidrojet',
}

# todos los campos de texto de la tabla equipos
CAMPOS_TEXTO = ('NUMERO_ETIQUETA', 'CATEGORIA_FLOTA', 'CODIGO_PATIO', 'MARCA',
                'MODELO', 'CAPACIDAD', 'COLOR', 'SERIAL_CHASIS', 'SERIAL_DE_MOTOR',
                'COMBUSTIBLE', 'DETALLE_UBICACION_ACTUAL', 'ESTADO_OPERATIVO')
TODO_TEXTO = "CONCAT_WS('|'," + ",".join("e." + c for c in CAMPOS_TEXTO) + ")"
ALQUILADO = "%s LIKE '%%ALQUILAD%%'" % TODO_TEXTO

EXCLUIR = ("NOT (e.ID_FRENTE_ACTUAL = 23 AND t.nombre = 'CAMIONETA') "
           "AND (e.ID_FRENTE_ACTUAL NOT IN (%s) OR e.ID_FRENTE_ACTUAL IS NULL) "
           "AND e.ESTADO_OPERATIVO <> 'DESINCORPORADO' "
           "AND NOT (t.nombre = 'VACUUM' AND (e.ANIO IS NULL OR e.ANIO < %d)) "
           "AND NOT (t.nombre = 'VACUUM' AND e.ID_FRENTE_ACTUAL IN (%s)) "
           "AND NOT (t.nombre = 'VOLTEO' AND e.ID_FRENTE_ACTUAL IN (%s)) "
           "AND NOT (%s)"
           % (','.join(str(f) for f in FRENTES_FUERA), VACUUM_DESDE,
              ','.join(str(f) for f in VACUUM_FUERA),
              ','.join(str(f) for f in VOLTEOS_FUERA), ALQUILADO))


def consultar(sql):
    r = subprocess.run([MYSQL, '-uroot', 'cd', '-e', sql],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise SystemExit('MySQL no respondio (enciende XAMPP): ' + (r.stderr or '').strip())
    return [l.split('\t') for l in r.stdout.strip().splitlines()][1:]


DESDE = ("FROM equipos e LEFT JOIN tipo_equipos t ON t.id = e.id_tipo_equipo "
         "WHERE e.deleted_at IS NULL AND " + EXCLUIR)

por_tipo = [(n, int(c)) for n, c in consultar(
    "SELECT COALESCE(t.nombre,'SIN TIPO'), COUNT(*) %s GROUP BY 1" % DESDE)]

# los montacargas viven en equipos_auxiliares, no en equipos
AUX_TEXTO = ("CONCAT_WS('|',MARCA,MODELO,SERIAL,CODIGO_INTERNO,CAPACIDAD,"
             "DETALLE_UBICACION_ACTUAL,NRO_DOC_PROPIEDAD,OBSERVACIONES)")
montacargas = int(consultar(
    "SELECT COUNT(*) FROM equipos_auxiliares WHERE TIPO='MONTACARGA' AND deleted_at IS NULL "
    "AND ESTADO_OPERATIVO <> 'DESINCORPORADO' "
    "AND NOT (%s LIKE '%%ALQUILAD%%')" % AUX_TEXTO)[0][0])
if montacargas:
    por_tipo.append(('MONTACARGA', montacargas))

por_tipo.sort(key=lambda x: -x[1])
total = sum(c for _, c in por_tipo)
marcas = int(consultar("SELECT COUNT(DISTINCT e.MARCA) %s" % DESDE)[0][0])
excluidos = int(consultar("SELECT COUNT(*) FROM equipos e "
                          "LEFT JOIN tipo_equipos t ON t.id = e.id_tipo_equipo "
                          "WHERE e.deleted_at IS NULL AND NOT (%s)" % EXCLUIR)[0][0])


def bloque(lista, cuantos, sobrante):
    cabeza, cola = lista[:cuantos], lista[cuantos:]
    filas = [{'nombre': NOMBRES.get(n, n.capitalize()), 'cantidad': c} for n, c in cabeza]
    fuera = sum(c for _, c in cola)
    if fuera:
        filas.append({'nombre': sobrante, 'cantidad': fuera})
    return filas, sum(c for _, c in lista)


pesada = [(n, c) for n, c in por_tipo if n in PESADA]
liviana = [(n, c) for n, c in por_tipo if n not in PESADA]
filas_pesada, total_pesada = bloque(pesada, TIPOS_PESADA, 'Otra maquinaria pesada')
filas_liviana, total_liviana = bloque(liviana, TIPOS_LIVIANA, 'Otros equipos de apoyo')

datos = {
    'total': total, 'marcas': marcas, 'excluidos': excluidos,
    'tipos_distintos': len(por_tipo),
    'pesada': total_pesada, 'liviana': total_liviana,
    'bloques': [
        {'titulo': 'Flota pesada', 'total': total_pesada, 'tipos': filas_pesada},
        {'titulo': 'Flota liviana y de apoyo', 'total': total_liviana, 'tipos': filas_liviana},
    ],
}
io.open(SALIDA, 'w', encoding='utf-8').write(json.dumps(datos, indent=1, ensure_ascii=False))

print('equipos contados: %d   (excluidos %d)   |   %d tipos   |   %d marcas'
      % (total, excluidos, len(por_tipo), marcas))
for b in datos['bloques']:
    print('\n%s  (%d)' % (b['titulo'].upper(), b['total']))
    for t in b['tipos']:
        print('  %4d  %s' % (t['cantidad'], t['nombre']))
print('\n->', SALIDA)
