# MetalinkGenerator

Tool to generate metalinks with hashes for each piece of the file (for distributing large files incase something goes wrong!)

## Known Problems

- When downloading a metalink with aria2c, it will always say "checksum error detected" when starting a download.

## Usage

Running the program as `python3 generateMetalink.py -h` will show usage information.

The default arguments for `url_base` and `web_root` WILL be incorrect for your application - you must supply them, or modify the defaults in the python script.
