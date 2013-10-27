zvdrtools: my python VDR tools
=========

My bundle of VDR tools written in pure python for use mostly on systems without perl available (like OpenELEC).

__Requirements__: [python-xmltv](https://pypi.python.org/pypi/python-xmltv) lib

- __svdrpsend.py__ - module for communication with VDR with the Simple VDR Protocol (SVDRP).
Can be used as a standalone script.
- __make\_channel\_mapping.py__ - helper script for generating mappings between XMLTV and VDR channels ID.
For now generate mappings based on files provided by linux-sat.tv. Use `--help` to view all possible options.
- __import\_xmltv.py__ - script for importing tv schedule in XMLTV to VDR EPG.
XMLTV file provided by linux-sat.tv is supported for now. Use `--help` to view all possible options.
- __process\_ocram\_logos.py__ - [ocram picons.sh](https://github.com/ocram/picons/raw/master/picons.sh) processing
script. The picons can be downloaded from [ocram picons downloads](http://ocram.github.io/picons/downloads.html) page.
Use `--help` to view all possible options. Here is the example how to generate create symlinks shell file for your
vdr channels:

    `process_ocram_logos.py --out_mask="ln -s ./ocram/%(ocram_name)s \"%(vdr_name)s%(ocram_file_ext)s\"" > ocram_links.sh`
