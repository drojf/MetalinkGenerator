import hashlib
import os

#user configurable items
download_url = 'http://test_url.exe' #specify url to download from
input_file_path = r'C:\games\Steam\steamapps\common\Umineko Chiru\Umineko5to8.exe' #specify file to be checksummed/metalink generated
# piece_size = 2 << 24
piece_size = 2 << 18

#template based on opensuse metalink
template = """<?xml version="1.0" encoding="UTF-8"?>
<metalink xmlns="urn:ietf:params:xml:ns:metalink">
  <file name="{filename}">
    <size>{filesize}</size>
    <hash type="sha-1">{full_hash}</hash>
    <pieces length="{piece_size}" type="sha-1">
{hashes}    </pieces>
    <url>{download_url}</url>
  </file>
</metalink>"""

#set the desired output filename (can be different from the url download path)
folder_path, filename = os.path.split(input_file_path)


#this is probably slow - but how do you reset the hash object otherwise?
def getHash(bytes):
    return hashlib.sha1(bytes).hexdigest()

#read chunk_size blocks of data from file
full_hash_generator = hashlib.sha1()

filesize = 0
checksums = []
with open(input_file_path, 'rb') as input_file:
    while(True):
        data = input_file.read(piece_size)
        if not data:
            break

        filesize += len(data)

        checksums.append(getHash(data))
        full_hash_generator.update(data)


#convert hashes into xml format
checksums_as_hash_list = ''.join(['        <hash>{}</hash>\n'.format(x) for x in checksums])


full_hash = full_hash_generator.hexdigest()

output = template.format(filename=filename, download_url=download_url, filesize=filesize, hashes=checksums_as_hash_list, full_hash=full_hash, piece_size=piece_size)

print(output)