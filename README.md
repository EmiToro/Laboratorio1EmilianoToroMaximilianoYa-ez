# Análisis de Trayectorias Peatonales

Integrantes:
- Emiliano Toro Rojas
- Maximiliano Yañez Castillo

Programa en Python que procesa trayectorias de peatones registradas en experimentos de laboratorio (datos del archivo de dinámica peatonal de Forschungszentrum Jülich) y calcula indicadores individuales, análisis espacial y una comparación entre experimentos. Los resultados se exportan a archivos CSV.

## Requisitos

- Linux (probado con terminal bash).
- **Python 3.10 o superior** (el código usa la sintaxis `float | None`).
- No requiere instalar librerías externas: usa solo la biblioteca estándar de Python.

Verifica tu versión de Python:

```bash
python3 --version
```

Si no tienes Python 3.10 o superior, instálalo. En Debian y Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-venv
```

## Instalación

1. Descarga el proyecto y entra a su carpeta. Si lo tienes en un `.zip`:

   ```bash
   unzip nombre-del-proyecto.zip
   cd nombre-de-la-carpeta-del-proyecto
   ```

   Si lo tienes en un repositorio Git:

   ```bash
   git clone <url-del-repositorio>
   cd <carpeta-del-repositorio>
   ```

2. (Opcional) Crea y activa un entorno virtual. No es obligatorio porque no hay dependencias, pero mantiene el entorno ordenado:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Para salir del entorno virtual más tarde: `deactivate`.

3. Verifica que la carpeta `data/` contenga los archivos de entrada `.txt` (por ejemplo `uni_corr_500_01.txt`).

## Estructura del proyecto

```
.
├── main.py              # Punto de entrada
├── data/                # Archivos de entrada (.txt)
├── results/             # Archivos de salida (.csv)
├── models/              # Modelos de datos (Observacion, Trayectoria, Experimento, ...)
├── pipeline/            # Infraestructura del pipeline (contexto, etapa base, ejecución)
└── stages/              # Etapas del procesamiento
    ├── carga.py         # Lectura de archivos y conversión de unidades
    ├── preparacion.py   # Validación y reconstrucción de trayectorias
    ├── individual.py    # Indicadores por peatón y detección de detenciones
    ├── espacial.py      # Zonas, densidad y flujo
    ├── colectivo.py     # Comparación global entre experimentos
    └── exportacion.py   # Escritura de los CSV
```

El programa ejecuta las etapas en este orden: carga, preparación, análisis individual, análisis espacial, comparación y exportación.

## Ejecución

Todos los comandos se ejecutan desde la carpeta raíz del proyecto.

Ejecución básica (lee `./data` y escribe en `./results`):

```bash
python3 main.py
```

Con rutas personalizadas:

```bash
python3 main.py --input ./data --output ./results
```

Procesar un solo archivo:

```bash
python3 main.py --input ./data/uni_corr_500_01.txt --output ./results
```

Mostrar la ayuda:

```bash
python3 main.py --help
```

Si el programa termina bien, el código de salida es 0. Puedes comprobarlo con:

```bash
echo $?
```

### Argumentos

| Argumento | Descripción | Valor por defecto |
|---|---|---|
| `--input` | Archivo `.txt` o directorio con archivos `.txt` de entrada | `./data` |
| `--output` | Directorio donde se guardan los resultados (se crea si no existe) | `./results` |
| `--fps` | Frecuencia de muestreo en cuadros por segundo | sin valor (ver nota) |

### Nota importante sobre los fps

La frecuencia de muestreo determina todas las velocidades, tiempos y flujos calculados. Se obtiene así, en este orden:

1. Si pasas `--fps`, se usa ese valor para todos los archivos.
2. Si no, y el archivo declara `framerate` en su encabezado, se usa ese valor.
3. Si ninguno de los dos existe, se usa **16 fps** (`FPS_POR_DEFECTO` en `stages/carga.py`). Los archivos `uni_corr_500_*` no declaran el framerate, y con 16 fps se obtienen velocidades realistas (alrededor de 1,5 m/s en flujo libre).

Para reproducir los resultados del informe, ejecuta **sin** el argumento `--fps`. Usar un valor distinto (por ejemplo `--fps 30`) cambia las velocidades de forma proporcional.

## Formato de los datos de entrada

Archivos de texto con encabezado en líneas que empiezan con `#` y una fila por observación, con columnas separadas por espacios:

```
<numero> <frame> <x> <y> <z> <rot> <id> <flag>
```

- Las unidades (metros o centímetros) se leen del encabezado y se convierten a metros automáticamente.
- Se descartan las observaciones con `frame < 0`, `id <= 0` o `flag = 52` (extrapolaciones).
- Los peatones con menos de 2 observaciones no se consideran trayectorias.

## Resultados

En el directorio de salida se generan:

- `comparacion_global.csv`: métricas globales (total de experimentos, total de peatones, velocidad media, eficiencia media y densidad media).
- `<nombre_experimento>_indicadores.csv`: una fila por peatón, con las columnas:

| Columna | Significado |
|---|---|
| `id_peaton` | Identificador del peatón |
| `pos_inicial_x`, `pos_inicial_y` | Posición inicial (m) |
| `pos_final_x`, `pos_final_y` | Posición final (m) |
| `tiempo_total` | Duración de la trayectoria (s) |
| `distancia_total` | Longitud recorrida (m) |
| `desplazamiento` | Distancia en línea recta entre inicio y fin (m) |
| `velocidad_media` | Distancia total dividida por el tiempo total (m/s) |
| `velocidad_maxima` | Mayor velocidad entre cuadros consecutivos (m/s) |
| `eficiencia` | Desplazamiento dividido por distancia total (0 a 1) |
| `cantidad_detenciones` | Número de detenciones detectadas |
| `tiempo_total_detenido` | Tiempo acumulado detenido (s) |
| `porcentaje_detenido` | Porcentaje del tiempo de la trayectoria que estuvo detenido |

Una detención se define como un tramo de al menos 0,5 s con velocidad menor o igual a 0,2 m/s (parámetros `VelUmbral` y `duraMin` en `stages/individual.py`).

El análisis espacial (zonas, densidad por tiempo y flujo) se calcula en la etapa `espacial.py` y se muestra en el resultado global solo como densidad media. Las zonas y el flujo por experimento no se exportan a CSV.

## Solución de problemas

- **`python3: command not found`**: instala Python (ver sección Requisitos).
- **`SyntaxError` o error con `float | None`**: tu Python es anterior a 3.10. Actualízalo.
- **`ModuleNotFoundError: No module named 'pipeline'` (o `models`, `stages`)**: ejecuta el programa desde la carpeta raíz del proyecto, donde está `main.py`.
- **`0 experimentos cargados`**: revisa que la ruta de `--input` exista y contenga archivos `.txt`.
- **Las velocidades parecen demasiado altas o bajas**: comprueba que no estés pasando un `--fps` incorrecto.
- **El procesamiento tarda**: los archivos más grandes tienen más de 500 mil líneas. Es normal que tome unos segundos por experimento.