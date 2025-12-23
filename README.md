# kobo-highlights-exporter
Extracts highlight annotations and notes from Kobo e-reader devices and exports them as formatted HTML files organized by book. Includes surrounding context from the original source material for better comprehension. 

## Features
- Connects to Kobo e-readers via USB to access highlight data.
- Extracts highlights, notes, and surrounding context from the Kobo database.
- Generates well-structured HTML files for each book with highlights and notes.
- Organizes exported files in a user-friendly directory structure.

## Requirements
- Python 3.6 or higher (tested on Python 3.12)
- BeautifulSoup4 library for HTML generation 
- Kobo e-reader device
- USB cable to connect the Kobo device to your computer

## Installation
1. Download the khe.py file to a dedicated folder on your local machine.
2. Intall BeautifulSoup4 if you haven't already: (`pip install beautifulsoup4`)

## Usage
1. Connect your Kobo e-reader to your computer via USB.
2. Ensure the device is mounted and accessible.
3. Run the script using Python:
   ```bash
   python khe.py
   ```
The script will detect the Kobo device, extract highlights and notes, and generate HTML files in the `Exported` directory.

## Output
The exported HTML files will look like this:

