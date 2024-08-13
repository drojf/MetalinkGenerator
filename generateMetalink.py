import hashlib
import os
import argparse
from pathlib import Path
import sys
from typing import BinaryIO
from urllib.parse import urlparse, unquote


# metalink template based on opensuse metalink

# this is probably slow - but how do you reset the hash object otherwise?
def get_hash(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def get_partial_and_full_sha1_hash(file: BinaryIO, piece_size: int) -> tuple[str, list[str], int]:
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


def write_metalink_for_file(url: str, chunk_size: int):
    # Extract the filename from the URL (See https://stackoverflow.com/a/18727481/848627)
    path_with_encoded_characters = urlparse(url).path
    path = unquote(path_with_encoded_characters)
    filename = Path(path).name

    # Check the file to be checksummed actually exists before continuing
    if not os.path.exists(filename) or not os.path.isfile(filename):
        print(f"ERROR: Couldn't find file [{filename}] to generate metalink from (at [{os.path.abspath(filename)}])")
        print(f"HINT: To fix this, place the file next to this script (you can also download the file from [{url}] if the URL is live)")
        exit(-1)

    # Build and write the metafile to disk
    metafile_output_path = filename + '.meta4'
    metafile_as_string = make_metalink(filename, url, chunk_size)
    with open(os.path.join(metafile_output_path), 'w', encoding='utf-8') as outFile:
        outFile.write(metafile_as_string)

    print(f"Wrote metafile to [{metafile_output_path}]")
    print(f" - filename: [{filename}]")
    print(f" - url: [{url}]")
    print(f" - chunksize: {chunk_size} bytes")


default_chunk_size = (1 << 24)

parser = argparse.ArgumentParser(description='Create a metalink from a given URL. The file at the URL must be placed adjacent to the script. The URL does not have to be live. Example: [generateMetalink.py https://example.com/cat-picture.jpg] where "cat-picture.jpg" is placed next to this script.')

parser.add_argument('url', type=str,
                    help='URL of the file for which the metalink file will be generated. The part of the URL after')

parser.add_argument('--chunksize', type=int, default=default_chunk_size,
                    help=f'Piece size/Chunk size for calculating hashes (in bytes). Defaults to {default_chunk_size >> 20} MB. Higher values increase the amount (one chunk) that needs to be re-downloaded if an error occurs or (depending on the download tool used) if the download is paused. Lower values can make the metalink file unnecessarily large.')

# Make sure help is printed if you pass no arguments to this script
if len(sys.argv) <= 1:
    print("ERROR: You need pass the URL of the file for which the metalink will be generated.")
    print("------------------------------------")
    parser.print_help()
    exit(-1)

args = parser.parse_args()

write_metalink_for_file(args.url, args.chunksize)
