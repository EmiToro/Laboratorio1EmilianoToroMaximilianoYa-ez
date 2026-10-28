"""Etapa de carga de varios experimentos."""

from pathlib import Path

from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline
from models.observacion import Observacion

class CargaExperimentos(EtapaPipeline[None, list[Experimento]]):

    def ejecutar(
        self,
        entrada: None,
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        print(f" Buscando experimentos!!: {contexto.ruta_entrada.resolve()}")
        experimentos = self._cargar_experimentos(contexto.ruta_entrada)        
        print(f"  {len(experimentos)} experimentos cargados exitosamente!!")
        return experimentos

    def _cargar_experimentos(self, ruta_entrada: Path) -> list[Experimento]:
        if ruta_entrada.is_file(): #Si es un archivo
            archivos = [ruta_entrada]
        else: #Si no
            archivos = sorted(ruta_entrada.glob("*.txt"))
        experimentos = []
        for archivo in archivos:
            observaciones = []
            fps = None
            arch = open(archivo, "r", encoding="utf-8")
            arch.readline()
            linea = arch.readline().strip()

            while linea != "":
                if linea.startswith("#"):  # cabecera
                    if "framerate" in linea and fps is None:
                        fps = float(linea.split(":")[1].split()[0])
                    continue
                

                partes = linea.split()
                if len(partes) < 4:  # Por si la linea esta vacia o incompleta
                    continue
                id = int(partes[0])
                frame = int(partes[1])
                x = float(partes[2])
                y = float(partes[3])
                obs = Observacion(id, frame, x, y)
                observaciones.append(obs)
            arch.close()

            print(f" {archivo.name}: con {len(observaciones)} observaciones, fps: {fps}")
            experimentos.append(
                Experimento(archivo.stem,fps,observaciones)
            )



        return experimentos
