import math
from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline



VelUmbral = 0.2  
duraMin = 0.5

class AnalisisIndividual(EtapaPipeline[list[Experimento], list[Experimento]]):

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        for expe in experimentos:
            fps = expe.fps if expe.fps else 30.0
            
            for trayectoria in expe.trayectorias:
                trayectoria.indicadores = self._calcular_indicadores(trayectoria, fps)
                trayectoria.detenciones = self._detectar_detenciones(trayectoria, fps)

            print(f" Análisis individual completado para: {expe.nombre} ({len(expe.trayectorias)} trayectorias analizadas)")
        
        return experimentos

    def _calcular_indicadores(
        self,
        trayectoria: Trayectoria,
        fps: float | None,
    ) -> dict[str, float]:
        fps = fps if fps else 30.0
        obs = trayectoria.observaciones
        if not obs:
            return {}

        pos_inicial = (obs[0].x, obs[0].y)
        pos_final = (obs[-1].x, obs[-1].y)
        tiempo_total = (obs[-1].frame - obs[0].frame) / fps if len(obs) > 1 else 0.0
        
        distancia_total = trayectoria.calcular_distancia_total()
        desplazamiento = trayectoria.calcular_desplazamiento()
        velocidad_media = trayectoria.calcular_velocidad_media(fps)
        
        eficiencia = desplazamiento / distancia_total if distancia_total > 0 else 0.0

        velocidades_instantaneas = []
        for i in range(len(obs) - 1):
            p1, p2 = obs[i], obs[i+1]
            dt = (p2.frame - p1.frame) / fps
            if dt > 0:
                dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
                velocidades_instantaneas.append(dist / dt)
        
        velocidad_maxima = max(velocidades_instantaneas) if velocidades_instantaneas else 0.0

        return {
            "pos_inicial_x": round(pos_inicial[0], 3),
            "pos_inicial_y": round(pos_inicial[1], 3),
            "pos_final_x": round(pos_final[0], 3),
            "pos_final_y": round(pos_final[1], 3),
            "tiempo_total": round(tiempo_total, 3),
            "distancia_total": round(distancia_total, 3),
            "desplazamiento": round(desplazamiento, 3),
            "velocidad_media": round(velocidad_media, 3),
            "velocidad_maxima": round(velocidad_maxima, 3),
            "eficiencia": round(eficiencia, 3)
        }

    def _detectar_detenciones(
        self,
        trayectoria: Trayectoria,
        fps: float | None,
    ) -> list[tuple[int, int]]:
        """Identifica intervalos de detención de una trayectoria."""
        Listadetenciones = []
        inicio = None

        for frame_i, frame_f, velocidad in trayectoria.calcular_velocidades_tramos(fps):
            if velocidad < VelUmbral:
                if inicio is None:
                    inicio = frame_i
                fin = frame_f
                
            else:
                if inicio is not None:
                    if (fin - inicio) / fps >= duraMin:
                        Listadetenciones.append((inicio, fin))
                inicio = None

        if inicio is not None:
            if (fin - inicio) / fps >= duraMin:
                Listadetenciones.append((inicio, fin))

        return Listadetenciones


    def promedio(resultados: dict[int, dict[str, float]], clave: str) -> float:
        suma = sum(r[clave] for r in resultados.values())
        return round(suma / len(resultados), 2)
