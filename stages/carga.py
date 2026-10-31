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
        experimentos = self._cargar_experimentos(contexto.ruta_entrada, contexto.fps)        
        print(f"  {len(experimentos)} experimentos cargados exitosamente!!")
        return experimentos

    def _cargar_experimentos(self, ruta_entrada: Path, fps_contexto: float | None) -> list[Experimento]:
        if ruta_entrada.is_file():  
            archivos = [ruta_entrada]
        else:  
            archivos = sorted(ruta_entrada.glob("*.txt"))
            
        experimentos = []
        for archivo in archivos:
            observaciones = []
            fps = fps_contexto if fps_contexto is not None else 30.0
            
            with open(archivo, "r", encoding="utf-8") as arch:
                for linea in arch:
                    linea = linea.strip()
                    if not linea:
                        continue
                    
                    if linea.startswith("#"):  
                        if "framerate" in linea.lower():
                            try:
                 
                                partes_fps = linea.replace(":", " ").split()
                                for i, p in enumerate(partes_fps):
                                    if "framerate" in p.lower() and i + 1 < len(partes_fps):
                                        fps = float(partes_fps[i + 1])
                                        break
                            except (ValueError, IndexError):
                                pass
                        continue

                  
                    partes = linea.split()
                    if len(partes) < 4:  
                        continue
                    
                    try:
                        id_peaton = int(partes[0])
                        frame = int(partes[1])
                        x = float(partes[2])
                        y = float(partes[3])
                        z = float(partes[4]) if len(partes) > 4 else 0.0
                        
                        obs = Observacion(id_peaton, frame, x, y, z)
                        observaciones.append(obs)
                    except ValueError:
                      
                        continue

            print(f" {archivo.name}: con {len(observaciones)} observaciones, fps: {fps}")
            experimentos.append(
                Experimento(archivo.stem, fps, observaciones)
            )

        return experimentos