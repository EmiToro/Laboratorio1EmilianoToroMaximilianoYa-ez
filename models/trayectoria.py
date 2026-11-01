from dataclasses import dataclass, field
from math import dist

from .observacion import Observacion


@dataclass
class Trayectoria:
    id_peaton: int
    observaciones: list[Observacion] = field(default_factory=list)

    def _puntos(self) -> list[tuple[float, float]]:
        return [(o.x, o.y) for o in self.observaciones]

    def calcular_distancia_total(self) -> float:
        p = self._puntos()
        return sum(dist(a, b) for a, b in zip(p, p[1:]))

    def calcular_desplazamiento(self) -> float:
        p = self._puntos()
        return dist(p[0], p[-1]) if len(p) >= 2 else 0.0

    def calcular_velocidad_media(self, fps: float) -> float:
        if len(self.observaciones) < 2 or fps <= 0:
            return 0.0

        obs = sorted(self.observaciones, key=lambda o: o.frame)

        frames = obs[-1].frame - obs[0].frame
        tiempo = frames / fps

        return self.calcular_distancia_total() / tiempo if tiempo > 0 else 0.0

    def calcularTiempoTotal(self, fps: float) -> float:
        if len(self.observaciones) < 2 or fps <= 0:
            return 0.0

        obs = sorted(self.observaciones, key=lambda o: o.frame)

        return (obs[-1].frame - obs[0].frame) / fps

    def calcularVelocidades(self, fps: float) -> list[tuple[int, int, float]]:
        velocidades = []

        if fps <= 0:
            return velocidades

        obs = sorted(self.observaciones, key=lambda o: o.frame)

        for anterior, actual in zip(obs, obs[1:]):
            distancia = dist(
                (anterior.x, anterior.y),
                (actual.x, actual.y)
            )

            tiempo = (actual.frame - anterior.frame) / fps

            if tiempo > 0:
                velocidades.append(
                    (anterior.frame, actual.frame, distancia / tiempo)
                )

        return velocidades

    def VelocidadMax(self, fps: float) -> float:
        velocidades = self.calcularVelocidades(fps)

        return max(
            (velocidad for frame_i, frame_f, velocidad in velocidades),
            default=0.0
        )

