"""
================================================================================
KOBO HIGHLIGHTS EXPORTER
================================================================================
Version:        1.0.0
Author:         Unaligned Coder
Last Updated:   2025-12-22
License:        MIT

DESCRIPTION:
    Extracts highlight annotations and notes from Kobo e-reader devices and
    exports them as formatted HTML files organized by book. Includes surrounding
    context from the original source material for better comprehension.

FEATURES:
    - Automatic Kobo device detection (Only tested under Windows)
    - Intelligent export (only processes new highlights or notes since the last run)
    - Include context to the highlight based on word count or paragraph
    - HTML output with styling for readability
    - Automatic folder opening on completion
    - Comprehensive logging of all operations
    - Summary statistics of exports included

REQUIREMENTS:
    - Python 3.6+
    - beautifulsoup4 (pip install beautifulsoup4)
    - Kobo e-reader device with accessible database

USAGE:
    1. Connect Kobo device to computer via USB
    2. Run: python khe.py
    3. Follow prompts to select Kobo drive (auto-detected if available)
    4. Check 'Exported' folder for HTML files
    5. Edit config.json to customize behavior (optional)

CONFIGURATION:
    Edit config.json to customize:
    - kobo_drive: Path to Kobo device (auto-detected if empty)
    - export_dir: Output directory for HTML files
    - context_words: Words of context in word count mode (default: 30)
    - context_paragraphs: Paragraphs of context in paragraph mode (default: 0)
    - open_folder_on_finish: Auto-open export folder (default: true)

OUTPUT:
    Creates HTML files in the export directory with one file per book.
    Each file contains all highlights from that book with surrounding context,
    styled for easy reading.

TROUBLESHOOTING:
    - "Drive error" - Ensure Kobo is connected and accessible
    - Missing context - Source EPUB file not found or encrypted
    - No highlights found - Check that highlights exist on device or
      increase 'last_exported_id' in config.json

RELEASE-NOTES:
    - First version released with core functionality and logging.

================================================================================
"""
import sqlite3, zipfile, os, re, json, shutil, subprocess
from datetime import datetime
from bs4 import BeautifulSoup, Comment

# --- BASIC CONFIG -- See config.json for more ---
CONFIG_FILE = "config.json"
LOG_FILE = "export_history.log"

# ============================================================================
# LOGGING SYSTEM - Records all export operations -- with timestamps
# ============================================================================
def log(msg, level="INFO", verbose_flag=True):
    """
    Log messages to file always; log to console only if verbose_flag is True.
    Useful for keeping the terminal clean while maintaining a full history in the log file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [{level}] {msg}"
    
    # Always write to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")
    
    # Conditionally print to terminal
    if verbose_flag:
        print(formatted_msg)

# ======================================================================================
# CONFIGURATION MANAGEMENT - Loads default settings - Edit config.json to change this
# ======================================================================================
def load_config():
    """
    Load configuration from config.json, falling back to defaults if file missing.
    Settings include Kobo drive location, export directory, context extraction mode, etc.
    """
    defaults = {
        "kobo_drive": "",
        "temp_db_name": "kobo_temp.sqlite",
        "export_dir": "Exported",
        "context_paragraphs": 0,
        "context_words": 30,
        "max_context_words": 100,
        "last_exported_id": 0,
        "open_folder_on_finish": True,
        "verbose": False  # New: Set to True to see detailed progress in terminal
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return {**defaults, **json.load(f)}
    return defaults

# ============================================================================
# HIGHLIGHT PROCESSING - Wraps highlighted text in HTML <mark> tags
# ============================================================================
def fuzzy_highlight(text_content, highlight_text):
    """
    Locate and wrap the target highlight text in <mark> tags within the HTML content.
    Handles whitespace variations and falls back to simple string replacement if regex fails.
    """
    clean_hl = " ".join(highlight_text.split())
    escaped = re.escape(clean_hl)
    pattern = re.sub(r'\\ ', r'\\s+', escaped)
    try:
        return re.sub(f"({pattern})", r"<mark>\1</mark>", text_content, flags=re.IGNORECASE | re.DOTALL)
    except:
        return text_content.replace(highlight_text, f"<mark>{highlight_text}</mark>")

# ============================================================================
# CONTEXT EXTRACTION - Retrieves surrounding text from EPUB files
# ============================================================================
def get_context(epub_path, content_id, target_text, config, book_info):
    """
    Extract context around a highlighted passage from the EPUB file.
    Returns HTML content with two modes:
    - WORD COUNT MODE: Extracts a fixed number of words around the highlight
    - PARAGRAPH MODE: Extracts full paragraphs surrounding the highlight
    """
    if not epub_path or not os.path.exists(epub_path):
        return f"<em>[Source file missing/encrypted]</em>"
    
    try:
        parts = content_id.split('#')
        internal_file = re.sub(r'^\(\d+\)', '', parts[1] if len(parts) > 1 else parts[0])
        
        with zipfile.ZipFile(epub_path, 'r') as z:
            ziplist = z.namelist()
            matched_file = next((f for f in ziplist if internal_file in f), None)
            if not matched_file: return target_text

            with z.open(matched_file) as f:
                content = f.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(content, 'html.parser')
                
                for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                    comment.extract()

                all_blocks = soup.find_all(['p', 'div', 'li', 'blockquote', 'h1', 'h2', 'h3'])
                target_node_idx = -1
                clean_target = " ".join(target_text.split())
                
                for i, block in enumerate(all_blocks):
                    block_text = " ".join(block.get_text().split())
                    if clean_target[:30] in block_text:
                        target_node_idx = i
                        break
                
                if target_node_idx == -1: return target_text

                # --- WORD COUNT MODE ---
                if config.get("context_paragraphs", 0) == 0:
                    start_b = max(0, target_node_idx - 1)
                    end_b = min(len(all_blocks), target_node_idx + 2)
                    combined_text = " ".join([" ".join(all_blocks[i].get_text().split()) for i in range(start_b, end_b)])
                    
                    words = combined_text.split()
                    clean_target_words = clean_target.split()
                    
                    start_word_idx = -1
                    for i in range(len(words)):
                        if words[i:i+3] == clean_target_words[:3]:
                            start_word_idx = i
                            break
                    
                    if start_word_idx != -1:
                        buf = config.get("context_words", 30)
                        s = max(0, start_word_idx - buf)
                        e = min(len(words), start_word_idx + len(clean_target_words) + buf)
                        return "... " + " ".join(words[s:e]) + " ..."
                
                # --- PARAGRAPH MODE (or Fallback) ---
                num = max(1, config.get("context_paragraphs", 1))
                p_start = max(0, target_node_idx - num)
                p_end = min(len(all_blocks), target_node_idx + num + 1)
                return "".join([str(all_blocks[i]) for i in range(p_start, p_end)])

    except Exception as e:
        log(f"Error in context extraction for {book_info}: {e}", "ERROR", config.get("verbose"))
        return target_text

# ============================================================================
# MAIN EXECUTION - Kobo highlights export pipeline
# ============================================================================

config = load_config()
is_verbose = config.get("verbose", False)
log("--- Starting Export Session ---", verbose_flag=is_verbose)

# --- STEP 1: IDENTIFY KOBO DRIVE (Cross-Platform) ---
drive = config.get("kobo_drive")
if not drive or not os.path.exists(drive):
    detected = None
    if os.name == 'nt': # Windows
        import string
        detected = next((f"{l}:/" for l in string.ascii_uppercase if os.path.exists(os.path.join(f"{l}:/", ".kobo", "KoboReader.sqlite"))), None)
    else: # macOS / Linux
        mount_points = ["/Volumes", "/media", f"/media/{os.getlogin()}", f"/run/media/{os.getlogin()}"]
        for base in mount_points:
            if os.path.exists(base):
                for folder in os.listdir(base):
                    potential = os.path.join(base, folder)
                    if os.path.exists(os.path.join(potential, ".kobo", "KoboReader.sqlite")):
                        detected = potential; break
            if detected: break

    drive = input(f"Enter Kobo Drive (Detected: {detected}): ").strip() or detected
    if drive and os.name == 'nt' and not drive.endswith(":/"): drive += ":/"

if not drive or not os.path.exists(drive):
    log("Drive error. Exiting.", "CRITICAL")
    exit()

config["kobo_drive"] = os.path.abspath(drive)

# --- STEP 2: COPY KOBO DATABASE ---
temp_db = config["temp_db_name"]
shutil.copy2(os.path.join(drive, ".kobo", "KoboReader.sqlite"), temp_db)

# --- STEP 3: QUERY HIGHLIGHTS FROM DATABASE ---
conn = sqlite3.connect(temp_db)
cur = conn.cursor()
query = """
    SELECT CAST(b.BookmarkID AS INTEGER), b.VolumeID, b.ContentID, b.Text, b.Annotation, c.Title, c.Attribution
    FROM Bookmark b
    LEFT JOIN content c ON b.VolumeID = c.ContentID
    WHERE b.Text IS NOT NULL AND CAST(b.BookmarkID AS INTEGER) > ?
    GROUP BY b.BookmarkID
    ORDER BY CAST(b.BookmarkID AS INTEGER) ASC
"""
cur.execute(query, (int(config["last_exported_id"]),))
rows = cur.fetchall()

if not rows:
    log("No new highlights found.", verbose_flag=True)
    exit()

if not os.path.exists(config["export_dir"]): 
    os.makedirs(config["export_dir"])

# Statistics Counters
count_hl = 0
count_notes = 0
books_seen = set()
max_id = int(config["last_exported_id"])

# Get current export date/time
export_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- STEP 4: PROCESS EACH HIGHLIGHT ---
for b_id, vol_id, cont_id, txt, note, title, author in rows:
    clean_author = "Unknown Author" if not author else " ".join(reversed([s.strip() for s in author.split(',')])) if ',' in author else author
    clean_title = title if title else os.path.basename(vol_id)
    book_label = f"{clean_author} - {clean_title}"
    
    # Update Stats
    count_hl += 1
    if note: count_notes += 1
    books_seen.add(book_label)

    log(f"Exporting: {book_label}", verbose_flag=is_verbose)

    # Path Resolution (Cross-Platform)
    k_fn = os.path.basename(vol_id)
    epub_file = os.path.join(drive, vol_id.replace("file:///mnt/onboard/", "").replace("/", os.sep))
    if not os.path.exists(epub_file):
        epub_file = os.path.join(drive, ".kobo", "kepub", k_fn)

    ctx_html = get_context(epub_file, cont_id, txt, config, book_label)
    final_output = fuzzy_highlight(ctx_html, txt)
    
    # --- STEP 5: WRITE TO HTML FILE ---
    safe_fn = re.sub(r'[\\/*?:"<>|]', "", book_label)
    file_path = os.path.join(config["export_dir"], f"{safe_fn}.html")
    
    mode = "a" if os.path.exists(file_path) else "w"
    with open(file_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write(f"<html><head><meta charset='UTF-8'><style>body{{font-family:'Georgia',serif;line-height:1.7;max-width:850px;margin:auto;padding:30px;background:#fdfdfd;}} .header-section{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:30px;}} .title-author{{}} h1{{margin:0;padding:0;}} h3{{margin:5px 0 0 0;padding:0;}} .export-date{{font-size:0.75rem;color:#888;text-align:right;}} .note-block{{border-left:5px solid #3498db;padding:20px;margin:30px 0;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.05);}} mark{{background:#fff176;font-weight:normal;color:black;padding:2px;}} .user-note{{margin-top:15px;padding:12px;background:#eef7fe;border-radius:5px;font-style:italic;}}</style></head><body><div class='header-section'><div class='title-author'><h1>{clean_title}</h1><h3>{clean_author}</h3></div><div class='export-date'>Exported: {export_datetime}</div></div><hr>")
        
        f.write(f"<div class='note-block'>{final_output}")
        if note: 
            f.write(f"<div class='user-note'><b>My Note:</b> {note}</div>")
        f.write("</div>")
    
    if int(b_id) > max_id: 
        max_id = int(b_id)

# --- STEP 6: UPDATE CONFIGURATION AND CLEANUP ---
config["last_exported_id"] = max_id
with open(CONFIG_FILE, "w") as f: 
    json.dump(config, f, indent=4)

# FINAL SUMMARY MESSAGE
summary_msg = f"Exported {count_hl} highlights and {count_notes} notes from {len(books_seen)} books."
log(f"Done. {summary_msg} Last ID: {max_id}", verbose_flag=False)

# --- STEP 7: OPEN EXPORT FOLDER (Cross-Platform) ---
if config["open_folder_on_finish"]:
    if os.name == 'nt': # Windows
        os.startfile(config["export_dir"])
    elif hasattr(os, 'uname') and os.uname().sysname == 'Darwin': # macOS
        subprocess.call(['open', config["export_dir"]])
    else: # Linux
        try:
            subprocess.call(['xdg-open', config["export_dir"]])
        except:
            pass