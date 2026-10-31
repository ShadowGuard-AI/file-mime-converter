![Banner](banner.png)

# file-mime-converter
Converts files between different MIME types using common conversion tools (e.g., using 'unoconv' for document formats), handling dependencies and reporting errors. - Focused on File operations and analysis

## Install
`git clone https://github.com/ShadowStrikeHQ/file-mime-converter`

## Usage
`python3 main.py input_file output_file [--target_mime TARGET_MIME] [--unoconv_path UNOCONV_PATH] [--debug]`

Example: `python3 main.py input.docx output.pdf --target_mime application/pdf`

Exit status: 0 only on a conversion that produced a non-empty output file. Any failure exits 1, including a missing or empty input, a converter failure, and a converter that exits 0 while producing no output or an empty output.

An empty input file is refused at exit 1 before the converter runs. An output path that resolves to the input file itself (the same path, a `./` alias, or a symlink to it) is refused at exit 1 before the converter runs.

A supplied `--target_mime` decides the conversion format through this map: application/pdf to pdf, text/plain to txt, text/html to html, application/vnd.oasis.opendocument.text to odt, application/vnd.openxmlformats-officedocument.wordprocessingml.document to docx, application/msword to doc, text/csv to csv, and application/rtf to rtf. If the mapped format and the output suffix disagree, the run is refused at exit 1. If neither `--target_mime` nor an output suffix yields a format, the run is refused at exit 1.

## Parameters
- `input_file`: The input file to convert (positional, required)
- `output_file`: The output file to save the conversion to (positional, required)
- `-h`: Show help message and exit
- `--target_mime`: The target MIME type for the conversion, mapped to a format as described above. If not specified, tries to infer from output file extension.
- `--unoconv_path`: Path to the unoconv executable. Defaults to 'unoconv'.
- `--debug`: Enable debug logging.

## License
Copyright (c) ShadowStrikeHQ
