"""
Umamusume skill-page text capture (macOS).
Scrolls up with Quartz drag and OCRs *all* text on each page.

You can later parse the raw text files to find skill titles, etc.
"""

import time, os
from typing import List
import pyautogui
import pytesseract
from PIL import Image
import cv2, numpy as np

# ---- Quartz drag ----
from Quartz.CoreGraphics import (
    CGEventCreateMouseEvent, kCGEventLeftMouseDown, kCGEventLeftMouseDragged,
    kCGEventLeftMouseUp, kCGHIDEventTap, CGEventPost, kCGMouseButtonLeft
)

def macos_drag(x1, y1, x2, y2, steps=30, delay=0.01):
    """Perform a real HID-level drag gesture on macOS."""
    def event(t, x, y):
        e = CGEventCreateMouseEvent(None, t, (x, y), kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, e)
    event(kCGEventLeftMouseDown, x1, y1)
    time.sleep(0.05)
    for i in range(steps + 1):
        nx = x1 + (x2 - x1) * i / steps
        ny = y1 + (y2 - y1) * i / steps
        event(kCGEventLeftMouseDragged, nx, ny)
        time.sleep(delay)
    event(kCGEventLeftMouseUp, x2, y2)
# ----------------------


# -------- CONFIG --------
LOGICAL_TOP_LEFT = (1456, 320)
LOGICAL_BOTTOM_RIGHT = (1610, 600)
SCALE = 1
MAX_PAGES = 12
DRAG_DISTANCE = 140
DRAG_STEPS = 35
DRAG_DELAY = 0.01
PAUSE_AFTER_DRAG = 1.2
SAVE_SCREENSHOTS = True

TESSERACT_PATHS = [
    "/opt/homebrew/bin/tesseract",
    "/usr/local/bin/tesseract",
    "/usr/bin/tesseract",
]
LANG = "eng"
# ------------------------


def _set_tesseract_path():
    for p in TESSERACT_PATHS:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            return


def logical_region_to_pixels(tl, br, scale):
    left = int(tl[0] * scale)
    top = int(tl[1] * scale)
    width = int((br[0] - tl[0]) * scale)
    height = int((br[1] - tl[1]) * scale)
    print(f"Using region (left={left}, top={top}, w={width}, h={height})")
    return (left, top, width, height)


def grab_region(region_pixels):
    return pyautogui.screenshot(region=region_pixels)


def preprocess_for_ocr(pil_img: Image.Image) -> np.ndarray:
    img = np.array(pil_img)[:, :, ::-1]
    img = cv2.resize(img, None, fx=1.75, fy=1.75, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, d=7, sigmaColor=75, sigmaSpace=75)
    thr = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41, 11
    )
    return thr


def ocr_all_text(thr_img: np.ndarray) -> str:
    """Return the full OCR text (no filtering)."""
    cfg = "--oem 1 --psm 6"
    text = pytesseract.image_to_string(thr_img, lang=LANG, config=cfg)
    return text


def collect_all_text() -> List[str]:
    _set_tesseract_path()
    region = logical_region_to_pixels(LOGICAL_TOP_LEFT, LOGICAL_BOTTOM_RIGHT, SCALE)
    pyautogui.PAUSE = 0.1

    start_x = region[0] + region[2] // 2
    start_y = region[1] + region[3] // 2

    os.makedirs("skill_pages", exist_ok=True)
    os.makedirs("skill_texts", exist_ok=True)

    all_text_blocks = []

    for page in range(MAX_PAGES):
        # 1️⃣ Screenshot
        shot = grab_region(region)
        if SAVE_SCREENSHOTS:
            shot.save(f"skill_pages/page_{page+1:02d}.png")

        # 2️⃣ OCR everything
        thr = preprocess_for_ocr(shot)
        text = ocr_all_text(thr).strip()
        if text:
            all_text_blocks.append(text)
            with open(f"skill_texts/page_{page+1:02d}.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[Page {page+1}] captured text length: {len(text)} chars")
        else:
            print(f"[Page {page+1}] no text detected")

        # 3️⃣ Drag upward for next page
        print("Dragging up for next set...")
        macos_drag(start_x, start_y, start_x, start_y - DRAG_DISTANCE,
                   steps=DRAG_STEPS, delay=DRAG_DELAY)
        time.sleep(PAUSE_AFTER_DRAG)

    return all_text_blocks


if __name__ == "__main__":
    try:
        for i in range(3):
            pyautogui.click(1538, 215)
        texts = collect_all_text()
        print("\n=== OCR COMPLETE ===")
        total_chars = sum(len(t) for t in texts)
        print(f"Captured {len(texts)} pages, total {total_chars} characters.")
        print("Raw text files saved to ./skill_texts/")
    except KeyboardInterrupt:
        print("\nStopped by user.")
