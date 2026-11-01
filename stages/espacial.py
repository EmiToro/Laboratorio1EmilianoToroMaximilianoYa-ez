from collections import defaultdict
from math import dist

from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

# Los peatones caminan a lo largo del eje Y (el corredor mide ~14 m en Y
# y ~5 m en X), por eso las zonas y la línea de flujo se definen sobre Y.
SEGUNDOS_INTERVALO_FLUJO = 10


class AnalisisEspacial(EtapaPipeline[list[Experimento], list[Experimento]]):

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        for expe in experimentos:
            expe.zonas = self._analizar_zonas(expe, expe.fps)
            expe.densidad = self._calcular_densidad(expe, expe.fps)
            expe.flujo = self._calcular_flujo(expe, expe.fps)

            print(f"Análisis espacial completado para: {expe.nombre}")

        return experimentos

    def _analizar_zonas(
        self,
        experimento: Experimento,
        fps: float,
    ) -> dict:
        if not experimento.observaciones or fps <= 0:
            return {}

        xs = [o.x for o in experimento.observaciones]
        ys = [o.y for o in experimento.observaciones]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        ancho = max_x - min_x
        largo = max_y - min_y

        if largo <= 0:
            return {}

        # Tres tramos a lo largo del recorrido (eje Y)
        limites = [
            min_y,
            min_y + largo / 3,
            min_y + 2 * largo / 3,
            max_y
        ]

        zonas = {}

        for i in range(3):
            nombre = f"zona_{i + 1}"
            y_inicio = limites[i]
            y_fin = limites[i + 1]

            peatones = []
            velocidades = []
            tiempos = []

            for trayectoria in experimento.trayectorias:
                obs = sorted(trayectoria.observaciones, key=lambda o: o.frame)

                puntos = [
                    o for o in obs
                    if y_inicio <= o.y <= y_fin
                ]

                if len(puntos) < 2:
                    continue

                tiempo = (puntos[-1].frame - puntos[0].frame) / fps

                if tiempo <= 0:
                    continue

                distancia = sum(
                    dist((a.x, a.y), (b.x, b.y))
                    for a, b in zip(puntos, puntos[1:])
                )

                peatones.append(trayectoria.id_peaton)
                tiempos.append(tiempo)
                velocidades.append(distancia / tiempo)

            zonas[nombre] = {
                "peatones": len(set(peatones)),
                "velocidad_media": round(
                    sum(velocidades) / len(velocidades), 4
                ) if velocidades else 0.0,
                "tiempo_medio": round(
                    sum(tiempos) / len(tiempos), 3
                ) if tiempos else 0.0,
                "y_inicio": round(y_inicio, 3),
                "y_fin": round(y_fin, 3)
            }

        zonas["dimensiones"] = {
            "min_x": round(min_x, 3),
            "max_x": round(max_x, 3),
            "min_y": round(min_y, 3),
            "max_y": round(max_y, 3),
            "ancho": round(ancho, 3),
            "largo": round(largo, 3)
        }

        return zonas

    def _calcular_densidad(
        self,
        experimento: Experimento,
        fps: float,
    ) -> dict:
        if not experimento.observaciones or fps <= 0:
            return {"densidades": [], "densidad_media": 0.0}

        xs = [o.x for o in experimento.observaciones]
        ys = [o.y for o in experimento.observaciones]

        area = (max(xs) - min(xs)) * (max(ys) - min(ys))

        if area <= 0:
            return {"densidades": [], "densidad_media": 0.0}

        # Se agrupa una sola vez por frame (antes se recorrían todas las
        # observaciones por cada frame, lo que era muy lento).
        peatones_por_frame = defaultdict(set)
        for o in experimento.observaciones:
            peatones_por_frame[o.frame].add(o.id_peaton)

        frames = sorted(peatones_por_frame)
        intervalo = max(1, int(fps))

        densidades = []

        for frame in frames[::intervalo]:
            cantidad = len(peatones_por_frame[frame])
            densidad = cantidad / area

            densidades.append({
                "frame": frame,
                "tiempo": round(frame / fps, 3),
                "peatones": cantidad,
                "densidad": round(densidad, 4)
            })

        promedio = (
            sum(d["densidad"] for d in densidades) / len(densidades)
            if densidades else 0.0
        )

        return {
            "area_total": round(area, 3),
            "densidades": densidades,
            "densidad_media": round(promedio, 4)
        }

    def _calcular_flujo(
        self,
        experimento: Experimento,
        fps: float,
    ) -> dict:
        if not experimento.observaciones or fps <= 0:
            return {"flujo": 0.0, "cruces": 0}

        ys = [o.y for o in experimento.observaciones]
        linea = (min(ys) + max(ys)) / 2

        cruces = []

        for trayectoria in experimento.trayectorias:
            obs = sorted(trayectoria.observaciones, key=lambda o: o.frame)

            for anterior, actual in zip(obs, obs[1:]):
                if anterior.y < linea <= actual.y:
                    cruces.append(actual.frame)
                    break

                if anterior.y > linea >= actual.y:
                    cruces.append(actual.frame)
                    break

        if not cruces:
            return {
                "linea_transversal": round(linea, 3),
                "cruces": 0,
                "flujo": 0.0,
                "intervalos": []
            }

        cruces.sort()

        frames = [o.frame for o in experimento.observaciones]
        tiempo_total = (max(frames) - min(frames)) / fps

        flujo = len(cruces) / tiempo_total if tiempo_total > 0 else 0.0

        intervalo_frames = max(1, int(fps * SEGUNDOS_INTERVALO_FLUJO))
        inicio = min(frames)
        fin = max(frames)

        intervalos = []

        for frame_inicio in range(inicio, fin + 1, intervalo_frames):
            frame_fin = frame_inicio + intervalo_frames

            cantidad = sum(
                1 for frame in cruces
                if frame_inicio <= frame < frame_fin
            )

            intervalos.append({
                "tiempo_inicio": round(frame_inicio / fps, 3),
                "tiempo_fin": round(frame_fin / fps, 3),
                "cruces": cantidad,
                "flujo": round(cantidad / SEGUNDOS_INTERVALO_FLUJO, 4)
            })

        return {
            "linea_transversal": round(linea, 3),
            "cruces": len(cruces),
            "tiempo_total": round(tiempo_total, 3),
            "flujo": round(flujo, 4),
            "intervalos": intervalos
        }