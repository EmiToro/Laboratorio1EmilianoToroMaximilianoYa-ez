
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
            fps = expe.fps

            for trayectoria in expe.trayectorias:
                trayectoria.indicadores = self._calcular_indicadores(
                    trayectoria, fps
                )

                trayectoria.detenciones = self._detectar_detenciones(
                    trayectoria, fps
                )

            print(
                f"Análisis individual completado para: {expe.nombre} "
                f"({len(expe.trayectorias)} trayectorias analizadas)"
            )

        return experimentos

    def _calcular_indicadores(
        self,
        trayectoria: Trayectoria,
        fps: float,
    ) -> dict[str, float]:

        obs = sorted(trayectoria.observaciones, key=lambda o: o.frame)

        if not obs or fps <= 0:
            return {}

        pos_inicial = (obs[0].x, obs[0].y)
        pos_final = (obs[-1].x, obs[-1].y)

        tiempo_total = (
            (obs[-1].frame - obs[0].frame) / fps
            if len(obs) > 1 else 0.0
        )

        distancia_total = trayectoria.calcular_distancia_total()
        desplazamiento = trayectoria.calcular_desplazamiento()
        velocidad_media = trayectoria.calcular_velocidad_media(fps)

        eficiencia = (
            desplazamiento / distancia_total
            if distancia_total > 0 else 0.0
        )

        velocidad_maxima = trayectoria.VelocidadMax(fps)

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
        fps: float,
    ) -> list[tuple[int, int]]:

        lista_detenciones = []
        inicio = None
        fin = None

        if fps <= 0:
            return lista_detenciones

        observaciones = sorted(
            trayectoria.observaciones,
            key=lambda o: o.frame
        )

        for i in range(len(observaciones) - 1):

            p1 = observaciones[i]
            p2 = observaciones[i + 1]

            tiempo = (p2.frame - p1.frame) / fps

            if tiempo <= 0:
                continue

            distancia = math.dist(
                (p1.x, p1.y),
                (p2.x, p2.y)
            )

            velocidad = distancia / tiempo

            if velocidad <= VelUmbral:

                if inicio is None:
                    inicio = p1.frame

                fin = p2.frame

            else:

                if inicio is not None:
                    duracion = (fin - inicio) / fps

                    if duracion >= duraMin:
                        lista_detenciones.append((inicio, fin))

                inicio = None
                fin = None

        if inicio is not None:
            duracion = (fin - inicio) / fps

            if duracion >= duraMin:
                lista_detenciones.append((inicio, fin))

        return lista_detenciones

    @staticmethod
    def promedio(
        resultados: dict[int, dict[str, float]],
        clave: str
    ) -> float:

        if not resultados:
            return 0.0

        suma = sum(r[clave] for r in resultados.values())

        return round(suma / len(resultados), 2)
