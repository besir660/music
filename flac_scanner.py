import os
import sys
from collections import defaultdict
try:
    from mutagen.flac import FLAC, FLACNoHeaderError
except ImportError:
    print("Error: 'mutagen' library is not installed.")
    print("Please install it using: pip install mutagen")
    sys.exit(1)

def get_flac_resolution(file_path):
    """
    Reads a FLAC file and returns a formatted resolution string.
    Returns: (bits_per_sample, sample_rate_in_hz)
    """
    try:
        audio = FLAC(file_path)
        # audio.info contains the stream information
        return audio.info.bits_per_sample, audio.info.sample_rate
    except (FLACNoHeaderError, Exception) as e:
        # Return None if file is corrupt or not readable
        return None

def format_resolution(bits, rate):
    """Formats bits and rate into a readable string (e.g., '24-bit / 96.0 kHz')"""
    khz = rate / 1000.0
    # Format to remove .0 if it's an integer (e.g. 44.1 vs 44.0)
    khz_str = f"{khz:g}" 
    return f"{bits}-bit / {khz_str} kHz"

def scan_music_library(root_path):
    """
    Recursively scans folders. If a folder contains FLACs, determines the
    resolution of the album.
    """
    # Dictionary to store results: Key = Resolution String, Value = List of Folder Paths
    library_report = defaultdict(list)
    
    print(f"Scanning directory: {root_path} ...\n")

    for root, dirs, files in os.walk(root_path):
        # Filter for FLAC files in the current directory
        flac_files = [f for f in files if f.lower().endswith('.flac')]
        
        if not flac_files:
            continue

        # Check resolution of files in this folder
        folder_resolutions = set()
        
        for f in flac_files:
            full_path = os.path.join(root, f)
            res_data = get_flac_resolution(full_path)
            
            if res_data:
                folder_resolutions.add(res_data)

        if not folder_resolutions:
            continue

        # Determine how to categorize this folder
        if len(folder_resolutions) == 1:
            # All files match (Standard Album)
            bits, rate = list(folder_resolutions)[0]
            res_string = format_resolution(bits, rate)
            library_report[res_string].append(root)
        else:
            # Files have different resolutions (Mixed Album)
            # We create a string listing all found resolutions
            res_strings = [format_resolution(b, r) for b, r in sorted(folder_resolutions)]
            mixed_key = f"Mixed Resolutions ({', '.join(res_strings)})"
            library_report[mixed_key].append(root)

    return library_report

def print_report(report):
    if not report:
        print("No FLAC files found.")
        return

    print("-" * 60)
    print(f"{'RESOLUTION':<25} | {'ALBUM COUNT':<10}")
    print("-" * 60)

    # Sort by resolution (simple string sort, but groups similar types)
    for resolution in sorted(report.keys()):
        albums = report[resolution]
        print(f"{resolution:<25} | {len(albums)} albums")

    print("-" * 60)
    print("\nDETAILED LISTING:")
    
    for resolution in sorted(report.keys()):
        print(f"\n=== {resolution} ===")
        for album_path in sorted(report[resolution]):
            print(f"  - {album_path}")

if __name__ == "__main__":
    # Configuration: Set your path here or pass it as an argument
    target_directory = input("Enter the path to your music folder: ").strip()
    
    if os.path.isdir(target_directory):
        results = scan_music_library(target_directory)
        print_report(results)
    else:
        print("Invalid directory path provided.")
