import io
import logging
import os

import tarfile
from typing import IO

from fastapi import UploadFile 

METADATA_FILENAME = "files_metadata"

type ExtractedFileName = str
type DecodedFileContent = str
type ExtractedFilesDict = dict[ExtractedFileName, DecodedFileContent]

def __read_and_decode_file(fileobj: IO[bytes]) -> str:
    decoded_chunks = []
    while True:
        chunk = fileobj.read(8192)
        if not chunk:
            break
        decoded_chunks.append(chunk.decode())
    return "".join(decoded_chunks)

def extract_tar_gz_to_dict_of_files(data: bytes) -> ExtractedFilesDict:
    extracted_files: ExtractedFilesDict = {}

    with tarfile.open(fileobj=io.BytesIO(data), mode="r") as tar:
        for member in tar.getmembers():
            if member.isfile():
                file = tar.extractfile(member)
                if file:
                    filename = os.path.basename(member.name)
                    try:
                        with file:
                            extracted_files[filename] = __read_and_decode_file(file)
                    except UnicodeDecodeError:
                        logging.warning(f"Could not decode {filename} as UTF-8.")
    return extracted_files

def compress_files_to_tar_gz(files_from_request: list[UploadFile]) -> bytes:
    files: dict[str, bytes] = {}
    for file in files_from_request:
        file_content = file.file.read()
        if not file_content:
            file_content = b""
        files[file.filename] = file_content
    with io.BytesIO() as tar_gz_buffer:
        with tarfile.open(fileobj=tar_gz_buffer, mode="w:gz") as tar:
            for filename, file_content in files.items():
                fileobj = io.BytesIO(file_content)
                tarinfo = tarfile.TarInfo(name=filename)
                tarinfo.size = len(file_content)
                tar.addfile(tarinfo, fileobj)
        return tar_gz_buffer.getvalue()