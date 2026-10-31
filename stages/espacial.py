from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class AnalisisEspacial(EtapaPipeline[list[Experimento], list[Experimento]]):

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        for expe in experimentos:
            expe.zonas = self._analizar_zonas(expe)
            expe.densidad = self._calcular_densidad(expe)
            expe.flujo = self._calcular_flujo(expe, expe.fps)

            print(f" Análisis espacial y colectivo completado para: {expe.nombre}")

        return experimentos

    def _analizar_zonas(self, experimento: Experimento) -> dict[str, float]:
        if not experimento.observaciones:
            return {}
        
        xs = [o.x for o in experimento.observaciones]
        ys = [o.y for o in experimento.observaciones]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        return {
            "min_x": round(min_x, 3),
            "max_x": round(max_x, 3),
            "min_y": round(min_y, 3),
            "max_y": round(max_y, 3),
            "ancho": round(max_x - min_x, 3),
            "alto": round(max_y - min_y, 3)
        }

    def _calcular_densidad(self, experimento: Experimento) -> dict[str, float]:
        if not experimento.observaciones or not experimento.trayectorias:
            return {"densidad": 0.0}

        xs = [o.x for o in experimento.observaciones]
        ys = [o.y for o in experimento.observaciones]
        
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        if area <= 0:
            area = 1.0

        total_peatones = len(experimento.trayectorias)
        densidad_global = total_peatones / area

        return {
            "area_total": round(area, 3),
            "total_peatones": total_peatones,
            "densidad": round(densidad_global, 4)
        }

    def _calcular_flujo(
        self,
        experimento: Experimento,
        fps: float | None,
    ) -> dict[str, float]:
        fps = fps if fps else 30.0
        obs = experimento.observaciones
        if not obs:
            return {"flujo": 0.0}

        frames = [o.frame for o in obs]
        min_frame, max_frame = min(frames), max(frames)
        tiempo_total = (max_frame - min_frame) / fps if max_frame > min_frame else 1.0
        
        total_peatones = len(experimento.trayectorias)
        flujo = total_peatones / tiempo_total if tiempo_total > 0 else 0.0

        return {
            "tiempo_total_experimento": round(tiempo_total, 3),
            "flujo": round(flujo, 4)
        }