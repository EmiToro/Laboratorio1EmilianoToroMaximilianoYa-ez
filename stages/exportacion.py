from pathlib import Path
import csv

from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class ExportacionResultados(EtapaPipeline[ResultadoAnalisis, None]):

    def ejecutar(
        self,
        resultados: ResultadoAnalisis,
        contexto: ContextoPipeline,
    ) -> None:
        ruta_salida = contexto.ruta_salida
        ruta_salida.mkdir(parents=True, exist_ok=True)
        self._exportar(resultados, ruta_salida)
        print(f"Resultados exportados exitosamente en: {ruta_salida.resolve()}")

    def _exportar(self, resultados: ResultadoAnalisis, ruta_salida: Path) -> None:
        archivo_comparacion = ruta_salida / "comparacion_global.csv"
        with open(archivo_comparacion, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["metrica", "valor"])
            for k, v in resultados.comparacion.items():
                writer.writerow([k, v])

        for expe in resultados.experimentos:
            if not expe.trayectorias:
                continue
            primera_tray = expe.trayectorias[0]
            if not hasattr(primera_tray, "indicadores") or not primera_tray.indicadores:
                continue

            archivo_expe = ruta_salida / f"{expe.nombre}_indicadores.csv"
            with open(archivo_expe, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                cabeceras = ["id_peaton"] + list(primera_tray.indicadores.keys())
                writer.writerow(cabeceras)

                for tray in expe.trayectorias:
                    indicadores = getattr(tray, "indicadores", {})
                    fila = [tray.id_peaton] + [indicadores.get(k, 0.0) for k in primera_tray.indicadores.keys()]
                    writer.writerow(fila)