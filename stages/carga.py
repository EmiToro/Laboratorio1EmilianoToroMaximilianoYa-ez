from pathlib import Path

from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline
from models.observacion import Observacion


class CargaExperimentos(EtapaPipeline[None, list[Experimento]]):

    def ejecutar(
        self,
        entrada: None,
        contexto: ContextoPipeline,
    ) -> list[Experimento]:

        print(f"Buscando experimentos: {contexto.ruta_entrada.resolve()}")

        experimentos = self._cargar_experimentos(
            contexto.ruta_entrada,
            contexto.fps
        )

        print(f"{len(experimentos)} experimentos cargados exitosamente.")

        return experimentos

    def _obtener_factor_unidad(self, archivo: Path) -> float:
        try:
            with open(archivo, "r", encoding="utf-8") as arch:
                for linea in arch:
                    linea = linea.strip().lower()

                    if "in cm" in linea or "in cm]" in linea:
                        return 0.01

                    if "in m" in linea:
                        return 1.0

                    if not linea.startswith("#"):
                        break

        except OSError:
            print(f"No se pudo leer el encabezado de {archivo.name}")

        return 1.0

    def _cargar_experimentos(
        self,
        ruta_entrada: Path,
        fps_contexto: float | None
    ) -> list[Experimento]:

        if ruta_entrada.is_file():
            archivos = [ruta_entrada]
        else:
            archivos = sorted(ruta_entrada.glob("*.txt"))

        experimentos = []

        for archivo in archivos:

            observaciones = []

            fps = fps_contexto if fps_contexto is not None else 16.0

            factor_unidad = self._obtener_factor_unidad(archivo)

            with open(archivo, "r", encoding="utf-8") as arch:

                for linea in arch:

                    linea = linea.strip()

                    if not linea:
                        continue

                    if linea.startswith("#"):

                        if "framerate" in linea.lower():
                            try:
                                partes_fps = linea.replace(":", " ").split()

                                for i, p in enumerate(partes_fps):

                                    if "framerate" in p.lower() and i + 1 < len(partes_fps):
                                        fps = float(partes_fps[i + 1])
                                        break

                            except (ValueError, IndexError):
                                pass

                        continue

                    partes = linea.split()

                    if len(partes) < 8:
                        continue

                    try:
                        frame = int(partes[1])

                        x = float(partes[2]) * factor_unidad
                        y = float(partes[3]) * factor_unidad
                        z = float(partes[4]) * factor_unidad

                        id_peaton = int(partes[6])
                        flag = int(partes[7])

                        if frame < 0 or id_peaton <= 0:
                            continue

                        if flag == 52:
                            continue

                        obs = Observacion(
                            id_peaton,
                            frame,
                            x,
                            y,
                            z
                        )

                        observaciones.append(obs)

                    except (ValueError, IndexError):
                        continue

            print(
                f"{archivo.name}: "
                f"{len(observaciones)} observaciones, "
                f"FPS: {fps}, "
                f"Factor unidad: {factor_unidad}"
            )

            if observaciones:
                experimentos.append(
                    Experimento(
                        archivo.stem,
                        fps,
                        observaciones
                    )
                )

        return experimentos