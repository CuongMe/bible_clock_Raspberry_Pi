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

# Directory for your custom fonts (EB Garamond)
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
REGULAR_FONT_PATH = os.path.join(FONT_DIR, "EBGaramond-Regular.ttf")
BOLD_FONT_PATH = os.path.join(FONT_DIR, "EBGaramond-Bold.ttf")

# For icons, we use DejaVu Sans Bold (system-wide installation)
ICON_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Setup Inky display (Inky Impression 7.3)
inky_display = auto()

# Load fonts
phrase_font = ImageFont.truetype(REGULAR_FONT_PATH, 20)    # For rotating Christian phrases (top left)
icon_font   = ImageFont.truetype(ICON_FONT_PATH, 28)         # For rotating Christian icons (top right)
verse_font  = ImageFont.truetype(REGULAR_FONT_PATH, 24)      # For Bible verses text
bold_font   = ImageFont.truetype(BOLD_FONT_PATH, 36)         # For Bible verse reference (displayed in red)
cross_font  = ImageFont.truetype(ICON_FONT_PATH, 36)         # For bottom crosses (using icon font)

# -----------------------------
# Define Rotating Phrases & Icons
# -----------------------------
CHRISTIAN_PHRASES = [
    "Faith Over Fear",
    "Jesus is King",
    "Walk by Faith",
    "Rejoice Always",
    "The Lord is My Shepherd",
    "God is Good All the Time",
    "Let Your Light Shine",
    "Christ is Enough",
    "Trust in the Lord",
    "God is With You",
    "Hope in Jesus",
    "Be Still and Know",
    "Love Never Fails",
    "God’s Grace is Sufficient",
    "Worthy is the Lamb",
    "Blessed Beyond Measure",
    "I Can Do All Things",
    "Saved by Grace",
    "Jesus Loves You",
    "Pray Without Ceasing",
    "Fear Not, For I Am With You",
    "Worship in Spirit and Truth",
    "God’s Love Never Fails",
    "Forgiven & Redeemed",
    "Seek First the Kingdom",
    "God’s Plan is Greater",
    "Mercy Triumphs Over Judgment",
    "The Cross is Enough",
    "The Joy of the Lord is My Strength",
    "Stand Firm in the Faith"
]

CHRISTIAN_ICONS = [
    "✝", "🕊", "📖", "🙏", "⛪", "🕯", "🎵", "🌿", "☀️", "🏆",
    "🎶", "🔥", "💖", "🌎", "⚓", "🌈", "🤍", "👑", "✨", "🛡"
]

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
# Main Bible Clock Loop Function
# -----------------------------
def bible_clock_loop():
    last_time_key = None

    while True:
        now = datetime.now()
        time_key = now.strftime("%H:%M")

        # Load Bible verses from JSON
        try:
            with open("bible_verse.json") as f:
                verses = json.load(f)
        except Exception as e:
            print("Error loading bible_verse.json:", e)
            verses = {}

        # Get verse info by current time key
        verse_info = verses.get(time_key, "No verse set for this time.")
        if "–" in verse_info:
            reference, verse_text = map(str.strip, verse_info.split("–", 1))
        else:
            reference = verse_info
            verse_text = ""

        # Only update if the time (minute) has changed
        if time_key != last_time_key:
            print(f"Updating display for {time_key}...")

            # Select a random phrase and a random icon
            christian_phrase = random.choice(CHRISTIAN_PHRASES)
            christian_icon = random.choice(CHRISTIAN_ICONS)

            # Create new blank canvas
            img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
            draw = ImageDraw.Draw(img)

            # Clear background to white
            draw.rectangle((0, 0, inky_display.WIDTH, inky_display.HEIGHT), fill=inky_display.WHITE)

            # ------------- Top Section -------------
            # Top Left: Display rotating Christian phrase
            draw.text((10, 10), christian_phrase, font=phrase_font, fill=inky_display.BLACK)

            # Top Right: Display rotating Christian icon
            icon_bbox = draw.textbbox((0, 0), christian_icon, font=icon_font)
            icon_width = icon_bbox[2] - icon_bbox[0]
            draw.text((inky_display.WIDTH - icon_width - 10, 10),
                      christian_icon, font=icon_font, fill=inky_display.BLACK)

            # Draw horizontal separator line
            draw.line([(0, 40), (inky_display.WIDTH, 40)], fill=inky_display.BLACK, width=2)

            # ------------- Center Section -------------
            # Center: Bible verse reference (red)
            ref_bbox = draw.textbbox((0, 0), reference, font=bold_font)
            ref_width = ref_bbox[2] - ref_bbox[0]
            ref_x = (inky_display.WIDTH - ref_width) // 2
            ref_y = 60  # Position below the line
            draw.text((ref_x, ref_y), reference, font=bold_font, fill=inky_display.RED)

            # Bible verse text (wrapped) in black
            verse_max_width = inky_display.WIDTH - 40
            lines = wrap_text(verse_text, verse_font, verse_max_width)
            line_height = verse_font.getbbox("Ay")[3]
            verse_start_y = ref_y + bold_font.getbbox("Ay")[3] + 10
            for i, line in enumerate(lines):
                line_bbox = draw.textbbox((0, 0), line, font=verse_font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (inky_display.WIDTH - line_width) // 2
                draw.text((line_x, verse_start_y + i * (line_height + 4)),
                          line, font=verse_font, fill=inky_display.BLACK)

            # ------------- Bottom Section -------------
            # Bottom: Draw three cross symbols using a reliable icon font
            cross_text = "✝   ✝   ✝"
            cross_bbox = draw.textbbox((0, 0), cross_text, font=cross_font)
            cross_width = cross_bbox[2] - cross_bbox[0]
            cross_x = (inky_display.WIDTH - cross_width) // 2
            cross_y = inky_display.HEIGHT - (cross_bbox[3] - cross_bbox[1]) - 20  # 20 px margin from bottom
            draw.text((cross_x, cross_y), cross_text, font=cross_font, fill=inky_display.BLACK)

            # Display the new image (full update)
            inky_display.set_image(img)
            inky_display.show()

            # Save the last displayed time key
            last_time_key = time_key

        # Refresh loop every 15 seconds
        time.sleep(15)

if __name__ == '__main__':
    bible_clock_loop()
