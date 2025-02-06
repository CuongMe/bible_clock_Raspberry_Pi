import json
import time
import platform
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Detect if running on Windows
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    print("Running in Windows preview mode. Using dummy display.")


    class DummyInky:
        WIDTH = 800  # Set same resolution as Inky Impression
        HEIGHT = 480

        def __init__(self, color):
            self.color = color
            print(f"Dummy display initialized with color: {color}")

        def set_image(self, img):
            self.img = img

        def show(self):
            print("Previewing image using Pillow's default viewer.")
            self.img.show()


    inky_display = DummyInky("black")
else:
    from inky import InkyImpression

    inky_display = InkyImpression("red")  # Change to "black" or "yellow" if needed
    inky_display.set_border(inky_display.WHITE)

# Load Bible verses from JSON
with open("verses.json", "r", encoding="utf-8") as f:
    verses = json.load(f)

# Load fonts (Book Name Normal, Chapter & Verse Number Bold)
try:
    time_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)  # Large, Bold Time Display
    book_font = ImageFont.truetype("DejaVuSerif.ttf", 50)  # Book Name (Larger & Formal Serif)
    bold_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)  # Chapter & Verse Number (Bold & Bigger)
    verse_font = ImageFont.truetype("Times New Roman.ttf", 40)  # Verse Text (Larger & Classic)
except IOError:
    time_font = ImageFont.load_default()
    book_font = ImageFont.load_default()
    bold_font = ImageFont.load_default()
    verse_font = ImageFont.load_default()


def get_current_verse():
    """Fetch the current Bible verse based on the current time."""
    current_time = datetime.now().strftime("%H:%M")
    return current_time, verses.get(current_time, None)


def update_display():
    """Design the layout and update the display (or preview in Windows)."""

    # Fetch current time and verse
    current_time, verse_text = get_current_verse()

    # Create a blank image (simulate E-Ink resolution)
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    # Check if it's a whole hour (e.g., 1:00, 2:00)
    minutes = current_time.split(":")[1]
    if minutes == "00":
        # Whole Hour Case: Show only the time in large centered text
        text_w, text_h = draw.textbbox((0, 0), current_time, font=time_font)[2:]
        text_x = (inky_display.WIDTH - text_w) // 2
        text_y = (inky_display.HEIGHT - text_h) // 2
        draw.text((text_x, text_y), current_time, font=time_font, fill="black")

    else:
        # Regular Case: Show Bible verse
        if verse_text:
            # Extract book name and verse
            if " " in verse_text:
                book, rest = verse_text.split(" ", 1)  # Split book from the rest
                chapter_verse, verse_main = rest.split(" – ", 1) if " – " in rest else ("", rest)
            else:
                book, chapter_verse, verse_main = verse_text, "", ""

            # Center the Book Name (Normal Font)
            book_w, book_h = draw.textbbox((0, 0), book, font=book_font)[2:]
            book_x = (inky_display.WIDTH - book_w) // 2
            book_y = inky_display.HEIGHT // 3 - book_h // 2
            draw.text((book_x, book_y), book, font=book_font, fill="black")

            # Center the Chapter & Verse Number (Bold Font)
            if chapter_verse:
                cv_w, cv_h = draw.textbbox((0, 0), chapter_verse, font=bold_font)[2:]
                cv_x = (inky_display.WIDTH - cv_w) // 2
                cv_y = book_y + book_h + 10
                draw.text((cv_x, cv_y), chapter_verse, font=bold_font, fill="black")

            # Word-wrap the verse text
            max_width = inky_display.WIDTH - 40
            wrapped_lines = wrap_text(verse_main, verse_font, max_width)
            line_height = verse_font.getbbox("A")[3] - verse_font.getbbox("A")[1] + 10
            start_y = cv_y + cv_h + 20 if chapter_verse else book_y + book_h + 20

            for i, line in enumerate(wrapped_lines):
                text_width = draw.textbbox((0, 0), line, font=verse_font)[2]
                text_x = (inky_display.WIDTH - text_width) // 2
                draw.text((text_x, start_y + i * line_height), line, font=verse_font, fill="black")

    # Show the preview image on Windows or update Inky Impression
    inky_display.set_image(img)
    inky_display.show()


def wrap_text(text, font, max_width):
    """Wrap text to fit within the specified width."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


# Run preview once on Windows, loop on Raspberry Pi
if IS_WINDOWS:
    update_display()
else:
    while True:
        update_display()
        time.sleep(60)
