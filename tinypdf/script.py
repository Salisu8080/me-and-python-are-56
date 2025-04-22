import os
import subprocess
import shutil

def compress_pdf(input_path, output_path, quality="screen"):
    """
    Compress a PDF file using Ghostscript with enhanced options.

    Parameters:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to save the compressed PDF file.
        quality (str): Compression quality. Options: "screen", "ebook", "printer", "prepress".
    """
    # Check if Ghostscript is installed
    gs_command = "gswin64c" if os.name == "nt" else "gs"
    if not shutil.which(gs_command):
        print("Ghostscript is not installed or not in the PATH. Please install it first.")
        return

    try:
        # Ghostscript command with enhanced compression options
        command = [
            gs_command,
            "-sDEVICE=pdfwrite",                     # Specify PDF output device
            "-dCompatibilityLevel=1.4",             # Set compatibility to PDF 1.4
            "-dPDFSETTINGS=/" + quality,            # Set compression quality
            "-dColorImageResolution=72",            # Reduce color image resolution (72 DPI for screen quality)
            "-dGrayImageResolution=72",             # Reduce grayscale image resolution
            "-dMonoImageResolution=72",             # Reduce monochrome image resolution
            "-dEmbedAllFonts=true",                 # Embed all fonts to reduce dependencies
            "-dSubsetFonts=true",                   # Subset fonts to reduce size
            "-dCompressFonts=true",                 # Compress embedded fonts
            "-dDownsampleColorImages=true",         # Downsample color images
            "-dDownsampleGrayImages=true",          # Downsample grayscale images
            "-dDownsampleMonoImages=true",          # Downsample monochrome images
            "-dNOPAUSE",                            # Disable interactive mode
            "-dBATCH",                              # Exit after completion
            "-dQUIET",                              # Suppress messages
            f"-sOutputFile={output_path}",          # Set output file
            input_path                              # Input file
        ]

        # Run the command
        subprocess.run(command, check=True)
        print(f"PDF compressed successfully! Saved as: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")

if __name__ == "__main__":
    # Input file path
    input_pdf = input("Enter the path to the input PDF file: ").strip()
    # Output file path
    output_pdf = input("Enter the path to save the compressed PDF file: ").strip()
    # Compression quality
    print("Choose compression quality:")
    print("1. screen  - Lowest file size, suitable for on-screen viewing.")
    print("2. ebook   - Good quality for eBooks, smaller size.")
    print("3. printer - High quality for printing.")
    print("4. prepress - High quality, large file size (best for prepress).")
    quality_options = {"1": "screen", "2": "ebook", "3": "printer", "4": "prepress"}
    quality = input("Enter the option (1-4): ").strip()
    quality = quality_options.get(quality, "screen")  # Default to "screen"

    # Check if the input file exists
    if not os.path.exists(input_pdf):
        print("The specified input file does not exist.")
    else:
        compress_pdf(input_pdf, output_pdf, quality)
