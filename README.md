# file-mime-converter
Converts files between different MIME types using common conversion tools (e.g., using 'unoconv' for document formats), handling dependencies and reporting errors. - Focused on File operations and analysis

## Install
`git clone https://github.com/ShadowStrikeHQ/file-mime-converter`

## Usage
`./file-mime-converter [params]`

## Parameters
- `-h`: Show help message and exit
- `--target_mime`: The target MIME type for the conversion. If not specified, tries to infer from output file extension.
- `--unoconv_path`: Path to the unoconv executable. Defaults to \
- `--debug`: Enable debug logging.

## License
Copyright (c) ShadowStrikeHQ
