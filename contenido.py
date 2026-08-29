# -*- coding: utf-8 -*-
"""Todo el contenido del brochure. Editar aqui los textos; el diseno vive en generar.py."""

EMPRESA = dict(
    tagline_portada=['Diseño', 'Ingeniería', 'Obras'],
    tagline_cierre=['Diseño', 'Ingeniería', 'Obras', 'Energía'],
    titular_portada='Construyendo la infraestructura<br>que mueve el país',
    entrada_portada=('Desde 2017, sumamos 9 años de experiencia aportando soluciones integrales a la '
                     'industria civil y petrolera del oriente del país. Nuestro compromiso se mide en '
                     'resultados: obras entregadas con excelencia, operando siempre con flota propia y '
                     'personal altamente calificado.'),
    titular_cierre='La fuerza que construye<br>nuestra industria petrolera',
    sello='2017 — 2026  ·  9 años de excelencia operativa',
    elaborado='Elaborado por Fernando Sánchez  ·  Ingeniero Industrial',
)

CONTACTO = [
    ('Sede corporativa', 'Calle París entre New York y Caroní,<br>Edf. Pedreañera #177, Urb. Las Mercedes,<br>Municipio Baruta, Edo. Miranda — Caracas.'),
    ('Sede operativa',   'Lechería, estado Anzoátegui.'),
    ('Teléfonos',        '+58 212 994.1106 / 1253<br>+58 212 994.0987 / 0730'),
    ('Contacto',         'info@cvidalsa27.com'),
]

PILARES = [
    ('01', 'Misión',   'Ser partícipes en el desarrollo del país a través de la elaboración de proyectos y la '
                       'ejecución de obras civiles, mediante la implementación de los últimos avances e '
                       'innovación en técnicas de ingeniería y procesos de construcción.'),
    ('02', 'Visión',   'Consolidarnos como referente nacional en la construcción de infraestructura civil y '
                       'petrolera, manteniendo excelencia operativa y compromiso socioambiental.'),
    ('03', 'Objetivo', 'Ser referentes en calidad, innovación y satisfacción del cliente durante la próxima '
                       'década, impulsando la transformación del área de construcción civil y petrolera.'),
]

SERVICIOS = [
    ('01', 'Construcción de ductos petroleros', [
        'Soldadura de 3/4″ a 42″ calificada',
        'Tubería enterrada y superficial',
        'Revestimiento y protección de tuberías',
        'Ingeniería, topografía y excavación',
        'Prueba hidrostática y flushing']),
    ('02', 'Servicios de alquiler de equipos', [
        'Maquinaria pesada y liviana',
        'Izamiento e instalación de equipos',
        'Chuto/batea y lowboy con escoltas',
        'Vacuum y brazo hidráulico',
        'Cortafuegos y estaciones de válvulas']),
    ('03', 'Ambiente y saneamiento', [
        'Saneamiento de áreas por afectaciones con derrame de crudo',
        'Trasegado con vacuum',
        'Tratamiento y disposición de suelo',
        'Saneamiento de lagunas a través del dragado de sólidos']),
    ('04', 'Suministro y procura', [
        'Válvulas bridadas de compuerta y globo',
        'Bridas, codos, tes y reducciones',
        'Weldolets, niples y tapones',
        'Empacaduras y espárragos',
        'Mangas y revestimientos']),
]

GERENCIAS = [
    'Gerencia de Proyectos Mayores de Producción FPO',
    'Dirección Adjunta de Logística FPO (DAL)',
    'Gerencia de Distribución y Transporte Faja',
    'Gerencia de Logística Operacional DAL FPO',
    'Gerencia de Gestión de Materiales DAL-FPO',
    'Gerencia de Tratamiento y Calidad de Fluidos (TCF)',
    'Gerencia de Perforación',
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
    texto=('No subcontratamos maquinaria: cada equipo es nuestro, con mantenimiento y '
           'operadores de la casa. Eso nos permite montar un frente completo sin depender '
           'de terceros, y el parque no ha dejado de crecer.'),
    pie='Cifras tomadas del sistema de gestión de flota de Vidalsa 27.',
    # las 4 fotos son img/flota_1.jpg ... flota_4.jpg (cambiables desde el editor)
)

# (nombre, subtitulo, archivo del logotipo en img/)
CARTERA = [
    ('PDVSA',        'Petróleos de Venezuela, S.A.', 'logo_pdvsa'),
    ('Petromonagas', 'Empresa mixta',                'logo_petromonagas'),
    ('Sinovensa',    'Petrolera Sinovensa',          'logo_sinovensa'),
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
   lista='Oleoducto 30″ × 14 km — Planta FF–Km 0',
   titulo='Oleoducto 30″ × 14 km',
   sub='Planta FF – Km 0 · Petrolera Sinovensa',
   texto='Construcción del Oleoducto de 30″ × 14 km desde la Estación de Flujo (FF) hasta el Km 0, Petrolera '
         'Sinovensa, necesarios para incrementar la producción desde 105 MBPD hasta 330 MBPD de crudo extrapesado. '
         'Así como la instalación y puesta en marcha del sistema de protección catódica.',
   cliente='Petrolera Sinovensa'),

 dict(id='tub12', area='construccion', anio='2026', estado='En ejecución',
   lista='Tubería 12″ agua salada × 29,6 km — COPEM – El Salto',
   titulo='Tubería 12″ × 29,6 km — agua salada',
   sub='COPEM – Pozos inyectores El Salto',
   texto='Construcción de 29,60 km de tubería de 12″ de inyección de agua salada desde COPEM Petromonagas hasta los '
         'pozos inyectores El Salto. Así como la instalación y puesta en marcha del sistema de protección catódica '
         'de tuberías enterradas.',
   cliente='Proyectos Mayores FPO'),

 dict(id='diluen20', area='construccion', anio='2023', estado='Culminado',
   lista='Diluenducto 20″ × 11,20 km — Palmichal–PTO',
   titulo='Diluenducto 20″ × 11,20 km',
   sub='Palmichal – Patio de Tanques Oficina · El Tigre, Anzoátegui',
   texto='Reemplazo de 10,5 km del Diluenducto de 20″ Palmichal – PTO, con perforación direccional bajo suelo en la '
         'Troncal 9 de la autopista Gran Mariscal de Ayacucho, con el propósito de restablecer la integridad del '
         'sistema de transporte e incrementar la presión de bombeo hasta 840 psi, permitiendo el manejo de nafta con '
         'un caudal promedio de 180 MBD de diluente.',
   cliente='Proyectos Mayores FPO'),

 dict(id='veladero', area='construccion', anio='2026', estado='En ejecución',
   lista='Oleoducto 30″ Veladero · Tramo I (5,9 km)',
   titulo='Oleoducto 30″ × 5,90 km',
   sub='Tramo I del Oleoducto de 30″ Veladero',
   texto='Reemplazo del Tramo I del Oleoducto de 30″ × 5,9 km, a fin de garantizar la confiabilidad y continuidad '
         'operacional, así como la integridad mecánica del oleoducto de 30″, en el cumplimiento del transporte de '
         'Diluente Mesa 30 para la División Carabobo, Distrito Morichal y empresas mixtas, y la formulación de la '
         'segregación Merey 16.',
   cliente='PDVSA'),

 dict(id='macolla15', area='construccion', anio='2024 – 2025', estado='Culminado',
   lista='Macolla 15 — vialidad y plataforma',
   titulo='Macolla 15 — vialidad y plataforma',
   sub='Centro Operativo Petromonagas (COPEM)',
   texto='Construcción de la vialidad de acceso y plataforma de perforación para la Macolla 15 del Centro Operativo '
         'Petromonagas, involucrando movimientos de tierra, conformación de taludes, construcción de 39 cellars y '
         'canales de drenaje perimetrales con pases reforzados.',
   cliente='Petromonagas'),

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
   cliente='DAL FPO'),

 dict(id='dragado', area='ambiente', anio='2025 – 2026', estado='Culminado',
   lista='Dragado SIAE COMOR — lagunas A, B, C y D',
   titulo='Dragado lagunas del SIAE COMOR',
   sub='Lagunas A, B, C y D del SIAE',
   texto='Saneamiento y posterior mantenimiento de las cuatro lagunas A, B, C y D del SIAE del Centro Operacional '
         'Morichal (COMOR), en la División Carabobo, a través del dragado de sólidos.',
   cliente='DAL FPO'),

 dict(id='trasegado', area='ambiente', anio='2025 – 2026', estado='En ejecución',
   lista='Movilización y trasegado de crudo — COMOR',
   titulo='Movilización y trasegado de crudo',
   sub='Centro Operativo Morichal',
   texto='Movilización y trasegado de crudo en el Sistema de Inyección y Efluentes (SIAE) ubicado en las '
         'instalaciones del Centro Operativo COMOR, con equipos de vacío tipo vacuum de mínimo 160 BLS.',
   cliente='DAL FPO'),

 dict(id='ef016', area='ambiente', anio='2025', estado='Culminado',
   lista='Saneamiento Estación de Flujo O-16',
   titulo='Estación de Flujo O-16',
   sub='Saneamiento O-16 · División Carabobo',
   texto='Operación de maquinaria pesada para realizar los trabajos de saneamiento de áreas afectadas por derrames '
         'de hidrocarburos: remoción, estabilización, homogeneización, apilamiento y tratamiento in situ del '
         'material impactado, contención y recolección de fluidos petrolizados, nivelación de terreno y carga de '
         'sólidos.',
   cliente='DAL FPO'),

 dict(id='transv', area='servicios', anio='2024 – 2026', estado='En ejecución',
   lista='Equipos transversales',
   titulo='Equipos transversales',
   sub='Equipos para la producción de la FPO',
   texto='Servicio de movimientos relacionados con remoción de suelos, carga, descarga y traslado de materiales '
         'logísticos y misceláneos, contemplados en las operaciones de rehabilitación y reacondicionamiento de '
         'pozos, subestaciones eléctricas, estaciones de flujo y descarga, asociados a las labores operacionales de '
         'las divisiones pertenecientes a la Dirección Ejecutiva de Producción FPO.',
   cliente='DAL FPO'),

 dict(id='chuto', area='servicios', anio='2024 – 2027', estado='En ejecución',
   lista='Chuto con batea',
   titulo='Chuto con batea',
   sub='Movilización de equipos y materiales de la FPO',
   texto='Movilización de todos los materiales y equipos (transformadores, generadores, plantas), misceláneos y '
         'lubricantes, desde las instalaciones PDVSA a nivel nacional hasta las áreas operacionales de las '
         'divisiones Carabobo, Ayacucho, Junín y Boyacá, adscritas a la Dirección Adjunta de Logística perteneciente '
         'a la Dirección Ejecutiva de Producción FPO HC.',
   cliente='DAL FPO'),

 dict(id='bombeo', area='servicios', anio='2025', estado='Culminado',
   lista='Mantenimiento de equipos de bombeo — FPO',
   titulo='Mantenimiento de equipos de bombeo',
   sub='Áreas operacionales de la Faja Petrolífera del Orinoco',
   texto='Reparación de bombas marca Bornemann, Warren, Sulzer y Flowserve, utilizadas para el transporte de fluidos '
         'en superficie y ubicadas en instalaciones pertenecientes a la Faja Petrolífera del Orinoco.',
   cliente='Gestión de Materiales DAL'),

 dict(id='sinovensa', area='servicios', anio='2025 – 2026', estado='Culminado',
   lista='Alquiler de maquinaria — Sinovensa Morichal',
   titulo='Alquiler de maquinaria — Sinovensa',
   sub='Activación de pozos, División Carabobo',
   texto='Servicios de maquinaria pesada para realizar actividades operacionales que contribuyan con la activación '
         'de pozos en la División Carabobo.',
   cliente='Petrolera Sinovensa'),

 dict(id='cortafuego', area='servicios', anio='2025 – 2026', estado='En ejecución',
   lista='Cortafuegos en corredores de tuberías',
   titulo='Cortafuegos en corredores de tuberías',
   sub='Divisiones FPO',
   texto='Construcción y mantenimiento de cortafuegos en corredores de tubería y líneas eléctricas de oleoductos y '
         'diluenductos de la Faja. Incluyendo corrección de filtraciones por soldadura y encapsulamiento de grampas '
         'apernadas.',
   cliente='DAL FPO'),

 dict(id='xpmorichal', area='servicios', anio='2025 – 2027', estado='En ejecución',
   lista='Alquiler de equipos — XP Extrapesado Morichal',
   titulo='Alquiler de equipos — XP Morichal',
   sub='Unidad de Producción Extrapesado, Distrito Morichal',
   texto='Servicios para acondicionamiento y adecuación de vías de acceso y locaciones, los cuales son '
         'indispensables para el óptimo funcionamiento y operación de las unidades de producción de la División '
         'Carabobo.',
   cliente='DAL FPO'),

 dict(id='curataqui', area='ambiente', anio='2024', estado='Culminado',
   lista='Saneamiento Laguna de Curataquiche',
   titulo='Laguna de Curataquiche',
   sub='Saneamiento y restauración ambiental',
   texto='Saneamiento y restauración de la Laguna de Curataquiche, progresiva 15+000 del Oleoducto de 36″, '
         'desarrollando actividades de remoción de capa de hidrocarburos con barreras oleofílicas y material '
         'particulado; estabilización mecánica, carga y transporte del material contaminado; reforestación del área, '
         'toma y análisis de muestras en la laguna, ejecutadas en las diferentes fases del proceso de saneamiento.',
   cliente='DAL FPO'),
]
