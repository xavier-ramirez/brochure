# -*- coding: utf-8 -*-
"""Todo el contenido del brochure. Editar aqui los textos; el diseno vive en generar.py."""

EMPRESA = dict(
    tagline_portada=['Diseño', 'Ingeniería', 'Obras'],
    titular_portada='Construyendo la infraestructura<br>que mueve el país',
    entrada_portada=('<b>CONSTRUCTORA VIDALSA 27 C.A.</b> es una empresa venezolana fundada en el año 2007, '
                     'desde entonces sumamos años de trayectoria en la construcción de infraestructura civil '
                     'y petrolera, con enfoque en la Faja Petrolífera del Orinoco.'),
    titular_cierre='La fuerza que construye<br>nuestra industria petrolera',
    sello='2007 — 2026  ·  19 años de trayectoria',
    elaborado='Elaborado por Fernando Sánchez  ·  Ingeniero Industrial',
)

#: La direccion de Caracas se escribe UNA vez: la usan el pie de contacto del
#: cierre -aqui debajo- y la tarjeta de Caracas de la lamina de oficinas. Sin
#: la ciudad al final, que cada sitio la pone a su manera: el pie la remata
#: con " — Caracas." y en la tarjeta la ciudad ya va en el chip de la foto.
DIR_CARACAS = ('Calle París entre New York y Caroní, Edif.&nbsp;#177, '
               'Urb.&nbsp;Las&nbsp;Mercedes, Municipio Baruta, Edo. Miranda')

CONTACTO = [
    # SIN <br>: los saltos los decide el ANCHO de la columna, que no es el mismo
    # en las dos hojas. Con los saltos escritos a mano, la hoja que no fuera la
    # de referencia partia la direccion donde no tocaba y encima volvia a
    # partir cada trozo por su cuenta. El texto no cambia ni una coma.
    #
    # Los &nbsp; de "Urb. Las Mercedes" y "Edif. #177" son espacios que NO dejan
    # partir: sueltos, el renglon cortaba en "Urb. / Las Mercedes" y podia dejar
    # el numero del edificio en la linea siguiente, huerfano de su "Edif.".
    # Atados, el corte se va solo a una coma, que es donde lo haria uno a mano.
    # Siguen siendo espacios normales al leerlos.
    # El edificio se nombraba "Edf. Pedreañera #177"; el usuario quito el nombre
    # propio y queda el numeral con el numero.
    ('Sede corporativa', DIR_CARACAS + ' — Caracas.'),
    ('Sede operativa',   'Lechería, estado Anzoátegui.'),
]

#: LAS OFICINAS (lamina "Nuestras oficinas"). Una foto por ciudad; el nombre de
#: la foto es el que usa el editor, asi que el usuario las cambia con doble
#: clic sin tocar nada de aqui. La de El Tigre ya es la de verdad -el patio con
#: la gente y la flota-; las otras tres siguen siendo un marcador de posicion,
#: a la espera de las suyas.
#:
#: Las direcciones de los dos centros operativos salen del propio sistema de la
#: empresa (tabla frentes_trabajo, frentes "PATIO I EL TIGRE" y "PATIO
#: MATURIN", los dos clasificados alli como RESGUARDO). Los puntos de
#: referencia -la Finca La Valentina en El Tigre, la Urb. Sabana Club en
#: Maturin- los dio el usuario, que es como se dan las direcciones alli. Van
#: escritos como "adyacente a" y no como "al lado de": lo pidio el 2026-09-04
#: para que la direccion se lea igual de formal que las otras dos.
#:
#: La sede de Oriente estuvo un tiempo puesta en BARCELONA, hasta que el
#: usuario aclaro que esta en LECHERIA -que es ademas lo que decia ya el pie de
#: contacto del cierre (CONTACTO), asi que las dos partes del brochure vuelven
#: a decir lo mismo-. Su direccion la dio el, no el sistema: alli ese frente
#: sigue "POR DEFINIR".
#:
#: Con 'dir' vacio el bloque sale sin esa linea, no rota.
#:
#: 'tipo' es el rotulo de la sede que va detras del nombre, dentro de la
#: pildora gris. Se escribe TAL CUAL sale impreso -mayuscula en cada palabra,
#: "Sede Administrativa Oriente", que es como lo pidio el usuario- y ya no
#: pasa por epigrafe() ni por espaciada(), que son las piezas que lo ponian entero en
#: versalita ("SEDE CORPORATIVA"), que es lo que no queria.
OFICINAS = [
    dict(foto='oficina_caracas',   ciudad='Caracas', tipo='Sede Corporativa',
         dir=DIR_CARACAS + '.'),
    dict(foto='oficina_lecheria',  ciudad='Lechería', tipo='Sede Administrativa Oriente',
         dir='Avenida Intercomunal, entre el Banco Venezolano de Crédito y el '
             'Centro Médico Meditotal, planta baja del Spa Hotel, '
             'estado Anzoátegui.'),
    dict(foto='oficina_eltigre',   ciudad='El Tigre', tipo='Centro Operativo',
         dir='Patio de máquinas. Avenida La Bomba, adyacente a la Finca '
             'La Valentina, municipio Simón Rodríguez, estado Anzoátegui.'),
    dict(foto='oficina_maturin',   ciudad='Maturín', tipo='Centro Operativo',
         dir='Patio de máquinas. Vía El Rincón de Monagas, adyacente a la '
             'Urb. Sabana Club, municipio Maturín, estado Monagas.'),
]

# Telefono y correo van APARTE de CONTACTO, no mezclados en la misma lista:
# son los dos datos de contacto DIRECTO, y cada uno lleva su propio rotulo -no
# un parrafo partido a mano con <br>-. lamina_cierre() los junta en un solo
# bloque, .ct-directo, que la CSS reparte distinto segun la hoja: en la
# panoramica, uno al lado del otro, como una columna mas; en la carta, uno
# debajo del otro, porque ahi no cabe una cuarta columna (ver .ct-directo en
# estilos.css y carta.css).
CONTACTO_DIRECTO = [
    ('Teléfono', '+58 212 994.1106 / 1253 / 0987 / 0730'),
    ('Correo',   'Info@cvidalsa27.com'),
]

# Dos, no tres: el usuario quito el Objetivo -decia lo mismo que la Vision con
# otras palabras-. La lamina no lleva el numero escrito en ningun sitio: la
# rejilla .pilares reparte las columnas segun cuantas haya, asi que anadir o
# quitar un pilar aqui es todo lo que hay que tocar.
PILARES = [
    ('01', 'Misión',   'Desarrollar proyectos de infraestructura civil y petrolera, mediante soluciones '
                       'constructivas, innovadoras y sostenibles.'),
    ('02', 'Visión',   'Ser el referente líder en la ejecución de proyectos de infraestructura, reconocidos '
                       'por transformar desafíos complejos en proyectos tangibles, seguros, de alta calidad y '
                       'con compromiso socioambiental, que impulsen el desarrollo económico y social del país.'),
]

VALORES = dict(
    # 'Quienes somos', no 'Nuestra cultura': decia casi lo mismo que el
    # titulo grande de al lado, 'Nuestros valores'. Es el mismo rotulo que
    # ya llevan las otras tres laminas de esta seccion -Nuestra empresa,
    # Mision y vision-, asi que de paso queda igual de familia con ellas.
    epigrafe='Quiénes somos',
    titulo='Nuestros valores',
    texto=('En Constructora Vidalsa27, C.A. construimos con propósito. Estos son los principios que guían '
           'nuestra conducta y nuestro compromiso social:'),
    items=[
        ('01', 'Seguridad', 'Cuidamos a nuestra gente y a nuestros clientes. La protección en cada frente de '
                            'trabajo no es negociable.'),
        ('02', 'Integridad', 'Ética y honestidad de principio a fin. Cultivamos relaciones sólidas basadas en '
                             'la confianza.'),
        ('03', 'Eficiencia', 'Respetamos tu tiempo y tu inversión. Optimizamos recursos para cumplir '
                             'compromisos sin margen de demora.'),
        ('04', 'Innovación', 'Evolución constante. Buscamos estar siempre un paso adelante en metodologías y '
                             'visión de negocio.'),
        ('05', 'Compromiso Ambiental', 'Construimos el futuro sin comprometer el presente, diseñando procesos '
                                       'respetuosos con el entorno, salvaguardando el ambiente para las '
                                       'generaciones futuras.'),
    ],
)

# Los cuatro titulos van en MAYUSCULA INICIAL palabra por palabra -lo pidio
# el usuario el 2026-09-04: los ve mas elegantes asi-. Las palabras de
# enlace -"y", "de"- se quedan en minuscula, que es como se titula en
# castellano; en versalita no se notarian, pero estos titulos salen tal cual
# se escriben aqui.
SERVICIOS = [
    ('01', 'Construcción de Ductos Petroleros', [
        'Soldadura de 3/4″ a 42″ calificada',
        'Tubería enterrada y superficial',
        'Revestimiento y protección de tuberías',
        'Ingeniería, topografía y excavación',
        'Prueba hidrostática y flushing']),
    ('02', 'Servicios de Alquiler de Equipos', [
        'Maquinaria pesada y liviana',
        'Izamiento e instalación de equipos',
        'Chuto/batea y lowboy con escoltas',
        'Vacuum y brazo hidráulico',
        'Cortafuegos y estaciones de válvulas']),
    ('03', 'Ambiente y Saneamiento', [
        'Saneamiento de áreas por afectaciones con derrame de crudo',
        'Trasegado con vacuum',
        'Tratamiento y disposición de suelo',
        'Saneamiento de lagunas a través del dragado de sólidos']),
    ('04', 'Suministro y Procura', [
        'Válvulas bridadas de compuerta y globo',
        'Bridas, codos, te y reducciones',
        'Weldolets, niples y tapones',
        'Empacaduras y espárragos',
        'Mangas y revestimientos']),
]

GERENCIAS = [
    'Gerencia de Proyectos Mayores de Producción FPO',
    'Gerencia de Distribución y Transporte Faja',
    'Gerencia de Logística Operacional DAL FPO',
    'Gerencia de Gestión de Materiales DAL-FPO',
    'Gerencia de Tratamiento y Calidad de Fluidos TCF',
    'Gerencia de Perforación',
    'Coordinación Operacional Faja COF',
]

PORTAFOLIO = dict(
    # None = se pone la fecha del dia en que corres generar.py.
    # Para congelarla, escribe aqui el texto, p. ej. 'Agosto de 2026'.
    fecha=None,
    rotulo='Actualizado al',
)

FLOTA = dict(
    epigrafe='Flota propia',
    titulo='Una flota que no para de crecer',
    texto=('Respaldamos cada obra con una flota 100% propia y en constante expansión. '
           'Tras la exitosa incorporación de equipos en 2025, este 2026 sumaremos nueva '
           'maquinaria para seguir garantizando total autonomía en los proyectos más '
           'exigentes.'),
    pie='Cifras tomadas del sistema de gestión de flota de Vidalsa 27.',
    # las 4 fotos son img/flota_1.jpg ... flota_4.jpg (cambiables desde el editor)
)

# (nombre, subtitulo, archivo del logotipo en img/)
CARTERA = [
    ('PDVSA',        'Petróleos de Venezuela, S.A.', 'logo_pdvsa'),
    ('PETROMONAGAS', 'Empresa mixta',                'logo_petromonagas'),
    ('SINOVENSA',    'Empresa mixta',                'logo_sinovensa'),
]

AREAS = [('construccion', 'Construcción'), ('ambiente', 'Ambiente'), ('servicios', 'Servicios y alquiler')]

# orden = orden en que salen las laminas de proyecto (2 por lamina)
PROYECTOS = [
 dict(id='oleo30x17', area='construccion', anio='2025', estado='Culminado',
   lista='Oleoducto 30″ × 17 km — Planta PDD – COPEM',
   titulo='Oleoducto 30″ × 17 km',
   sub='Planta PDD – Rebombeo El Aceital',
   texto='Construcción de las obras civiles, mecánicas, eléctricas e instrumentación del Oleoducto de 30″ × 17 km, '
         'desde la Planta Desaladora Deshidratadora PDD hasta el rebombeo El Aceital, Morichal, estado Monagas. '
         'Además de la aplicación y puesta en funcionamiento del sistema de protección catódica.',
   cliente='Proyectos Mayores FPO'),

 dict(id='oleo42', area='construccion', anio='2025 – 2026', estado='Culminado',
   lista='Completación mecánica Oleoducto de 42″ — PTO–TAEJ',
   titulo='Oleoducto de 42″',
   sub='PTO – TAEJ · Completación mecánica',
   texto='Completación mecánica de la tubería de 42″ desde el Patio de Tanques Oficina (PTO) hasta el Terminal de '
         'Almacenamiento y Embarque Jose (TAEJ), así como la construcción de 07 tanquillas de concreto en válvulas '
         'de retención de 42″.',
   cliente='Proyectos Mayores FPO'),

 dict(id='oleo30x14', area='construccion', anio='2025 – 2026', estado='Culminado',
   lista='Oleoducto 30″ × 14 km — Planta FF–Trampa de envío',
   titulo='Oleoducto 30″ × 14 km',
   sub='Planta FF – Trampa de envío · PETROLERA SINOVENSA',
   texto='Construcción del Oleoducto de 30″ × 14 km desde la Estación de Flujo (FF) hasta el Km 0, PETROLERA '
         'SINOVENSA, necesarios para incrementar la producción desde 105 MBPD hasta 330 MBPD de crudo extrapesado. '
         'Así como la instalación y puesta en marcha del sistema de protección catódica.',
   cliente='PETROLERA SINOVENSA'),

 dict(id='tub12', area='construccion', anio='2026', estado='En ejecución',
   lista='Tubería 12″ agua salada × 29,6 km — COPEM – El Salto',
   titulo='Tubería 12″ × 29,6 km — agua salada',
   sub='COPEM – Pozos inyectores El Salto',
   texto='Construcción de 29,60 km de tubería de 12″ de inyección de agua salada desde COPEM PETROMONAGAS hasta los '
         'pozos inyectores El Salto. Así como la instalación y puesta en marcha del sistema de protección catódica '
         'de tuberías enterradas.',
   cliente='Proyectos Mayores FPO'),

 dict(id='veladero', area='construccion', anio='2026', estado='En ejecución',
   lista='Oleoducto 30″ Veladero · Tramo I (5,9 km)',
   titulo='Oleoducto 30″ × 5,90 km',
   sub='Tramo I del Oleoducto de 30″ Veladero',
   texto='Reemplazo del Tramo I del Oleoducto de 30″ × 5,9 km, a fin de garantizar la confiabilidad y continuidad '
         'operacional, así como la integridad mecánica del oleoducto de 30″, en el cumplimiento del transporte de '
         'Diluente Mesa 30 para la División Carabobo, Distrito Morichal y empresas mixtas, y la formulación de la '
         'segregación Merey 16.',
   cliente='Coordinación Operacional Faja (COF)'),

 dict(id='diluen20', area='construccion', anio='2023', estado='Culminado',
   lista='Diluenducto 20″ × 11,20 km — Palmichal–PTO',
   titulo='Diluenducto 20″ × 11,20 km',
   sub='Palmichal – Patio de Tanques Oficina · El Tigre, Anzoátegui',
   texto='Reemplazo de 10,5 km del Diluenducto de 20″ Palmichal – PTO, con perforación direccional bajo suelo en la '
         'Troncal 9 de la autopista Gran Mariscal de Ayacucho, con el propósito de restablecer la integridad del '
         'sistema de transporte e incrementar la presión de bombeo hasta 840 psi, permitiendo el manejo de nafta con '
         'un caudal promedio de 180 MBD de diluente.',
   cliente='Proyectos Mayores FPO'),

 dict(id='macolla15', area='construccion', anio='2024 – 2025', estado='Culminado',
   lista='Macolla 15 — vialidad y plataforma',
   titulo='Macolla 15 — vialidad y plataforma',
   sub='Centro Operativo PETROMONAGAS (COPEM)',
   texto='Construcción de la vialidad de acceso y plataforma de perforación para la Macolla 15 del Centro Operativo '
         'PETROMONAGAS, involucrando movimientos de tierra, conformación de taludes, construcción de 39 cellars y '
         'canales de drenaje perimetrales con pases reforzados.',
   cliente='PETROMONAGAS'),

 dict(id='valvulas', area='servicios', anio='2025 – 2026', estado='En ejecución',
   lista='Estaciones de válvulas — FPO HC',
   titulo='Estaciones de válvulas — FPO HC',
   sub='Corredores de tuberías principales de la Faja Petrolífera del Orinoco',
   texto='Limpieza y mantenimiento de estaciones de válvulas en corredores de tuberías, cortafuegos perimetrales, '
         'señalización de áreas y pintura de puentes y estructuras metálicas.',
   cliente='Logística Operacional DAL'),

 dict(id='comorsuelo', area='ambiente', anio='2024 – 2026', estado='Culminado',
   lista='COMOR — Saneamiento de suelo contaminado',
   titulo='COMOR — Saneamiento de suelo contaminado',
   sub='Centro Operativo Morichal · fases II, III y IV',
   texto='Remoción, recolección y recuperación de crudo sobrenadante, así como la carga, transporte, tratamiento y '
         'disposición final del suelo contaminado en instalaciones de PDVSA autorizadas por el MINEC, generado en '
         'las actividades de saneamiento realizadas en el Centro Operativo de Morichal (COMOR), División Carabobo.',
   cliente='Logística Operacional DAL'),

 dict(id='dragado', area='ambiente', anio='2025 – 2026', estado='Culminado',
   lista='Dragado SIAE COMOR — lagunas A, B, C y D',
   titulo='Dragado lagunas del SIAE COMOR',
   sub='Lagunas A, B, C y D del SIAE',
   texto='Saneamiento y posterior mantenimiento de las cuatro lagunas A, B, C y D del SIAE del Centro Operacional '
         'Morichal (COMOR), en la División Carabobo, a través del dragado de sólidos.',
   cliente='Logística Operacional DAL'),

 dict(id='trasegado', area='ambiente', anio='2025 – 2026', estado='En ejecución',
   lista='Movilización y trasegado de crudo — COMOR',
   titulo='Movilización y trasegado de crudo',
   sub='Centro Operativo Morichal',
   texto='Movilización y trasegado de crudo en el Sistema de Inyección y Efluentes (SIAE) ubicado en las '
         'instalaciones del Centro Operativo COMOR, con equipos de vacío tipo vacuum de mínimo 160 BLS.',
   cliente='Logística Operacional DAL'),

 dict(id='ef016', area='ambiente', anio='2025', estado='Culminado',
   lista='Saneamiento Estación de Flujo O-16',
   titulo='Estación de Flujo O-16',
   sub='Saneamiento O-16 · División Carabobo',
   texto='Operación de maquinaria pesada para realizar los trabajos de saneamiento de áreas afectadas por derrames '
         'de hidrocarburos: remoción, estabilización, homogeneización, apilamiento y tratamiento in situ del '
         'material impactado, contención y recolección de fluidos petrolizados, nivelación de terreno y carga de '
         'sólidos.',
   cliente='Logística Operacional DAL'),

 dict(id='transv', area='servicios', anio='2024 – 2026', estado='En ejecución',
   lista='Equipos transversales',
   titulo='Equipos transversales',
   sub='Equipos para la producción de la FPO',
   texto='Servicio de movimientos relacionados con remoción de suelos, carga, descarga y traslado de materiales '
         'logísticos y misceláneos, contemplados en las operaciones de rehabilitación y reacondicionamiento de '
         'pozos, subestaciones eléctricas, estaciones de flujo y descarga, asociados a las labores operacionales de '
         'las divisiones pertenecientes a la Dirección Ejecutiva de Producción FPO.',
   cliente='Logística Operacional DAL'),

 dict(id='chuto', area='servicios', anio='2024 – 2027', estado='En ejecución',
   lista='Chuto con batea',
   titulo='Chuto con batea',
   sub='Movilización de equipos y materiales de la FPO',
   texto='Movilización de todos los materiales y equipos (transformadores, generadores, plantas), misceláneos y '
         'lubricantes, desde las instalaciones PDVSA a nivel nacional hasta las áreas operacionales de las '
         'divisiones Carabobo, Ayacucho, Junín y Boyacá, adscritas a la Dirección Adjunta de Logística perteneciente '
         'a la Dirección Ejecutiva de Producción FPO HC.',
   cliente='Logística Operacional DAL'),

 dict(id='bombeo', area='servicios', anio='2025', estado='Culminado',
   lista='Mantenimiento de equipos de bombeo — FPO',
   titulo='Mantenimiento de equipos de bombeo',
   sub='Áreas operacionales de la Faja Petrolífera del Orinoco',
   texto='Reparación de bombas marca Bornemann, Warren, Sulzer y Flowserve, utilizadas para el transporte de fluidos '
         'en superficie y ubicadas en instalaciones pertenecientes a la Faja Petrolífera del Orinoco.',
   cliente='Gestión de Materiales DAL'),

 dict(id='sinovensa', area='servicios', anio='2025 – 2026', estado='Culminado',
   lista='Alquiler de maquinaria — SINOVENSA Morichal',
   titulo='Alquiler de maquinaria — SINOVENSA',
   sub='Activación de pozos, División Carabobo',
   texto='Servicios de maquinaria pesada para realizar actividades operacionales que contribuyan con la activación '
         'de pozos en la División Carabobo.',
   cliente='PETROLERA SINOVENSA'),

 dict(id='cortafuego', area='servicios', anio='2025 – 2026', estado='En ejecución',
   lista='Cortafuegos en corredores de tuberías',
   titulo='Cortafuegos en corredores de tuberías',
   sub='Divisiones FPO',
   texto='Construcción y mantenimiento de cortafuegos en corredores de tubería y líneas eléctricas de oleoductos y '
         'diluenductos de la Faja. Incluyendo corrección de filtraciones por soldadura y encapsulamiento de grampas '
         'apernadas.',
   cliente='Logística Operacional DAL'),

 dict(id='xpmorichal', area='servicios', anio='2025 – 2027', estado='En ejecución',
   lista='Alquiler de equipos — XP Extrapesado Morichal',
   titulo='Alquiler de equipos — XP Morichal',
   sub='Unidad de Producción Extrapesado, Distrito Morichal',
   texto='Servicios para acondicionamiento y adecuación de vías de acceso y locaciones, los cuales son '
         'indispensables para el óptimo funcionamiento y operación de las unidades de producción de la División '
         'Carabobo.',
   cliente='Logística Operacional DAL'),

 dict(id='curataqui', area='ambiente', anio='2024', estado='Culminado',
   lista='Saneamiento Laguna de Curataquiche',
   titulo='Laguna de Curataquiche',
   sub='Saneamiento y restauración ambiental',
   texto='Saneamiento y restauración de la Laguna de Curataquiche, progresiva 15+000 del Oleoducto de 36″, '
         'desarrollando actividades de remoción de capa de hidrocarburos con barreras oleofílicas y material '
         'particulado; estabilización mecánica, carga y transporte del material contaminado; reforestación del área, '
         'toma y análisis de muestras en la laguna, ejecutadas en las diferentes fases del proceso de saneamiento.',
   cliente='Logística Operacional DAL'),
]
