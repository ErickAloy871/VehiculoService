"""
Generador del archivo ZIP oficial de entrega para la Guía Práctica 4 (APE 04).
Empaqueta todos los componentes de código fuente eliminando dependencias, binarios y cachés:
- Excluye: .git, .venv, node_modules, target, bin, obj, __pycache__, .idea, *.log, *.zip
"""
import os
import zipfile

OUTPUT_ZIP = "APE04_ENTREGA_CODIGO_FUENTE.zip"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCLUDE_DIRS = {
    ".git", ".venv", "node_modules", "target", "bin", "obj", 
    "__pycache__", ".idea", ".vscode", "dist", ".system_generated",
    "logs", "coverage"
}

EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".log", ".class", ".exe", ".dll", ".pdb", 
    ".cache", ".suo", ".user"
}

def debe_incluir(ruta_relativa):
    partes = ruta_relativa.replace("\\", "/").split("/")
    for p in partes:
        if p in EXCLUDE_DIRS:
            return False
    _, ext = os.path.splitext(ruta_relativa)
    if ext.lower() in EXCLUDE_EXTS:
        return False
    if ruta_relativa.endswith(".zip"):
        return False
    return True

def generar_zip():
    total_archivos = 0
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for raiz, directorios, archivos in os.walk(BASE_DIR):
            # Filtrar directorios en la marcha
            directorios[:] = [d for d in directorios if d not in EXCLUDE_DIRS]
            for archivo in archivos:
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, BASE_DIR)
                if debe_incluir(ruta_relativa):
                    z.write(ruta_completa, ruta_relativa)
                    total_archivos += 1

    tam_mb = os.path.getsize(OUTPUT_ZIP) / (1024 * 1024)
    print(f"ZIP generado exitosamente: {OUTPUT_ZIP}")
    print(f"Total de archivos incluidos: {total_archivos}")
    print(f"Tamaño del archivo comprimido: {tam_mb:.2f} MB")

if __name__ == "__main__":
    generar_zip()
