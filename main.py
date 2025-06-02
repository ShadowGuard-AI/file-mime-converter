import argparse
import logging
import subprocess
import pathlib
import mimetypes
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Converts files between different MIME types.')
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

        # Determine the output format from the file extension if target_mime is not provided
        if not target_mime:
            output_extension = pathlib.Path(output_file).suffix.lstrip('.')  # Remove leading dot
            target_mime = mimetypes.guess_type(output_file)[0]

            if not target_mime:
                logging.error(f"Could not infer target MIME type from output file extension: {output_extension}.  Please specify --target_mime.")
                return False
            logging.info(f"Inferred target MIME type: {target_mime}")

        # Security best practice:  Sanitize input and output file names
        input_file = str(input_path.resolve()) # Get absolute path to prevent relative path vulnerabilities
        output_file = str(pathlib.Path(output_file).resolve())

        # Construct the unoconv command
        command = [
            unoconv_path,
            '-f', str(pathlib.Path(output_file).suffix).lstrip('.'),  # Format is the file suffix
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