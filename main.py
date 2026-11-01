import argparse
import logging
import subprocess
import pathlib
import mimetypes
import os
import sys

MIME_TO_FORMAT = {
    'application/pdf': 'pdf',
    'text/plain': 'txt',
    'text/html': 'html',
    'application/vnd.oasis.opendocument.text': 'odt',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/msword': 'doc',
    'text/csv': 'csv',
    'application/rtf': 'rtf',
}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Converts files between different MIME types. Exits 1 on any failure: a missing or empty input, an output path that resolves to the input file, a target MIME type that disagrees with the output suffix, a missing format, a converter failure, or a converter that produces no non-empty output file.')
    parser.add_argument('input_file', type=str, help='The input file to convert.')
    parser.add_argument('output_file', type=str, help='The output file to save the conversion to.')
    parser.add_argument('--target_mime', type=str, help='The target MIME type for the conversion. If not specified, tries to infer from output file extension.')
    parser.add_argument('--unoconv_path', type=str, default='unoconv', help='Path to the unoconv executable. Defaults to \'unoconv\'.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')
    return parser.parse_args()


def convert_file(input_file, output_file, target_mime, unoconv_path):
    """
    Converts a file to a different MIME type using unoconv.

    Args:
        input_file (str): The path to the input file.
        output_file (str): The path to the output file.
        target_mime (str): The target MIME type for the conversion.
        unoconv_path (str): The path to the unoconv executable.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    try:
        # Input validation: Check if the input file exists
        input_path = pathlib.Path(input_file)
        if not input_path.is_file():
            logging.error(f"Input file not found: {input_file}")
            return False

        if input_path.stat().st_size == 0:
            logging.error(f"Input file is empty: {input_file}. Refusing to convert an empty input.")
            print("Input file is empty. Refusing to convert it.")
            return False

        # Refuse an output path that resolves to the input file itself.
        if pathlib.Path(output_file).resolve() == input_path.resolve():
            logging.error("Output path resolves to the input file. Refusing to convert a file over itself.")
            return False

        output_format = pathlib.Path(output_file).suffix.lstrip('.').lower()

        # A supplied target MIME type decides the format through the map.
        # Two ways to decide the format, and they are not symmetric. A supplied
        # MIME type must exist in the eight entry map and must agree with the
        # output suffix. With no MIME type, the suffix alone decides, and the
        # inferred MIME type is only logged: a suffix outside the map, such as
        # png, is passed to unoconv as a format and fails at the converter.
        if target_mime:
            mapped_format = MIME_TO_FORMAT.get(target_mime.strip().lower())
            if not mapped_format:
                logging.error(f"Unsupported target MIME type: {target_mime}. Supported types: {', '.join(sorted(MIME_TO_FORMAT))}.")
                return False
            if output_format and output_format != mapped_format:
                logging.error(f"Target MIME type {target_mime} maps to format '{mapped_format}', which disagrees with the output suffix '{output_format}'. Refusing.")
                return False
            output_format = mapped_format
            logging.info(f"Target MIME type {target_mime} mapped to format: {output_format}")
        else:
            if not output_format:
                logging.error("Could not determine a conversion format: no --target_mime was given and the output file has no suffix. Please specify --target_mime.")
                return False
            target_mime = mimetypes.guess_type(output_file)[0]
            if not target_mime:
                logging.error(f"Could not infer target MIME type from output file extension: {output_format}.  Please specify --target_mime.")
                return False
            logging.info(f"Inferred target MIME type: {target_mime}")

        if not output_format:
            logging.error("Could not determine a conversion format from --target_mime or the output suffix.")
            return False

        # Security best practice:  Sanitize input and output file names
        # Both paths are resolved to absolutes before the subprocess runs, so
        # the converter's working directory cannot change which files the
        # relative spellings meant. The command itself is an argv list, so no
        # path is ever shell interpreted.
        input_file = str(input_path.resolve()) # Get absolute path to prevent relative path vulnerabilities
        output_file = str(pathlib.Path(output_file).resolve())

        # Construct the unoconv command
        command = [
            unoconv_path,
            '-f', output_format,
            '-o', output_file,
            input_file
        ]

        # Execute the command
        logging.info(f"Executing command: {' '.join(command)}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Check the return code
        if process.returncode != 0:
            logging.error(f"Conversion failed with return code {process.returncode}")
            logging.error(f"Stdout: {stdout.decode()}")
            logging.error(f"Stderr: {stderr.decode()}")
            return False

        output_path = pathlib.Path(output_file)
        # A zero exit code from unoconv is not taken as proof. The output has
        # to exist and be non-empty, because a converter that quietly writes
        # nothing would otherwise be reported as a successful conversion.
        if not output_path.is_file() or output_path.stat().st_size == 0:
            logging.error(f"Converter exited 0 but produced no non-empty output file at: {output_file}")
            return False

        logging.info(f"Conversion successful. Output file: {output_file}")
        return True

    except FileNotFoundError as e:
        logging.error(f"Error: unoconv not found. Please ensure it is installed and in your PATH. {e}")
        return False
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        return False


def main():
    """
    Main function to parse arguments and perform the file conversion.
    """
    args = setup_argparse()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled.")

    if convert_file(args.input_file, args.output_file, args.target_mime, args.unoconv_path):
        print(f"File successfully converted to {args.output_file}")
    else:
        print("File conversion failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()


# Example Usage:
# python main.py input.docx output.pdf --target_mime application/pdf
# python main.py input.odt output.docx --unoconv_path /usr/bin/unoconv

# Offensive tool example (using unoconv to potentially trigger vulnerabilities in document processing):
# Note:  This is for educational purposes only.  Do not use for malicious activities.
# It's possible, although rare, that specially crafted documents can exploit vulnerabilities
# in document processing software.  Unoconv, by using LibreOffice/OpenOffice, *could* be
# a vector if such a vulnerability exists.
# python main.py malicious.doc transformed.pdf --target_mime application/pdf

# Example for specifying unoconv path.
# python main.py input.docx output.pdf --unoconv_path /opt/libreoffice7.5/program/soffice --target_mime application/pdf