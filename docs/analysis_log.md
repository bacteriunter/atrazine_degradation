# Atrazine degradation modelling — Analysis log

## Checkpoint 0 — Project initialization

Project directory structure created.

Raw datasets:

- base_1.xlsx
- base_2.xlsx
- base_3.xlsx
- base_4.xlsx
- pda_aislamiento.xlsx
- pdab1_bacterias.xlsx

Raw datasets are treated as immutable.

SHA-256 checksums are stored in:

docs/raw_data_sha256.txt

No statistical analyses or data transformations have been performed.

## Checkpoint 2 — Preparación del experimento de laboratorio

Se procesó `data/raw/base_1.xlsx` mediante `scripts/01_prepare_lab_data.py`.

Diseño experimental confirmado:
- Suelo de Capulín completamente esterilizado.
- Muestreo destructivo; las observaciones de distintos tiempos corresponden a unidades experimentales independientes.
- Tiempos: 5, 10, 20 y 40 días.
- Tres réplicas independientes por tratamiento y tiempo.
- B: blanco, suelo sin atrazina y sin microorganismos inoculados.
- Te: testigo, suelo contaminado con 500 ppm de atrazina y sin microorganismos inoculados.
- R: 500 ppm de atrazina + Rhizobium.
- T: 500 ppm de atrazina + Trichoderma.
- RT: 500 ppm de atrazina + Rhizobium + Trichoderma.
- La concentración inicial de 500 ppm fue nominal/teórica y no corresponde a una medición HPLC en t=0.

Se identificaron 60 observaciones experimentales:
5 tratamientos × 4 tiempos × 3 réplicas.

La fila adicional del archivo original no corresponde a una unidad experimental. Contiene únicamente `Muestra.1 = max` y `% biodegra = 92.910053`, por lo que fue excluida del dataset procesado.

Las columnas `% remosión` y `% biodegra` contienen valores idénticos. Se conserva `biodegradation_pct` como variable estandarizada, manteniendo las columnas originales necesarias para trazabilidad.

No se realizaron pruebas estadísticas ni ajustes de modelos en este checkpoint.

Dataset generado:
`data/processed/lab_degradation.csv`

## Selección histórica de diluciones en los recuentos microbiológicos

Las diluciones registradas en pdab1_bacterias.xlsx corresponden a las
diluciones seleccionadas experimentalmente para realizar los recuentos.
Las diluciones anteriores presentaban crecimiento incontable y por esa
razón no fueron utilizadas para el conteo.

No se aplicará retrospectivamente un intervalo externo de colonias
contables (por ejemplo, 30-300 colonias), ya que ese criterio no formó
parte de la metodología documentada para estos datos.

Los análisis conservarán explícitamente suelo, dilución, bloque y
repetición. Los valores de CFU/mL utilizados serán los recalculados a
partir del conteo de colonias, la dilución y el volumen inoculado,
manteniendo los valores originales para trazabilidad.

## Selección histórica de diluciones en los recuentos microbiológicos

Las diluciones registradas en pdab1_bacterias.xlsx corresponden a las
diluciones seleccionadas experimentalmente para realizar los recuentos.
Las diluciones anteriores presentaban crecimiento incontable y por esa
razón no fueron utilizadas para el conteo.

No se aplicará retrospectivamente un intervalo externo de colonias
contables (por ejemplo, 30-300 colonias), ya que ese criterio no formó
parte de la metodología documentada para estos datos.

Los análisis conservarán explícitamente suelo, dilución, bloque y
repetición. Los valores de CFU/mL utilizados serán los recalculados a
partir del conteo de colonias, la dilución y el volumen inoculado,
manteniendo los valores originales para trazabilidad.

## Naturaleza de las réplicas de la caracterización fisicoquímica

Las tres determinaciones disponibles para cada variable fisicoquímica
de cada suelo corresponden a submuestras de una muestra compuesta,
no a tres muestras de suelo biológicamente independientes.

En consecuencia, estas determinaciones se utilizarán para caracterización
descriptiva de cada muestra compuesta (por ejemplo, media y desviación
estándar), pero no como réplicas independientes para pruebas inferenciales
entre suelos.

No se realizarán ANOVA, Kruskal-Wallis ni otras pruebas de significancia
entre los tres suelos utilizando estas submuestras como réplicas
independientes.

Asimismo, no se utilizarán las submuestras para aumentar artificialmente
el tamaño muestral en análisis multivariados o asociaciones entre
propiedades fisicoquímicas y microbiológicas.

## Estructura de replicación de los recuentos microbiológicos

Los suelos utilizados para los recuentos microbiológicos proceden de
una muestra compuesta por suelo.

Los bloques B1, B2 y B3 corresponden a repeticiones realizadas a partir
de la misma muestra compuesta y no representan muestras de suelo
biológicamente independientes.

Dentro de cada bloque, las tres repeticiones corresponden a tres cajas
Petri inoculadas con la misma dilución y constituyen réplicas técnicas.

Por tanto, las nueve observaciones disponibles para una combinación
suelo-dilución no se tratarán como nueve réplicas biológicas
independientes.

Los recuentos microbiológicos se utilizarán para caracterización
descriptiva, manteniendo separadas las diluciones y mostrando la
variabilidad observada entre bloques y cajas. No se realizarán pruebas
inferenciales entre suelos utilizando bloques o cajas Petri como
réplicas biológicas.

Esta decisión evita pseudorreplicación.
