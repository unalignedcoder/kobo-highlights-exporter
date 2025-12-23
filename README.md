# Kobo Highlights Exporter

Ths script extracts highlight annotations and notes from Kobo e-reader devices and exports them as formatted HTML files organized by book.
It includes surrounding context from the original source material for better comprehension.


<p align=center><img width="466" height="45" alt="image" src="https://github.com/user-attachments/assets/001f2885-5dbb-48b2-9e31-1f6715427f09" /></p>

## Features

Nothing is more frustrating than an incomplete or old highlight which we cannot place in context. 

This script allows the user to extracts highlights and notes, with **surrounding context from preceding sentences or paragraphs!**

Furthermore, it keeps track of the highlights that have already been exported, and will only extract new ones, until told otherwise.

The script generates well-structured HTML files for each book and organizes the exported files in a user-friendly directory structure.

## Requirements
- Python 3.6 or higher (tested on Python 3.12)
- BeautifulSoup4 library for HTML generation 
- Kobo e-reader device (tested on Kobo Aura)

## Compatibility
The script is designed to work on Windows, macOS and Linux systems, but to be honest it was only tested on Windows 10... Feedback on this will be really appreciated.

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

It will **never write anything on the device**, and, before reading its content, it will copy the kobo database locally.

## Output
The exported HTML files (one for each book, containing its notes and highlights) will look something like this: 

<img width="870" height="502" alt="image" src="https://github.com/user-attachments/assets/abd27326-6f77-44cf-a605-48f2d7e78806" />

The highlights can be seen in yellow, while the rest is given for context.

## Configuration
By editing `config.json`, The user can choose how much context they need by editing either `context_paragraphs` or `context_words`.
Other options are available as well (see picture below).
The config file is created the first time the script is run, and any modifications to it will be applied in subsequent runs.

<img width="697" height="607" alt="image" src="https://github.com/user-attachments/assets/a58da0c2-e879-42c3-8d4c-a0d25bcb1e35" />


<p align=center>&#9786;</p>

<p align=center>Why, thank you for asking!<br />👉 You can donate to all my projects <a href="https://www.buymeacoffee.com/unalignedcoder" target="_blank" title="buymeacoffee.com">here</a>👈</p>
