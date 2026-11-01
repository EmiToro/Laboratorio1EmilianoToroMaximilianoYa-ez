
from models.experimento import Experimento
from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class ComparacionExperimentos(
    EtapaPipeline[list[Experimento], ResultadoAnalisis]
):

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> ResultadoAnalisis:
        comparacion = self._comparar(experimentos)
        print(f" Comparación completada para {len(experimentos)} experimentos.")
        return ResultadoAnalisis(experimentos=experimentos, comparacion=comparacion)

    def _comparar(self, experimentos: list[Experimento]) -> dict[str, float]:
        if not experimentos:
            return {}

        total_peatones_global = 0
        velocidades_medias = []
        eficiencias = []
        densidades = []

        for expe in experimentos:
            total_peatones_global += len(expe.trayectorias)

            for tray in expe.trayectorias:
                if hasattr(tray, "indicadores") and tray.indicadores:
                    if "velocidad_media" in tray.indicadores:
                        velocidades_medias.append(tray.indicadores["velocidad_media"])

                    if "eficiencia" in tray.indicadores:
                        eficiencias.append(tray.indicadores["eficiencia"])

            if hasattr(expe, "densidad") and expe.densidad:
                if "densidad_media" in expe.densidad:
                    densidades.append(expe.densidad["densidad_media"])

        promedio_velocidad = (
            sum(velocidades_medias) / len(velocidades_medias)
            if velocidades_medias else 0.0
        )

        promedio_eficiencia = (
            sum(eficiencias) / len(eficiencias)
            if eficiencias else 0.0
        )

        promedio_densidad = (
            sum(densidades) / len(densidades)
            if densidades else 0.0
        )

        return {
            "total_experimentos": float(len(experimentos)),
            "total_peatones_global": float(total_peatones_global),
            "velocidad_media_global": round(promedio_velocidad, 3),
            "eficiencia_media_global": round(promedio_eficiencia, 3),
            "densidad_media_global": round(promedio_densidad, 4)
        }
