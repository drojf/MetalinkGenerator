import hashlib
import os
import argparse
from typing import List, BinaryIO
from urllib.parse import urljoin, quote


# metalink template based on opensuse metalink

# this is probably slow - but how do you reset the hash object otherwise?
def get_hash(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def get_partial_and_full_sha1_hash(file: BinaryIO, piece_size: int) -> (str, List[str], int):
    full_hash_generator = hashlib.sha1()

    filesize = 0
    chunk_hashes = []
    while (True):
        data = file.read(piece_size)
        if not data:
            break

        filesize += len(data)

        # update the piecewise full hash
        chunk_hashes.append(get_hash(data))
        full_hash_generator.update(data)

    return full_hash_generator.hexdigest(), chunk_hashes, filesize


def make_metalink(input_file_path: str, download_url: str, piece_size: int) -> str:
    """
    :param input_file_path: The path to the file for which a metalink should be generated
    :param download_url: The download url of the file
    :param piece_size: default = 16mb chunks
    :return: The metalink file as a str
    """
    with open(input_file_path, 'rb') as input_file:
        full_hash, chunk_hashes, filesize = get_partial_and_full_sha1_hash(input_file, piece_size)

    # convert hashes into xml format
    hashes_as_string = ''.join(['        <hash>{}</hash>\n'.format(x) for x in chunk_hashes])

    return \
        f"""<?xml version="1.0" encoding="UTF-8"?>
<metalink xmlns="urn:ietf:params:xml:ns:metalink">
  <file name="{os.path.split(input_file_path)[1]}">
    <size>{filesize}</size>
    <hash type="sha-1">{full_hash}</hash>
    <pieces length="{piece_size}" type="sha-1">
{hashes_as_string}    </pieces>
    <url>{download_url}</url>
  </file>
</metalink>
"""


def write_metalink_for_file(website_url: str, web_root_path: str, relative_path: str, piece_size: int):
    url = quote(urljoin(website_url, relative_path))

    metafile_output_path = relative_path + '.meta4'
    with open(os.path.join(web_root_path, metafile_output_path), 'w', encoding='utf-8') as outFile:
        outFile.write(make_metalink(relative_path, url, piece_size))

    print(f"Wrote metafile to [{metafile_output_path}]")


default_chunk_size = (1 << 24)

parser = argparse.ArgumentParser(description='Create a metalink from a given file')

parser.add_argument('path_relative_to_web_root', type=str,
                    help='Path of the file relative to the web root to have a metalink file generated')

parser.add_argument('--url_base', type=str, default='https://07th-mod.com',
                    help='Base URL which will be attached to the relative path to form the final download URL')

parser.add_argument('--web_root', type=str, default='/home/07th-mod/web/', help='Web root on the server')

parser.add_argument('--chunksize', type=int, default=default_chunk_size,
                    help='Piece size/Chunk size for calculating hashes (in bytes)')

args = parser.parse_args()

write_metalink_for_file(args.url_base, args.web_root, args.path_relative_to_web_root, args.chunksize)
