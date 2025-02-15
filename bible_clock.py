#!/usr/bin/env python3
import json
import os
import time
import random
from datetime import datetime
from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Setup Font Paths and Display
# -----------------------------
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
REGULAR_FONT_PATH = os.path.join(FONT_DIR, "EBGaramond-Regular.ttf")
BOLD_FONT_PATH = os.path.join(FONT_DIR, "EBGaramond-Bold.ttf")
ICON_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Best for symbols

# Setup Inky display (Inky Impression 7.3)
inky_display = auto()

# Load fonts
phrase_font = ImageFont.truetype(REGULAR_FONT_PATH, 20)
icon_font   = ImageFont.truetype(ICON_FONT_PATH, 24)
verse_font  = ImageFont.truetype(REGULAR_FONT_PATH, 24)
bold_font   = ImageFont.truetype(BOLD_FONT_PATH, 36)
cross_font  = ImageFont.truetype(ICON_FONT_PATH, 36)

# -----------------------------
# Define Rotating Phrases & Icons
# -----------------------------
CHRISTIAN_PHRASES = [
    "Faith Over Fear", "Jesus is King", "Walk by Faith", "Rejoice Always", 
    "The Lord is My Shepherd", "God is Good All the Time", "Let Your Light Shine",
    "Trust in the Lord", "Hope in Jesus", "Be Still and Know"
]

CHRISTIAN_ICONS = ["✝", "†", "☧", "⚓", "⛪", "🕯", "📜"]  # Ensure Unicode support

# -----------------------------
# Helper Functions
# -----------------------------
def wrap_text(text, font, max_width):
    """Wrap text so that each line fits within max_width."""
    words = text.split()
    lines = []
    current_line = ""
    temp_img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    temp_draw = ImageDraw.Draw(temp_img)
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if temp_draw.textbbox((0, 0), test_line, font=font)[2] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# -----------------------------
# Main Bible Clock Loop Function (Optimized for Speed)
# -----------------------------
def bible_clock_loop():
    last_time_key = None  # Store last displayed time
    last_phrase = None    # Track last displayed phrase
    last_icon = None      # Track last displayed icon

    while True:
        now = datetime.now()
        time_key = now.strftime("%H:%M")  # Current time in HH:MM format

        # Load Bible verses from JSON
        try:
            with open("bible_verse.json") as f:
                verses = json.load(f)
        except Exception as e:
            print("Error loading bible_verse.json:", e)
            verses = {}

        # Get verse for the current time
        verse_info = verses.get(time_key, "No verse set for this time.")
        if "–" in verse_info:
            reference, verse_text = map(str.strip, verse_info.split("–", 1))
        else:
            reference = verse_info
            verse_text = ""

        # Select new phrase and icon
        christian_phrase = random.choice(CHRISTIAN_PHRASES)
        christian_icon = random.choice(CHRISTIAN_ICONS)

        # Only update the screen if the time, phrase, or icon has changed
        if time_key != last_time_key or christian_phrase != last_phrase or christian_icon != last_icon:
            print(f"Updating display at {time_key}...")

            # Create new blank canvas
            img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
            draw = ImageDraw.Draw(img)

            # Clear background
            draw.rectangle((0, 0, inky_display.WIDTH, inky_display.HEIGHT), fill=inky_display.WHITE)

            # 🔹 Top Left: Christian Phrase
            draw.text((10, 10), christian_phrase, font=phrase_font, fill=inky_display.BLACK)

            # 🔹 Top Right: Christian Icon
            icon_x = inky_display.WIDTH - 40  # Adjust position for better alignment
            draw.text((icon_x, 10), christian_icon, font=icon_font, fill=inky_display.BLACK)

            # Draw horizontal separator line
            draw.line([(0, 40), (inky_display.WIDTH, 40)], fill=inky_display.BLACK, width=2)

            # 🔹 Center: Bible Verse Reference (Red)
            ref_bbox = draw.textbbox((0, 0), reference, font=bold_font)
            ref_x = (inky_display.WIDTH - ref_bbox[2]) // 2
            ref_y = 60
            draw.text((ref_x, ref_y), reference, font=bold_font, fill=inky_display.RED)

            # 🔹 Bible Verse Text (Wrapped)
            verse_max_width = inky_display.WIDTH - 40
            lines = wrap_text(verse_text, verse_font, verse_max_width)
            verse_start_y = ref_y + bold_font.getbbox("Ay")[3] + 10
            for i, line in enumerate(lines):
                line_x = (inky_display.WIDTH - verse_font.getbbox(line)[2]) // 2
                draw.text((line_x, verse_start_y + i * 30), line, font=verse_font, fill=inky_display.BLACK)

            # 🔹 Bottom: Three Crosses
            cross_text = "✝   ✝   ✝"
            cross_x = (inky_display.WIDTH - 120) // 2  # Adjust for centering
            cross_y = inky_display.HEIGHT - 50
            draw.text((cross_x, cross_y), cross_text, font=cross_font, fill=inky_display.BLACK)

            # Display Update
            inky_display.set_image(img)
            inky_display.show()

            # Update last displayed values
            last_time_key = time_key
            last_phrase = christian_phrase
            last_icon = christian_icon

        time.sleep(5)  # Update every 5 seconds instead of 15

if __name__ == '__main__':
    bible_clock_loop()
