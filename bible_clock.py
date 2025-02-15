#!/usr/bin/env python3
import json
import os
import time
import random
from datetime import datetime
from inky.auto import auto
from PIL import Image, ImageDraw, ImageFont

# Set up the font directory
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

# Load EB Garamond fonts
REGULAR_FONT_PATH = os.path.join(FONT_DIR, "EBGaramond-Regular.ttf")
BOLD_FONT_PATH = os.path.join(FONT_DIR, "EBGaramond-Bold.ttf")

# Setup for the Inky display
inky_display = auto()

# Load fonts
phrase_font = ImageFont.truetype(REGULAR_FONT_PATH, 20)  # Christian phrase
icon_font = ImageFont.truetype(BOLD_FONT_PATH, 32)       # Christian icon
verse_font = ImageFont.truetype(REGULAR_FONT_PATH, 24)   # Bible verses
bold_font = ImageFont.truetype(BOLD_FONT_PATH, 36)       # Chapter & verse reference
cross_font = ImageFont.truetype(BOLD_FONT_PATH, 36)

# Expanded Christian phrases (Top Left)
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

# Expanded Christian icons (Top Right)
CHRISTIAN_ICONS = ["✝", "🕊", "📖", "🙏", "⛪", "🕯", "🎵", "🌿", "☀️", "🏆",
                   "🎶", "🔥", "💖", "🌎", "⚓", "🌈", "🤍", "👑", "✨", "🛡"]

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

def bible_clock_loop():
    """Loop continuously: update display with Bible verse, Christian phrase, and icon."""
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

        # Retrieve verse info
        verse_info = verses.get(time_key, "No verse set for this time.")
        if "–" in verse_info:
            reference, verse_text = map(str.strip, verse_info.split("–", 1))
        else:
            reference = verse_info
            verse_text = ""

        # Only update the display if the time has changed
        if time_key != last_time_key:
            print(f"🕒 Updating display for {time_key}...")

            # Select a random Christian phrase and icon
            christian_phrase = random.choice(CHRISTIAN_PHRASES)
            christian_icon = random.choice(CHRISTIAN_ICONS)

            # Create a new blank canvas
            img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
            draw = ImageDraw.Draw(img)

            # Clear the canvas
            draw.rectangle((0, 0, inky_display.WIDTH, inky_display.HEIGHT), fill=inky_display.WHITE)

            # 🔹 Top Left: Christian Phrase
            draw.text((10, 10), christian_phrase, font=phrase_font, fill=inky_display.BLACK)

            # 🔹 Top Right: Christian Icon
            icon_bbox = draw.textbbox((0, 0), christian_icon, font=icon_font)
            icon_size = (icon_bbox[2] - icon_bbox[0], icon_bbox[3] - icon_bbox[1])
            draw.text((inky_display.WIDTH - icon_size[0] - 10, 10),
                      christian_icon, font=icon_font, fill=inky_display.BLACK)

            # Draw a horizontal line below the top section
            draw.line([(0, 40), (inky_display.WIDTH, 40)], fill=inky_display.BLACK, width=2)

            # Center: Bible verse reference (drawn in red)
            ref_bbox = draw.textbbox((0, 0), reference, font=bold_font)
            ref_size = (ref_bbox[2] - ref_bbox[0], ref_bbox[3] - ref_bbox[1])
            ref_x = (inky_display.WIDTH - ref_size[0]) // 2
            ref_y = 60
            draw.text((ref_x, ref_y), reference, font=bold_font, fill=inky_display.RED)

            # Bible verse text (wrapped)
            verse_max_width = inky_display.WIDTH - 40
            lines = wrap_text(verse_text, verse_font, verse_max_width)
            line_height = verse_font.getbbox("Ay")[3]
            verse_start_y = ref_y + ref_size[1] + 10
            for i, line in enumerate(lines):
                line_bbox = draw.textbbox((0, 0), line, font=verse_font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (inky_display.WIDTH - line_width) // 2
                draw.text((line_x, verse_start_y + i * (line_height + 4)),
                          line, font=verse_font, fill=inky_display.BLACK)

            # Bottom: Three cross symbols
            cross_text = "✝   ✝   ✝"
            cross_bbox = draw.textbbox((0, 0), cross_text, font=cross_font)
            cross_size = (cross_bbox[2] - cross_bbox[0], cross_bbox[3] - cross_bbox[1])
            cross_x = (inky_display.WIDTH - cross_size[0]) // 2
            cross_y = inky_display.HEIGHT - cross_size[1] - 10
            draw.text((cross_x, cross_y), cross_text, font=cross_font, fill=inky_display.BLACK)

            # Display the image
            inky_display.set_image(img)
            inky_display.show()

            # Store the last displayed time to avoid unnecessary updates
            last_time_key = time_key

        # Refresh every 15 seconds
        time.sleep(15)

if __name__ == '__main__':
    bible_clock_loop()
