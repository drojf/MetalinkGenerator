# MetalinkGenerator
Tool to generate metalinks with hashes for each piece of the file (for distributing large files incase something goes wrong!)


# Known Problems
- I tested both the OpenSuse official metalink and my generated metalink using aria2c. Both worked, but both also give a "checksum error detected" when the download starts. 
The download completes normally, so I'm really not sure what's going on. The OpenSuse metalink is generated with MirrorBrain.

- The program doesn't currently support spaces in output filenames


# Usage
The program expects a file (called the 'urlfile') containing the list of download urls (by default called 'links.txt'). You can specify the file using the `--urlfile` argument.

An example file is shown below:

```
http://test.com/a.bmp
http://test.com/not_hashed.bmp ~
http://test.com/a43&j2l3k4j saved_filename.exe
```

The first line will cause the program to search the directory where the 'urlfile' is in for a file called `a.bmp`. The file will then be hashed and added to the metafile.

The second line with the `~` separated by a space will not try to hash the file, and will directly add the url to the metafile (no file checks are performed for size/hash)

The third line is used when the download url doesn't match the desired filename. The program will search for `saved_filename.exe` in the directory where the 'urlfile' is to calculate the checksum, but still try to download the file from the given URL. When a downloader downloads the file, it will be saved with the name `saved_filename.exe`

## Arguments

usage: generateMetalink.py [-h] [--urlfile URLFILE] [--chunksize CHUNKSIZE] [--outputpath OUTPUTPATH]

--urlfile (default:'links.txt') -> The filepath of the urlfile containing the list of urls. The folder the urlfile is in will be searched for files to compute the checksums (sha-1)

--chunksize (default: 8mb) -> The size of the pieces which the file will be divided into for hashing (each chunk will get one hash). The final chunk may be smaller than the other chunks, but you don't need to worry about that - it is handled automatically.

--outputpath (default: 'download.meta4') -> This is the full path to where the metalink file will be output.


