import hashlib
import os
import argparse

outer_xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<metalink xmlns="urn:ietf:params:xml:ns:metalink">
{}
</metalink>
"""

#template based on opensuse metalink
file_xml_template = """
  <file name="{filename}">
    <size>{filesize}</size>
    <hash type="sha-1">{full_hash}</hash>
    <pieces length="{piece_size}" type="sha-1">
{hashes}    </pieces>
    <url>{download_url}</url>
  </file>
"""

file_nohash_xml_template =  """
  <file name="{filename}">
    <url>{download_url}</url>
  </file>
"""

#this is probably slow - but how do you reset the hash object otherwise?
def getHash(bytes):
    return hashlib.sha1(bytes).hexdigest()

def makePartialMetalinkForFile(input_file_path, download_url, piece_size):
    #set the desired output filename (can be different from the url download path)
    #for now just use the same name as the input_file_path filename
    folder_path, filename = os.path.split(input_file_path)

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

            #update the piecewise hash and the full hash
            checksums.append(getHash(data))
            full_hash_generator.update(data)


    #convert hashes into xml format
    checksums_as_hash_list = ''.join(['        <hash>{}</hash>\n'.format(x) for x in checksums])

    #get full hash of file
    full_hash = full_hash_generator.hexdigest()

    #substitute all the information into the xml template
    file_xml_output = file_xml_template.format(filename=filename, download_url=download_url, filesize=filesize, hashes=checksums_as_hash_list, full_hash=full_hash, piece_size=piece_size)

    return file_xml_output


parser = argparse.ArgumentParser(description='Create a metalink which downloads the urls listed in a text file (urlfile). This program will search the directory of the text file for files which match the download links in the text file.')
parser.add_argument('--urlfile', type=str, default='links.txt', help='Path to the text file containing URLs to be added to the metalink. The containing folder will be scanned for files.')
parser.add_argument('--chunksize', type=int, default=(2 << 21), help='Piece size/Chunk size for calculating checksums (in bytes)')
parser.add_argument('--outputpath', type=str, default=None, help='Filepath where the .meta4 file will be placed')

args = parser.parse_args()

if not os.path.exists(args.urlfile):
    print('[ERROR ] - Cant find input file [{}]'.format(args.urlfile))
    exit(-1)

print('Using\n > input file=[{}]\n > chunk size=[{} bytes/{}mb]'.format(args.urlfile, args.chunksize, args.chunksize/1024/1024))

absolute_path_to_urlfile = os.path.abspath(args.urlfile)
scan_folder, _ = os.path.split(absolute_path_to_urlfile)

print('Scanning directory',scan_folder, 'for input files to hash')

list_of_partial_metalinks = []

args_for_next_stage = []

fail_to_find_files = False

#iterate through each url in the urlfile
with open(args.urlfile, 'r', encoding='utf-8') as urlfile:
    for unstripped_line in urlfile:
        usehash = True

        line = unstripped_line.strip()

        splitline = line.split()

        url = splitline[0]
        _, _, filename = url.rpartition('/')

        if len(splitline) > 1:
            if splitline[1] == '~':
                usehash = False
            else:
                filename = splitline[1]

        #
        # #TODO: support spaces in filename
        # url = line
        # _, _, filename = line.rpartition('/')
        #
        # if len(splitline) != 1:
        #     url = splitline[0]
        #
        #     if splitline[1] == '~':
        #         usehash = False
        #
        #     else:
        #         filename = splitline[1]

        expected_file_path = os.path.join(scan_folder,filename)

        if os.path.exists(expected_file_path):
            print('[SUCCESS] - [{}]'.format(expected_file_path))
        else:
            print("[ERROR  ] - couldn't find [{}] - please make sure it exists so it can be hashed".format(expected_file_path))
            fail_to_find_files = True

        args_for_next_stage.append((expected_file_path, url, usehash))

if fail_to_find_files:
    print("\nExiting as couldn't find all files - METAFILE NOT WRITTEN")
    exit(-1)


for expected_file_path, url, usehash in args_for_next_stage:
    print('[Working] > Processing file {} '.format(expected_file_path))
    print('url:', url)

    #try to find the file in the scan folder
    if usehash:
        list_of_partial_metalinks.append(makePartialMetalinkForFile(expected_file_path, url, args.chunksize, ))
    else:
        _, temp_filename = os.path.split(expected_file_path)
        list_of_partial_metalinks.append(file_nohash_xml_template.format(download_url=url, filename=temp_filename))



#partial_xml = makePartialMetalinkForFile(input_file_path, download_url)
full_xml_output = outer_xml_template.format(''.join(list_of_partial_metalinks))

# print(full_xml_output)

metafile_name = 'download.meta4'
metafile_output_path = os.path.join(scan_folder, metafile_name)

if args.outputpath != None:
    metafile_output_path = args.outputpath

with open(metafile_output_path, 'w', encoding='utf-8') as outfile:
    outfile.write(full_xml_output)

print('\n\n[Finished] > Wrote metafile to [{}]'.format(metafile_output_path))
