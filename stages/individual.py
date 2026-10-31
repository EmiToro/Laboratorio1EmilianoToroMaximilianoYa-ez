"""Etapa de análisis individual de los experimentos."""

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline



UMBRAL_VELOCIDAD = 0.2  
DURACION_MINIMA = 1

class AnalisisIndividual(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Coordina el análisis de múltiples trayectorias y reúne sus indicadores."""

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las trayectorias de cada experimento."""
        for exp in experimentos:
            print("Inicia Analisis! /n")
            exp.resultados_individuales = {t.id_peaton: self._calcular_indicadores(t, exp.fps) for t in exp.trayectorias}
            r = exp.resultados_individuales
            total_detenciones = int(sum(i["cantidad_detenciones"] for i in r.values()))
            print(f" Experimento: {exp.nombre}")
            print(f" Peatones analizados: {len(r)}")
            print(f" Velocidad media: {self.promedio(r, 'velocidad_media_ms')} m/s")
            print(f" Eficiencia media: {self.promedio(r, 'eficiencia')}")
            print(f" Total de detenciones: {total_detenciones}")
            print(f" Tiempo medio detenido: {self.promedio(r, 'porcentaje_detenido')} %")
        return experimentos




    def _calcular_indicadores(
        self,
        trayectoria: Trayectoria,
        fps: float | None,
    ) -> dict[str, float]:
        """Calcula los indicadores individuales de una trayectoria."""
        primera = trayectoria.observaciones[0]
        ultima = trayectoria.observaciones[-1]
        distancia = trayectoria.calcular_distancia_total()
        desplazamiento = trayectoria.calcular_desplazamiento()
        tiempo_total = trayectoria.calcular_tiempo_total(fps)

        detenciones = self._detectar_detenciones(trayectoria, fps)
        tiempo_detenido = sum(map(lambda d: (d[1] - d[0]) / fps, detenciones))

        return { #Retornamos diccionario con los indicadores
            "x_inicial": primera.x,
            "y_inicial": primera.y,
            "x_final": ultima.x,
            "y_final": ultima.y,
            "tiempo_total_s": tiempo_total,
            "distancia_total_m": distancia,
            "desplazamiento_m": desplazamiento,
            "velocidad_media_ms": trayectoria.calcular_velocidad_media(fps),
            "velocidad_maxima_ms": trayectoria.calcular_velocidad_maxima(fps),
            "eficiencia": desplazamiento / distancia if distancia > 0 else 0.0,
            "cantidad_detenciones": float(len(detenciones)),
            "tiempo_detenido_s": tiempo_detenido,
            "porcentaje_detenido": (
                100 * tiempo_detenido / tiempo_total if tiempo_total > 0 else 0.0
            ),
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
            if velocidad < UMBRAL_VELOCIDAD:
                if inicio is None:
                    inicio = frame_i
                fin = frame_f
                
            else:
                if inicio is not None:
                    if (fin - inicio) / fps >= DURACION_MINIMA:
                        Listadetenciones.append((inicio, fin))
                inicio = None

        if inicio is not None:
            if (fin - inicio) / fps >= DURACION_MINIMA:
                Listadetenciones.append((inicio, fin))

        return Listadetenciones


    def promedio(resultados: dict[int, dict[str, float]], clave: str) -> float:
        suma = sum(r[clave] for r in resultados.values())
        return round(suma / len(resultados), 2)