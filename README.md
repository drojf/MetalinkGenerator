# MetalinkGenerator

Tool to generate metalinks with hashes for each piece of the file (for distributing large files incase something goes wrong!)

## Known Problems

- When downloading a metalink with aria2c, it will always say "checksum error detected" when starting a download.
- Not many downloads support metalink files anymore. Aria2 supports metalink files. CURL used to support it, but it was removed some time ago.

## Limitations

- Only one file per metalink is supported
- The URL must contain the name of the file at the end (percent-encoding is allowed). Technically you can get around this by providing a dummy URL, then manually editing the metalink afterwards.

## Usage

### Example

`generateMetalink.py https://example.com/cat-picture.jpg` where the file `cat-picture.jpg` is placed next to this script.

The script will detect the filename from the last part of the URL (currently it cannot query the URL if the URL name doesn't match the filename name).

Then it will look for a file of the same name, calculate its chunk checksums, and write out the metalink.

You can optionally specify the chunk size (which defaults to 16MB) as below:

`generateMetalink.py https://example.com/cat-picture.jpg --chunksize 67108864` for 64MB chunk size

### More Details

Running the program as `python3 generateMetalink.py -h` will show more usage information.

