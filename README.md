# Kobo Highlights Exporter
Why we underline things in books we read, to simply forget about them? 
Ths script extracts highlight annotations and notes from Kobo e-reader devices and exports them as formatted HTML files organized by book. 
It includes surrounding context from the original source material for better comprehension. 

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
1. Download `khe.py` to a dedicated folder on your local machine.
2. Install BeautifulSoup4 if you haven't already: (`pip install beautifulsoup4`)

## Usage
1. Connect your Kobo e-reader to your computer via USB.
2. Ensure the device is mounted and accessible.
3. Run the script using Python:
   ```bash
   python khe.py
   ```
The script will detect the Kobo device, extract highlights and notes, and generate HTML files in the `Exported` directory.

## Output
The exported HTML files (one for each book, containing its notes and highlights) will look something like this: 

<img width="870" height="502" alt="image" src="https://github.com/user-attachments/assets/abd27326-6f77-44cf-a605-48f2d7e78806" />

The highlights can be see in yellow, while the rest is given for context.

## Configuration
The user can choose how much context they need by editing either `context_paragraphs` or `context_words` in the `config.json` file. Such file is created the first time the script is run, and any modifications to it will be applied in subsequent runs.

<p align=center>&#9786;</p>

<p align=center>Why, thank you for asking!<br />👉 You can donate to all my projects <a href="https://www.buymeacoffee.com/unalignedcoder" target="_blank" title="buymeacoffee.com">here</a>👈</p>
