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

        frames = self.observaciones[-1].frame - self.observaciones[0].frame
        tiempo = frames / fps

        return self.calcular_distancia_total() / tiempo if tiempo > 0 else 0.0

    def calcularTiempoTotal(self, fps: float) -> float:
        if len(self.observaciones) < 2 or fps <= 0:
            return 0.0

        return (self.observaciones[-1].frame - self.observaciones[0].frame) / fps

    def calcularVelocidades(self, fps: float) -> list[tuple[int, int, float]]:
        velocidades = []

        p = self._puntos()

        for i in range(len(p) - 1):
            p1 = self.observaciones[i]
            p2 = self.observaciones[i + 1]

            distancia = dist(p[i], p[i + 1])
            tiempo = (p2.frame - p1.frame) / fps

            if tiempo > 0:
                velocidades.append((p1.frame, p2.frame, distancia / tiempo))

        return velocidades

    def VelocidadMax(self, fps: float) -> float:
        velocidades = self.calcularVelocidades(fps)
        return max(velocidades) if velocidades else 0.0