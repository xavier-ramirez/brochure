# -*- coding: utf-8 -*-
"""Lee la flota del sistema (MySQL de XAMPP, base 'cd' del proyecto
vidalsa_sistema) y deja en flota.json el conteo POR TIPO DE EQUIPO que usa
la lamina de flota.

    python preparar_flota.py

QUE NO SE CUENTA (y por que):
  - Camionetas del frente ASIGNACIONES ESPECIALES (id 23)  -> lo pediste tu.
  - Todo el frente POR DEFINIR (id 2)                      -> lo pediste tu.
  - Todo el frente CONTROL DE ACTIVOS VENDIDOS (id 56)     -> ya no es flota propia.
  - Equipos con estado DESINCORPORADO                      -> ya no operan.
Tampoco entran los EQUIPOS AUXILIARES: viven en otra tabla (equipos_auxiliares)
y esta consulta solo mira la tabla 'equipos'.
Cambia EXCLUIR de abajo si quieres contarlos.

Si MySQL esta apagado, generar.py sigue usando el ultimo flota.json guardado.
"""
import io, json, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
MYSQL = os.path.join('C:' + chr(92) + 'xampp', 'mysql', 'bin', 'mysql.exe')
SALIDA = os.path.join(BASE, 'flota.json')

TIPOS_EN_LAMINA = 11          # los demas se suman en "Otros equipos"

FRENTES_FUERA = (2, 56)        # POR DEFINIR, CONTROL DE ACTIVOS VENDIDOS

EXCLUIR = ("NOT (e.ID_FRENTE_ACTUAL = 23 AND t.nombre = 'CAMIONETA') "
           "AND (e.ID_FRENTE_ACTUAL NOT IN (%s) OR e.ID_FRENTE_ACTUAL IS NULL) "
           "AND e.ESTADO_OPERATIVO <> 'DESINCORPORADO'"
           % ','.join(str(f) for f in FRENTES_FUERA))

# como se escribe cada tipo en la lamina (la tabla los guarda en mayuscula y sin tildes)
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
}


def consultar(sql):
    r = subprocess.run([MYSQL, '-uroot', 'cd', '-e', sql],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise SystemExit('MySQL no respondio (enciende XAMPP): ' + (r.stderr or '').strip())
    return [l.split('\t') for l in r.stdout.strip().splitlines()][1:]


DESDE = ("FROM equipos e LEFT JOIN tipo_equipos t ON t.id = e.id_tipo_equipo "
         "WHERE e.deleted_at IS NULL AND " + EXCLUIR)

filas = consultar("SELECT COALESCE(t.nombre,'SIN TIPO'), COUNT(*) %s "
                  "GROUP BY 1 ORDER BY 2 DESC" % DESDE)
por_tipo = [(n, int(c)) for n, c in filas]
total = sum(c for _, c in por_tipo)
marcas = int(consultar("SELECT COUNT(DISTINCT e.MARCA) %s" % DESDE)[0][0])
pesada = int(consultar("SELECT COUNT(*) %s AND e.CATEGORIA_FLOTA='FLOTA PESADA'" % DESDE)[0][0])
liviana = int(consultar("SELECT COUNT(*) %s AND e.CATEGORIA_FLOTA='FLOTA LIVIANA'" % DESDE)[0][0])
excluidos = int(consultar("SELECT COUNT(*) FROM equipos e "
                          "LEFT JOIN tipo_equipos t ON t.id = e.id_tipo_equipo "
                          "WHERE e.deleted_at IS NULL AND NOT (%s)" % EXCLUIR)[0][0])

cabeza = por_tipo[:TIPOS_EN_LAMINA]
cola = por_tipo[TIPOS_EN_LAMINA:]
tipos = [{'nombre': NOMBRES.get(n, n.capitalize()), 'cantidad': c} for n, c in cabeza]
if cola:
    tipos.append({'nombre': 'Otros equipos', 'cantidad': sum(c for _, c in cola)})

datos = {'total': total, 'marcas': marcas, 'pesada': pesada, 'liviana': liviana,
         'tipos': tipos, 'excluidos': excluidos,
         'tipos_distintos': len(por_tipo)}
io.open(SALIDA, 'w', encoding='utf-8').write(json.dumps(datos, indent=1, ensure_ascii=False))

print('equipos contados: %d   (excluidos %d)   |   %d tipos distintos   |   %d marcas'
      % (total, excluidos, len(por_tipo), marcas))
print('pesada %d   liviana %d' % (pesada, liviana))
for t in tipos:
    print('  %4d  %s' % (t['cantidad'], t['nombre']))
print('->', SALIDA)
