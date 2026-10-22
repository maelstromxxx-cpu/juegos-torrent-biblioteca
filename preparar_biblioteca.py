"""Juegos Torrent - generador de biblioteca.json directamente en el repositorio.

Colocá este script en la raíz del clon de juegos-torrent-biblioteca,
al lado de imagenes/, capturas/ y sinopsis/. No copia ni borra recursos.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
CARPETAS = {
    'imagenes': {'.jpg', '.jpeg', '.png', '.webp'},
    'capturas': {'.jpg', '.jpeg', '.png', '.webp'},
    'sinopsis': {'.txt'},
}
LIMITE_BYTES = 12_000_000


def main() -> None:
    registros = []
    omitidos = 0
    for nombre, extensiones in CARPETAS.items():
        carpeta = BASE / nombre
        if not carpeta.is_dir():
            print(f'Aviso: no existe la carpeta {nombre}/')
            continue
        for archivo in sorted(carpeta.rglob('*')):
            if not archivo.is_file():
                continue
            if archivo.is_symlink() or archivo.suffix.lower() not in extensiones:
                omitidos += 1
                continue
            if any(parte.is_symlink() for parte in archivo.relative_to(BASE).parents if parte != Path('.')):
                omitidos += 1
                continue
            tamano = archivo.stat().st_size
            if tamano > LIMITE_BYTES:
                print(f'Omitido por tamaño: {archivo.relative_to(BASE)}')
                omitidos += 1
                continue
            sha = hashlib.sha256()
            with archivo.open('rb') as entrada:
                for bloque in iter(lambda: entrada.read(1024 * 1024), b''):
                    sha.update(bloque)
            registros.append({
                'path': archivo.relative_to(BASE).as_posix(),
                'size': tamano,
                'sha256': sha.hexdigest(),
            })

    if not registros:
        print('ERROR: no encontré archivos válidos. No se modificó biblioteca.json.')
        return

    destino = BASE / 'biblioteca.json'
    contenido = json.dumps({'schema': 1, 'files': registros}, ensure_ascii=False, indent=2) + '\n'
    if destino.exists() and destino.read_text(encoding='utf-8') == contenido:
        print(f'Biblioteca sin cambios: {len(registros)} archivos.')
    else:
        temporal = BASE / 'biblioteca.json.tmp'
        temporal.write_text(contenido, encoding='utf-8')
        temporal.replace(destino)
        print(f'Actualizado biblioteca.json: {len(registros)} archivos.')
    if omitidos:
        print(f'Archivos omitidos: {omitidos}.')
    print('Ahora abrí GitHub Desktop: Commit to main y Push origin.')


if __name__ == '__main__':
    main()
