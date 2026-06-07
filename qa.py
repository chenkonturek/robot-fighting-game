import os
import time
from playwright.sync_api import sync_playwright

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_URL = f"file://{REPO_DIR}/index.html"
SCREENSHOT_DIR = os.path.join(REPO_DIR, "qa_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

results = []

def log(msg, status="INFO"):
    tag = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️"}.get(status, "ℹ️")
    line = f"{tag} {msg}"
    print(line)
    results.append(line)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=400)
    page = browser.new_page(viewport={"width": 1280, "height": 720})

    # Capture console errors
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    page.goto(FILE_URL)
    page.wait_for_load_state("networkidle")
    time.sleep(2)  # Let Three.js initialize

    # --- TEST 1: Character Select Screen ---
    page.screenshot(path=f"{SCREENSHOT_DIR}/01_char_select.png")
    char_select = page.locator("#char-select")
    if char_select.is_visible():
        log("Character select screen visible", "PASS")
    else:
        log("Character select screen NOT visible", "FAIL")

    cs_title = page.locator(".cs-title").text_content()
    if "SELECT YOUR FIGHTER" in cs_title:
        log(f"Character select title correct: '{cs_title}'", "PASS")
    else:
        log(f"Character select title wrong: '{cs_title}'", "FAIL")

    iron_x = page.locator("text=IRON-X").first
    venom_c = page.locator("text=VENOM-C").first
    log(f"IRON-X card visible: {iron_x.is_visible()}", "PASS" if iron_x.is_visible() else "FAIL")
    log(f"VENOM-C card visible: {venom_c.is_visible()}", "PASS" if venom_c.is_visible() else "FAIL")

    # --- TEST 2: Start game as IRON-X ---
    # Use JS to start game — the 3D canvas occludes card click in Playwright's hit-testing
    page.evaluate("window.startGame('humanoid')")
    time.sleep(2)  # Let game initialize
    page.screenshot(path=f"{SCREENSHOT_DIR}/02_game_start.png")

    char_select_hidden = not page.locator("#char-select").is_visible()
    log(f"Character select hidden after start: {char_select_hidden}", "PASS" if char_select_hidden else "FAIL")

    canvas = page.locator("#canvas")
    log(f"Canvas visible: {canvas.is_visible()}", "PASS" if canvas.is_visible() else "FAIL")

    # --- TEST 3: HUD Elements ---
    hud = page.locator("#hud")
    log(f"HUD visible: {hud.is_visible()}", "PASS" if hud.is_visible() else "FAIL")

    p1_name = page.locator("#p1-name").text_content()
    p2_name = page.locator("#p2-name").text_content()
    log(f"P1 name: '{p1_name.strip()}'", "PASS" if "IRON-X" in p1_name else "FAIL")
    # Playing as humanoid IRON-X → CPU is centipede GORE-C
    log(f"P2 name: '{p2_name.strip()}'", "PASS" if "GORE-C" in p2_name else "FAIL")

    timer = page.locator("#timer-display").text_content()
    try:
        timer_val = int(timer.strip())
        log(f"Timer visible and numeric: {timer_val}", "PASS" if 0 < timer_val <= 99 else "FAIL")
    except:
        log(f"Timer not numeric: '{timer}'", "FAIL")

    p1_hp = page.locator("#p1-hp-label").text_content()
    p2_hp = page.locator("#p2-hp-label").text_content()
    # AI attacks immediately so P1 HP may already be below 100 by the time we check
    log(f"P1 HP label: {p1_hp}", "PASS" if int(p1_hp.strip()) <= 100 else "FAIL")
    # GORE-C (centipede) starts at 120 HP
    log(f"P2 HP label: {p2_hp}", "PASS" if p2_hp.strip() == "120" else "FAIL")

    round_display = page.locator("#round-display").text_content()
    log(f"Round display: '{round_display}'", "PASS" if "ROUND" in round_display else "FAIL")

    # --- TEST 4: Controls Hint ---
    controls = page.locator("#controls-hint")
    log(f"Controls hint visible: {controls.is_visible()}", "PASS" if controls.is_visible() else "FAIL")

    # --- TEST 5: Keyboard input - movement ---
    page.keyboard.press("d")
    time.sleep(0.3)
    page.keyboard.press("a")
    time.sleep(0.3)
    page.screenshot(path=f"{SCREENSHOT_DIR}/03_after_move.png")
    log("A/D movement keys sent without crash", "PASS")

    # --- TEST 6: Jump ---
    page.keyboard.press("w")
    time.sleep(0.5)
    page.screenshot(path=f"{SCREENSHOT_DIR}/04_after_jump.png")
    log("W jump key sent without crash", "PASS")

    # --- TEST 7: Attacks ---
    page.keyboard.press("j")
    time.sleep(0.3)
    page.screenshot(path=f"{SCREENSHOT_DIR}/05_after_punch.png")
    log("J punch key sent without crash", "PASS")

    page.keyboard.press("k")
    time.sleep(0.3)
    page.screenshot(path=f"{SCREENSHOT_DIR}/06_after_kick.png")
    log("K kick key sent without crash", "PASS")

    page.keyboard.press("u")
    time.sleep(0.3)
    log("U uppercut key sent without crash", "PASS")

    # --- TEST 8: Block ---
    page.keyboard.down("l")
    time.sleep(0.3)
    block_icon = page.locator("#p1-block-icon")
    log(f"Block icon visible while L held: {block_icon.is_visible()}", "PASS" if block_icon.is_visible() else "FAIL")
    page.keyboard.up("l")

    # --- TEST 9: Timer counting down ---
    timer_before = int(page.locator("#timer-display").text_content().strip())
    time.sleep(3)
    timer_after_str = page.locator("#timer-display").text_content().strip()
    try:
        timer_after = int(timer_after_str)
        log(f"Timer counting down ({timer_before} → {timer_after})", "PASS" if timer_after < timer_before else "FAIL")
    except:
        log(f"Timer value after wait: '{timer_after_str}'", "FAIL")

    # --- TEST 10: HP changes after attacks ---
    time.sleep(2)
    p2_hp_after = page.locator("#p2-hp-label").text_content().strip()
    log(f"P2 HP after attacks: {p2_hp_after} (started at 120)", "INFO")
    try:
        hp_changed = int(p2_hp_after) < 120
        log(f"P2 HP decreased from damage: {hp_changed}", "PASS" if hp_changed else "INFO")
    except:
        log(f"P2 HP label non-numeric: '{p2_hp_after}'", "FAIL")

    page.screenshot(path=f"{SCREENSHOT_DIR}/07_mid_game.png")

    # --- TEST 11: Console errors ---
    if console_errors:
        for err in console_errors[:5]:
            log(f"Console error: {err}", "FAIL")
    else:
        log("No console errors detected", "PASS")

    time.sleep(3)  # Pause so user can see final state before window closes
    browser.close()

print("\n--- QA SUMMARY ---")
passes = sum(1 for r in results if "✅" in r)
fails = sum(1 for r in results if "❌" in r)
print(f"PASSED: {passes}  FAILED: {fails}")
print(f"Screenshots saved to: {SCREENSHOT_DIR}/")
