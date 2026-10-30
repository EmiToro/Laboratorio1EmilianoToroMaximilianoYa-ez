from dataclasses import dataclass, field
from math import dist #Agregamos math.dist para hacer la suma de puntos

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
        return (dist(p[0], p[-1]) if len(p) >= 2 else 0.0)

    def calcular_velocidad_media(self, fps: float) -> float:
        if len(self.observaciones) < 2:
            return 0.0
        frames = self.observaciones[-1].frame - self.observaciones[0].frame
        tiempo = frames / fps
        return self.calcular_distancia_total() / tiempo if tiempo > 0 else 0.0


    def calcularTiempoTotal(self, fps: float) -> float: #Calculamos el tiempo observado en segundos
        if len(self.observaciones) < 2:
            return 0.0
        return (self.observaciones[-1].frame - self.observaciones[0].frame) / fps


    def calcularVelocidades(self, fps: float) -> list[float]: #Se calcula velocidades por peaton y se retornan con la lista velocidades
        p = self._puntos()
        velocidades = []
        for i in range(len(p) - 1):
            p1 = self.observaciones[i]
            p2 = self.observaciones[i + 1]
            distancia = dist(p[i], p[i+1])
            interTemp = (p2.frame - p1.frame) / fps
            if interTemp > 0:
                velocidades.append(distancia / interTemp)
        return velocidades


    def VelocidadMax(self, fps: float) -> float: #Calculamos la velocidad maxima y la retornamos
        vel = self.calcularVelocidades(fps)
        return (max(vel) if vel else 0.0)