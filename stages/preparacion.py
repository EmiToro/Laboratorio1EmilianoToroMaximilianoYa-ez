"""Etapa de preparación de observaciones y trayectorias."""

from models.experimento import Experimento
from models.observacion import Observacion
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class PreparacionTrayectorias(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa validación, organización y reconstrucción de trayectorias."""

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Prepara las observaciones y trayectorias de cada experimento."""
        for expe in experimentos:
            total = len(expe.observaciones)
            validas = self._validar_observaciones(expe.observaciones)
            organizadas = self._organizar_observaciones(validas)

            expe.observaciones = validas
            expe.trayectorias = self._reconstruir_trayectorias(organizadas)
            print("Experimentos:")
            print(f" Descartados: {expe.nombre}: {total - len(validas)}")
            print(f" trayectorias de Peatones: {len(expe.trayectorias)}")
        return experimentos

    
    def _validar_observaciones(
        self,
        observaciones: list[Observacion],
    ) -> list[Observacion]:
        """Valida y retorna las observaciones de un experimento."""
        raise NotImplementedError

    def _organizar_observaciones(
        self,
        observaciones: list[Observacion],
    ) -> dict[int, list[Observacion]]:
        """Organiza las observaciones por identificador de peatón."""
        raise NotImplementedError

    def _reconstruir_trayectorias(
        self,
        observaciones_organizadas: dict[int, list[Observacion]],
    ) -> list[Trayectoria]:
        """Construye trayectorias desde las observaciones organizadas."""
        raise NotImplementedError
