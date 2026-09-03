# WORKSHOP1

## BUSINESS CONTEXT

Consider a company dedicated to recruiting talent in the technology sector. As part of its selection processes, it receives candidates with different professional profiles and characteristics related to their experience and knowledge in technology. For each candidate, the company has information such as their country of origin, level of seniority, years of professional experience, and the technology areas in which they specialize.
In addition to the relevant information for each candidate, the company conducts a technical evaluation during the selection process. This evaluation consists of two main results: The Code Challenge Score, which reflects the candidate’s performance on a coding test, and the Technical Interview Score, which corresponds to the result obtained in the technical interview. 
Currently, this information is available as operational data from candidate applications. However, relying solely on this data does not provide a direct analytical view of the recruitment process. The company needs to transform this information into a system that allows it to analyze application results from different perspectives and identify patterns related to hiring.
The business process to be analyzed involves the evaluation and outcomes of candidate applications within the technology recruitment process. Each record represents an application submitted by a candidate and contains information about the candidate’s profile, professional qualifications, and performance on technical assessments. Based on these records, the goal is to analyze the results of the selection and hiring process to generate useful insights for recruitment management.


# Objetivo del proyecto

To build an analytical system that transforms operational data from candidate applications into structured, useful information for analyzing the technology recruitment process.
The system will enable the analysis of hiring outcomes from various perspectives, such as trends over time, the technologies associated with candidates, their seniority levels and years of experience, their countries of origin, and their performance on technical assessments. In this way, the information can be used to identify patterns in the selection processes, compare results across different profiles, and provide insights to support decision-making related to recruitment management.
To achieve this objective, application data will be organized and transformed into an analytical structure that enables queries, generates metrics, and subsequently produces visualizations designed to address the company’s specific needs. The ultimate goal is not merely to store data, but to convert it into insights that provide a better understanding of the selection process’s outcomes and support evidence-based management decisions.


# Business Requirements

The requirements for the analysis were as follows:

| ID     | Requirement                                                                                                                |
| ------ | -------------------------------------------------------------------------------------------------------------------------- |
| **R1** | How has the number of hires changed over time?                                                                             |
| **R2** | ¿Qué tecnologías presentan mayor demanda y mejores resultados de contratación?                                             |
| **R3** | ¿Qué perfiles de candidatos presentan mejores resultados de contratación según su seniority y experiencia?                 |
| **R4** | ¿Qué países representan mercados de reclutamiento más atractivos según el volumen de candidatos y su tasa de contratación? |
| **R5** | ¿Qué tecnologías presentan dificultades para convertir las aplicaciones recibidas en contrataciones?                       |



# Descripción del dataset

El proyecto utiliza como fuente principal el archivo:

```text
data/raw/candidates.csv
```

La extracción se realiza mediante Pandas utilizando `;` como separador.

El dataset contiene información relacionada con las aplicaciones realizadas por candidatos, incluyendo datos personales, ubicación, experiencia, tecnología, fechas y resultados de evaluaciones.

Entre los principales atributos se encuentran:

| Columna                   | Descripción                      |
| ------------------------- | -------------------------------- |
| First Name                | Nombre del candidato             |
| Last Name                 | Apellido del candidato           |
| Email                     | Correo electrónico               |
| Country                   | País del candidato               |
| Application Date          | Fecha de aplicación              |
| YOE                       | Años de experiencia              |
| Seniority                 | Nivel de seniority               |
| Technology                | Tecnología asociada              |
| Code Challenge Score      | Puntaje de la prueba técnica     |
| Technical Interview Score | Puntaje de la entrevista técnica |

---

# 4. Estructura del proyecto

La organización principal del proyecto es la siguiente:

```text
workshop-1/
│
├── data/
│   └── raw/
│       └── candidates.csv
│
├── notebooks/
│   └── data_profiling.py
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── dimensional_model.py
│   ├── validation.py
│   ├── load.py
│   └── main.py
│
├── sql/
│   ├── create_tables.sql
│   └── analytical_queries.sql
│
├── diagrams/
│   └── star_schema.png
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 5. Perfilamiento inicial de los datos

El perfilamiento inicial se implementó en:

```text
notebooks/data_profiling.py
```

Este proceso analiza el dataset original sin modificarlo. Para mantener una única fuente de extracción, el script reutiliza la función `extract_data()` definida en `src/extract.py`.

## Análisis realizados

El perfilamiento incluye:

1. Número de filas y columnas.
2. Nombres de las columnas y tipos de datos originales.
3. Identificación de valores faltantes.
4. Identificación de registros duplicados.
5. Revisión de valores únicos en variables categóricas.
6. Análisis del rango de fechas.
7. Estadísticas descriptivas de variables numéricas.
8. Validación de los rangos de los puntajes.
9. Resumen de hallazgos.

## Hallazgos principales

| Aspecto                        | Hallazgo                                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| Tamaño del dataset             | 50.000 filas y 10 columnas                                                                                   |
| Valores nulos                  | No se encontraron valores nulos                                                                              |
| Filas completamente duplicadas | No se encontraron                                                                                            |
| Emails repetidos               | Existen registros que pueden compartir email, pero representan aplicaciones y no se eliminan automáticamente |
| Application Date               | Se encontraba como texto y se convirtió posteriormente a tipo fecha                                          |
| Seniority                      | 7 niveles de seniority                                                                                       |
| Technology                     | 24 tecnologías diferentes                                                                                    |
| Country                        | 244 países diferentes                                                                                        |
| Code Challenge Score           | Valores dentro del rango de 0 a 10                                                                           |
| Technical Interview Score      | Valores dentro del rango de 0 a 10                                                                           |

### Decisión sobre registros repetidos

Los valores repetidos en la columna `Email` no fueron eliminados automáticamente. El grano definido para el proyecto corresponde a **una aplicación**, por lo que dos registros con el mismo correo pueden representar aplicaciones diferentes.

Por esta razón, eliminar registros únicamente porque comparten un correo podría ocasionar pérdida de información.

---

# 6. Proceso de extracción

La extracción se implementó en:

```text
src/extract.py
```

La función principal es:

```python
extract_data()
```

Su responsabilidad es únicamente leer el archivo original:

```text
data/raw/candidates.csv
```

El archivo se carga utilizando:

```python
pd.read_csv(source_path, sep=";")
```

## Decisiones implementadas

Durante la etapa de extracción:

* Se utiliza el archivo fuente original.
* El archivo original no se modifica.
* No se aplican transformaciones de negocio.
* No se eliminan registros.
* Se verifica que el archivo exista antes de intentar leerlo.
* Se retorna un DataFrame con los datos tal como vienen desde el origen.

Esto permite separar claramente la extracción de las etapas posteriores de preparación y transformación.

---

# 7. Preparación y transformación de datos

Las transformaciones se implementaron en:

```text
src/transform.py
```

El proceso se divide en dos etapas principales.

## 7.1 Preparación de datos

La función:

```python
prepare_data(df)
```

realiza las siguientes acciones:

### Conversión de fecha

La columna:

```text
Application Date
```

se convierte a tipo fecha:

```python
pd.to_datetime(
    df["Application Date"],
    format="%Y-%m-%d"
)
```

### Limpieza de espacios

Se eliminan espacios adicionales al inicio y al final de las columnas de texto:

* First Name
* Last Name
* Email
* Country
* Seniority
* Technology

### Orden de seniority

Se establece un orden lógico para los niveles de seniority:

```text
Intern
→ Trainee
→ Junior
→ Mid-Level
→ Senior
→ Lead
→ Architect
```

Esto facilita posteriormente el análisis ordenado de los perfiles de candidatos.

### Conversión de variables categóricas

Las columnas:

```text
Technology
Country
```

se convierten a variables categóricas.

### Verificación de valores faltantes

Después de la preparación se realiza una verificación adicional para identificar posibles valores nulos.

---

## 7.2 Regla de negocio de contratación

La función:

```python
apply_business_rules(df)
```

implementa la siguiente regla:

```text
HIRED =
(Code Challenge Score >= 7)
AND
(Technical Interview Score >= 7)
```

Es decir, un candidato se considera contratado únicamente cuando obtiene un puntaje igual o superior a 7 en ambas evaluaciones.

El resultado se almacena en una nueva columna:

```text
Hired
```

con valores booleanos.

### Decisión importante

La transformación **no elimina las aplicaciones no contratadas**.

Esto es necesario porque el grano del modelo es una aplicación y los requerimientos necesitan analizar tanto el total de aplicaciones como las contrataciones.

Eliminar los registros `NOT HIRED` impediría calcular correctamente indicadores como:

```text
Hiring Rate =
Total Hired / Total Applications
```

---

# 8. Modelo dimensional

Se implementó un modelo dimensional de tipo:

# Star Schema

El modelo está compuesto por:

* 4 dimensiones.
* 1 tabla de hechos.

La transformación dimensional se encuentra en:

```text
src/dimensional_model.py
```

---

## 8.1 Grano de la tabla de hechos

El grano definido es:

> **Una fila en `fact_application` representa una aplicación de un candidato a una tecnología en una fecha y país específicos.**

Esta definición permite conservar cada aplicación como una observación individual y posteriormente analizarla desde diferentes dimensiones.

---

## 8.2 Dimensiones

### `dim_date`

| Campo      | Descripción                 |
| ---------- | --------------------------- |
| `date_key` | Clave surrogate de la fecha |
| `day`      | Día                         |
| `month`    | Mes                         |
| `quarter`  | Trimestre                   |
| `year`     | Año                         |

Durante la transformación se utiliza temporalmente `full_date` para relacionar cada aplicación con su `date_key`.

Sin embargo, `full_date` se elimina antes de retornar el esquema dimensional final.

---

### `dim_candidate`

| Campo           | Descripción                   |
| --------------- | ----------------------------- |
| `candidate_key` | Clave surrogate del candidato |
| `first_name`    | Nombre                        |
| `last_name`     | Apellido                      |
| `email`         | Correo                        |
| `yoe`           | Años de experiencia           |
| `seniority`     | Nivel de seniority            |

---

### `dim_technology`

| Campo            | Descripción     |
| ---------------- | --------------- |
| `technology_key` | Clave surrogate |
| `technology`     | Tecnología      |

---

### `dim_country`

| Campo         | Descripción     |
| ------------- | --------------- |
| `country_key` | Clave surrogate |
| `country`     | País            |

---

## 8.3 Tabla de hechos

### `fact_application`

| Campo             | Tipo lógico | Descripción                      |
| ----------------- | ----------- | -------------------------------- |
| `application_key` | PK          | Clave surrogate de la aplicación |
| `date_key`        | FK          | Referencia a `dim_date`          |
| `candidate_key`   | FK          | Referencia a `dim_candidate`     |
| `technology_key`  | FK          | Referencia a `dim_technology`    |
| `country_key`     | FK          | Referencia a `dim_country`       |
| `code_score`      | Medida      | Puntaje de Code Challenge        |
| `interview_score` | Medida      | Puntaje de Technical Interview   |
| `hired_indicator` | Medida      | 1 para HIRED y 0 para NOT HIRED  |

---

## 8.4 Claves surrogate

Todas las dimensiones utilizan claves surrogate generadas secuencialmente:

```text
1, 2, 3, ...
```

Estas claves son independientes de las claves naturales del origen.

Por ejemplo, no se utiliza:

```text
email
technology
country
Application Date
```

como clave primaria de las dimensiones.

Esto permite desacoplar el modelo dimensional de los identificadores naturales del dataset.

---

## 8.5 Integridad durante la construcción del modelo

Para construir la tabla de hechos, cada aplicación se relaciona con las dimensiones correspondientes mediante `merge`.

Después se verifica que ninguna clave foránea haya quedado sin asignar:

```text
date_key
candidate_key
technology_key
country_key
```

Si alguna relación no encuentra una dimensión correspondiente, el proceso genera un error y evita continuar con una tabla de hechos inconsistente.

---

## 8.6 Diagrama del modelo

El esquema implementado corresponde al siguiente modelo estrella:

```text
                 dim_date
                    │
                    │
dim_candidate ── fact_application ── dim_technology
                    │
                    │
               dim_country
```

> En el repositorio se debe incluir el diagrama visual en:
>
> ```text
> diagrams/star_schema.png
> ```

---

# 9. Validaciones de calidad previas a la carga

Antes de cargar los datos en MySQL se ejecutan validaciones implementadas en:

```text
src/validation.py
```

El objetivo es detectar problemas antes de insertar datos en el Data Warehouse.

La función principal es:

```python
run_all_validations(df_source, star_schema)
```

---

## 9.1 Validación de claves primarias

Se verifica para cada tabla que su clave primaria:

* No contenga valores nulos.
* Sea única.

Las claves validadas son:

| Tabla              | Clave primaria    |
| ------------------ | ----------------- |
| `dim_date`         | `date_key`        |
| `dim_candidate`    | `candidate_key`   |
| `dim_technology`   | `technology_key`  |
| `dim_country`      | `country_key`     |
| `fact_application` | `application_key` |

---

## 9.2 Integridad referencial

Se verifica que cada clave foránea de `fact_application` exista en su dimensión correspondiente.

Las relaciones verificadas son:

```text
date_key
candidate_key
technology_key
country_key
```

No se permite continuar si existen:

* Valores nulos en las claves foráneas.
* Referencias a claves inexistentes.
* Valores huérfanos.

---

## 9.3 Conteo de registros

Se compara:

```text
Número de registros del dataset transformado
```

contra:

```text
Número de filas de fact_application
```

Esto permite verificar que durante la transformación:

* No se hayan perdido aplicaciones.
* No se hayan duplicado aplicaciones.

---

## 9.4 Validación de medidas

Se validan las siguientes reglas:

| Medida            | Regla              |
| ----------------- | ------------------ |
| `code_score`      | Entre 0 y 10       |
| `interview_score` | Entre 0 y 10       |
| `hired_indicator` | Solo valores 0 o 1 |

Si alguna validación crítica falla, se lanza:

```text
ValidationError
```

y el pipeline no continúa hacia la carga.

---

# 10. Carga al Data Warehouse

La carga se implementó en:

```text
src/load.py
```

El motor utilizado es:

# MySQL

La base de datos utilizada es:

```text
recruitment_dw
```

La conexión se realiza utilizando:

* SQLAlchemy
* PyMySQL
* python-dotenv

---

## 10.1 Configuración de credenciales

Las credenciales se cargan desde un archivo:

```text
.env
```

Las variables utilizadas son:

```text
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME
```

El archivo `.env` no debe versionarse en Git para evitar exponer credenciales.

---

## 10.2 Creación del esquema físico

El script:

```text
sql/create_tables.sql
```

crea las tablas del Data Warehouse.

Se incluyen:

* Primary Keys.
* Foreign Keys.
* Tipos de datos correspondientes a los atributos.

Las claves foráneas de la tabla de hechos son:

```text
fk_fact_date
fk_fact_candidate
fk_fact_technology
fk_fact_country
```

---

## 10.3 Orden de carga

La carga se realiza respetando las dependencias entre las tablas:

```text
1. dim_date
2. dim_candidate
3. dim_technology
4. dim_country
5. fact_application
```

Primero se cargan las dimensiones y finalmente la tabla de hechos.

Este orden evita errores de integridad referencial.

---

# 11. Validación post-carga

Después de cargar los datos, se realizan validaciones directamente contra MySQL.

Esto es importante porque no se valida únicamente el DataFrame en memoria, sino el resultado real almacenado en el Data Warehouse.

Las validaciones incluyen:

## Claves primarias

Se comparan:

```sql
COUNT(*)
```

contra:

```sql
COUNT(DISTINCT primary_key)
```

y se verifica la ausencia de valores nulos.

---

## Integridad referencial

Se utilizan consultas con `LEFT JOIN` entre `fact_application` y cada dimensión para detectar posibles registros huérfanos.

La validación comprueba que todas las claves utilizadas en la tabla de hechos tengan una dimensión válida.

---

## Conteo de registros

Para cada tabla se compara:

```text
Registros esperados
```

contra:

```text
Registros realmente cargados en MySQL
```

La carga se considera correcta cuando todas las validaciones son satisfactorias.

---

# 12. Orquestación del pipeline ETL

Todo el proceso es coordinado desde:

```text
src/main.py
```

El pipeline ejecuta las siguientes etapas:

```text
1. EXTRACCIÓN
2. PREPARACIÓN DE DATOS
3. TRANSFORMACIÓN DE NEGOCIO
4. TRANSFORMACIÓN DIMENSIONAL
5. VALIDACIÓN DE CALIDAD PRE-CARGA
6. CARGA AL DATA WAREHOUSE
7. VALIDACIÓN POST-CARGA EN MYSQL
8. FIN DEL PROCESO
```

El flujo completo puede representarse de la siguiente forma:

```text
extract_data()
        ↓
prepare_data()
        ↓
apply_business_rules()
        ↓
build_star_schema()
        ↓
run_all_validations()
        ↓
create_schema()
        ↓
load_star_schema()
        ↓
validate_primary_keys()
validate_referential_integrity()
validate_row_counts()
```

Además, el proyecto utiliza la librería `rich` para generar reportes visuales en consola durante las diferentes etapas.

---

# 13. Consultas analíticas

Las consultas se encuentran en:

```text
sql/analytical_queries.sql
```

Cada requerimiento de negocio cuenta con una consulta específica.

---

## R1 — Hiring Trends

Analiza la evolución de:

* Total de aplicaciones.
* Total de contrataciones.
* Hiring rate.

Los datos se agrupan por:

```text
Año
Mes
```

La consulta permite identificar cómo ha evolucionado el proceso de contratación a través del tiempo.

---

## R2 — Technology Analysis

Analiza cada tecnología utilizando:

* Total de aplicaciones.
* Total de contrataciones.
* Hiring rate.
* Promedio de Code Challenge Score.
* Promedio de Technical Interview Score.

Esto permite identificar tecnologías con mayor volumen de candidatos y evaluar sus resultados de contratación.

---

## R3 — Candidate Profile Analysis

Analiza los candidatos según:

```text
Seniority
```

Los indicadores calculados son:

* Promedio de años de experiencia.
* Total de aplicaciones.
* Total de contrataciones.
* Hiring rate.
* Promedio de Code Challenge Score.
* Promedio de Technical Interview Score.

Esto permite comparar los resultados de contratación entre los diferentes perfiles profesionales.

---

## R4 — Mercados de reclutamiento atractivos

Analiza los países utilizando:

* Total de aplicaciones.
* Total de contrataciones.
* Hiring rate.

Los resultados se ordenan principalmente por tasa de contratación y, posteriormente, por volumen de aplicaciones.

Esto permite comparar los diferentes mercados disponibles para el proceso de reclutamiento.

---

## R5 — Tecnologías con dificultades de contratación

Analiza las tecnologías con menor capacidad de convertir aplicaciones en contrataciones.

Para evitar conclusiones basadas en muestras pequeñas, la consulta solo considera tecnologías con:

```text
50 o más aplicaciones
```

Se calculan:

* Total de aplicaciones.
* Total de contrataciones.
* Hiring rate.
* Promedio de Code Challenge Score.
* Promedio de Technical Interview Score.

Los resultados se ordenan de menor a mayor `hiring_rate`.

---

# 14. KPIs implementados

Para el dashboard se crearon indicadores principales para resumir el comportamiento general del proceso de reclutamiento.

| KPI                         | Descripción                                               |
| --------------------------- | --------------------------------------------------------- |
| **Total Applications**      | Número total de aplicaciones                              |
| **Total Hired**             | Número total de candidatos contratados                    |
| **Hiring Rate**             | Porcentaje de aplicaciones que terminaron en contratación |
| **Average Code Score**      | Puntaje promedio de Code Challenge                        |
| **Average Interview Score** | Puntaje promedio de Technical Interview                   |

El indicador de contratación se calcula conceptualmente como:

```text
Hiring Rate =
(Total Hired / Total Applications) × 100
```

---

# 15. Dashboard en Power BI

Se desarrolló un dashboard titulado:

# Recruitment Analytics Dashboard

El dashboard permite responder visualmente los cinco requerimientos de negocio.

La interfaz incluye:

* Título principal.
* Segmentadores superiores.
* Tarjetas KPI.
* Cinco visualizaciones analíticas.
* Navegación lateral.
* Diseño visual consistente basado en tonos oscuros, morados, azules, verdes y rosados según el propósito de cada visualización.

Los filtros disponibles incluyen:

```text
Año
Mes
Tecnología
País
Seniority
```

Estos filtros permiten analizar los indicadores de manera interactiva.

---

## KPI principales observados

A nivel general, el dashboard muestra aproximadamente:

| Indicador               | Resultado |
| ----------------------- | --------: |
| Total Applications      |    50 mil |
| Total Hired             |     7 mil |
| Hiring Rate             |   13,40 % |
| Average Code Score      |      5,00 |
| Average Interview Score |      5,00 |

Estos valores proporcionan una visión general del proceso antes de aplicar filtros específicos.

---

## Visualización R1 — Evolución de aplicaciones y contrataciones

**Tipo de gráfico:** gráfico de líneas.

**Eje X:** tiempo, utilizando los atributos disponibles de `dim_date`, principalmente año y mes.

**Eje Y:** cantidad de aplicaciones y cantidad de contrataciones.

**Medidas utilizadas:**

* Total Applications.
* Total Hired.

Este gráfico permite comparar cómo evoluciona el volumen de aplicaciones frente a las contrataciones a través del tiempo.

---

## Visualización R2 — Análisis de tecnologías

**Tipo de gráfico:** barras horizontales.

El gráfico permite identificar las tecnologías con mayor número de aplicaciones y comparar su demanda dentro del proceso de reclutamiento.

La información se complementa con los indicadores y consultas analíticas para evaluar también los resultados de contratación.

---

## Visualización R3 — Resultados por seniority

**Tipo de gráfico:** barras.

La visualización compara los diferentes niveles de seniority utilizando el comportamiento de contratación correspondiente a cada perfil.

Esto permite identificar qué perfiles presentan mejores resultados en el proceso.

---

## Visualización R4 — Top países

**Tipo de gráfico:** barras horizontales.

El gráfico muestra los países con mejores resultados de contratación, teniendo en cuenta el análisis realizado mediante el volumen de aplicaciones y la tasa de contratación.

---

## Visualización R5 — Tecnologías con mayor dificultad de contratación

**Tipo de gráfico:** barras horizontales.

La visualización destaca las tecnologías con menor tasa de contratación, considerando únicamente aquellas con un mínimo de 50 aplicaciones.

Esto evita que una tecnología con muy pocos registros genere una conclusión poco representativa.

---

# 16. Diseño visual del dashboard

El dashboard fue diseñado buscando una apariencia moderna y consistente.

La estructura principal se divide en:

```text
┌──────────────────────────────────────────────────────────┐
│ TÍTULO                         FILTROS                   │
├──────────────────────────────────────────────────────────┤
│ KPI 1 │ KPI 2 │ KPI 3 │ KPI 4 │ KPI 5                    │
├──────────────────────────────────────────────────────────┤
│ R1 — Evolución temporal                                 │
├──────────────────────────────┬───────────────────────────┤
│ R2 — Tecnologías             │ R3 — Seniority            │
├──────────────────────────────┼───────────────────────────┤
│ R4 — Países                  │ R5 — Tecnologías          │
│                              │ con dificultad            │
└──────────────────────────────┴───────────────────────────┘
```

La distribución permite que los indicadores generales se visualicen primero y que posteriormente el usuario pueda profundizar en cada uno de los requerimientos.

---

# 17. Trazabilidad de requerimientos

La siguiente tabla muestra cómo cada requerimiento fue conectado con el modelo dimensional, las consultas y las visualizaciones.

| Requerimiento | Dimensiones utilizadas | Medidas principales                          | Consulta SQL               | Visualización        |
| ------------- | ---------------------- | -------------------------------------------- | -------------------------- | -------------------- |
| **R1**        | `dim_date`             | Total Applications, Total Hired, Hiring Rate | Hiring Trends              | Línea temporal       |
| **R2**        | `dim_technology`       | Applications, Hired, Hiring Rate, Scores     | Technology Analysis        | Barras horizontales  |
| **R3**        | `dim_candidate`        | Experience, Hired, Hiring Rate, Scores       | Candidate Profile Analysis | Barras por seniority |
| **R4**        | `dim_country`          | Applications, Hired, Hiring Rate             | Recruitment Markets        | Barras horizontales  |
| **R5**        | `dim_technology`       | Applications, Hired, Hiring Rate, Scores     | Hiring Difficulties        | Barras horizontales  |

---

# 18. Validación final de requerimientos

| Requirement | Implemented? | DW Tables Used                       | Query / KPI                                          | Main Finding                                                                                                                                     |
| ----------- | ------------ | ------------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **R1**      | Yes          | `fact_application`, `dim_date`       | Total Applications, Total Hired y evolución temporal | Permite analizar la evolución de las aplicaciones y contrataciones a través del tiempo.                                                          |
| **R2**      | Yes          | `fact_application`, `dim_technology` | Technology Analysis                                  | Permite identificar las tecnologías con mayor volumen de aplicaciones y analizar sus resultados de contratación.                                 |
| **R3**      | Yes          | `fact_application`, `dim_candidate`  | Hiring Rate por Seniority                            | Permite comparar los resultados de contratación entre los diferentes niveles de seniority y experiencia.                                         |
| **R4**      | Yes          | `fact_application`, `dim_country`    | Hiring Rate por Country                              | Permite identificar los países con mejores resultados y volumen dentro del proceso de reclutamiento.                                             |
| **R5**      | Yes          | `fact_application`, `dim_technology` | Hiring Rate por Technology                           | Permite detectar tecnologías con menor capacidad de convertir aplicaciones en contrataciones, considerando muestras de al menos 50 aplicaciones. |

---

# 19. Tecnologías utilizadas

El proyecto fue desarrollado utilizando las siguientes herramientas:

| Tecnología      | Uso                                                |
| --------------- | -------------------------------------------------- |
| Python          | Desarrollo del proceso ETL                         |
| Pandas          | Manipulación y transformación de datos             |
| MySQL           | Almacenamiento del Data Warehouse                  |
| MySQL Workbench | Administración y consulta de la base de datos      |
| SQLAlchemy      | Conexión entre Python y MySQL                      |
| PyMySQL         | Driver de conexión a MySQL                         |
| python-dotenv   | Gestión de variables de entorno                    |
| Rich            | Reportes visuales en consola                       |
| Power BI        | Visualización y análisis de datos                  |
| Git/GitHub      | Control de versiones y almacenamiento del proyecto |

---

# 20. Instalación y ejecución

## 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
```

## 2. Ingresar al proyecto

```bash
cd workshop-1
```

## 3. Crear un entorno virtual

```bash
python -m venv venv
```

## 4. Activar el entorno virtual

En Windows:

```bash
venv\Scripts\activate
```

## 5. Instalar las dependencias

```bash
pip install -r requirements.txt
```

## 6. Configurar las variables de entorno

Crear un archivo `.env` con la siguiente estructura:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=recruitment_dw
```

> El archivo `.env` no debe subirse al repositorio.

## 7. Crear la base de datos

Antes de ejecutar el pipeline debe existir la base de datos:

```sql
CREATE DATABASE recruitment_dw;
```

## 8. Ejecutar el pipeline ETL

Desde la carpeta `src`:

```bash
python main.py
```

El proceso ejecutará:

```text
Extracción
→ Preparación
→ Transformación de negocio
→ Transformación dimensional
→ Validaciones pre-carga
→ Creación de tablas
→ Carga en MySQL
→ Validaciones post-carga
```

---

# 21. Dependencias

El archivo `requirements.txt` incluye:

```text
sqlalchemy
pymysql
python-dotenv
```

Adicionalmente, el proyecto utiliza:

```text
pandas
rich
```

Por tanto, **te recomiendo revisar tu `requirements.txt`**, porque según el código que me compartiste también estás importando `pandas` y `rich`. Para que cualquier persona pueda ejecutar correctamente el proyecto desde cero, debería quedar así:

```text
pandas
rich
sqlalchemy
pymysql
python-dotenv
```

Esta corrección sí te recomiendo hacerla antes de entregar el repositorio.

---

# 22. Conclusiones

El proyecto permitió construir un proceso completo desde datos transaccionales almacenados en un archivo CSV hasta un entorno analítico compuesto por un Data Warehouse y un dashboard interactivo.

Entre los principales resultados del proyecto se encuentran:

* Se procesaron **50.000 aplicaciones**.
* Se conservaron todas las aplicaciones durante el proceso, incluyendo las contratadas y no contratadas.
* Se implementó una regla de negocio para identificar automáticamente las contrataciones.
* Se construyó un modelo dimensional con **4 dimensiones y 1 tabla de hechos**.
* Se utilizaron claves surrogate para desacoplar el modelo dimensional de las claves naturales del origen.
* Se implementaron validaciones de calidad antes de la carga.
* Se realizaron validaciones directamente sobre MySQL después de la carga.
* Se desarrollaron consultas analíticas para responder los cinco requerimientos de negocio.
* Se construyó un dashboard en Power BI con filtros, KPIs y visualizaciones interactivas.
* El resultado general muestra aproximadamente **7 mil contrataciones sobre 50 mil aplicaciones**, equivalente a un **Hiring Rate de 13,40 %**.

En conclusión, el proyecto demuestra un flujo completo de ingeniería de datos, desde la extracción y transformación hasta la construcción de un modelo dimensional, almacenamiento en un Data Warehouse y explotación analítica mediante herramientas de Business Intelligence.

---

## Mi recomendación antes de subirlo a GitHub

Hay **tres cosas** que yo ajustaría antes de darlo por terminado:

1. **Cambiar `requirements.txt`** para incluir `pandas` y `rich`.
2. **Agregar la imagen real del Star Schema** dentro de `diagrams/`.
3. **Agregar una captura del dashboard final** al README, porque visualmente le dará mucha más fuerza al proyecto.

Por ejemplo, debajo de la sección **Dashboard en Power BI** puedes insertar:

```md
## Vista del Dashboard

![Recruitment Analytics Dashboard](ruta/a/tu/imagen.png)
```

Y también convendría insertar la imagen del esquema estrella:

```md
## Modelo Star Schema

![Star Schema](diagrams/star_schema.png)
```

**Esta versión ya está basada en el código que realmente compartiste y en el dashboard que construiste**, en lugar de dejar tareas como pendientes o afirmar procesos que no realizaste.
