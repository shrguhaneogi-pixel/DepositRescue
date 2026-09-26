import asyncio
import os
import re
import sys
import json
import subprocess
from pathlib import Path
import edge_tts
from imageio_ffmpeg import get_ffmpeg_exe
from playwright.async_api import async_playwright

# Add root directory to python path
sys.path.insert(0, str(Path(__file__).parent))

from api.core.schemas import AuditRequest
from api.index import audit_landlord_statement

FFMPEG_EXE = get_ffmpeg_exe()

VOICEOVERS = {
    "vo1": (
        "Welcome to DepositRescue, a tool designed to help tenants reclaim unfairly withheld security deposits. "
        "Today, I'll walk you through our core feature: the automated dispute ledger. "
        "As you can see, the minimalist interface focuses entirely on getting the user exactly what they need without overwhelming text."
    ),
    "vo2": (
        "Let's test the system live. I'm pasting an actual message a landlord might send. "
        "I am entering the data live, rather than using a pre-filled form, to demonstrate the real-time processing."
    ),
    "vo3": (
        "Here we see the real results rendered immediately. "
        "Notice how the system easily handles standard inputs, but also gracefully catches invalid entries when we test edge cases."
    ),
    "vo4": (
        "Generative AI is the core engine here. When I submit this complex text, we are sending a prompt directly to the Groq LLM running Llama 3. "
        "The AI's job is to parse unstructured, messy human complaints and extract structured JSON data. "
        "It dynamically separates the legitimate damage—like the punched wall—from illegal routine maintenance deductions like dust and floor wear."
    ),
    "vo5": (
        "By combining the LLM's extraction with our backend deterministic legal math, the tenant gets an immediate, accurate ledger ready for small claims court. "
        "Thank you for watching this demonstration of DepositRescue."
    )
}

def get_audio_duration(file_path):
    cmd = [FFMPEG_EXE, "-i", file_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if match:
        h, m, s = map(float, match.groups())
        return h * 3600 + m * 60 + s
    return 0.0

async def generate_voiceovers():
    os.makedirs("audio_temp", exist_ok=True)
    durations = {}
    for key, text in VOICEOVERS.items():
        out_path = f"audio_temp/{key}.mp3"
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="-2%")
        await communicate.save(out_path)
        dur = get_audio_duration(out_path)
        durations[key] = dur
        print(f"[TTS] Generated {out_path}: {dur:.2f}s", flush=True)
    return durations

async def handle_api_route(route, request):
    if request.method == "POST":
        post_data = request.post_data_json
        text = post_data.get("text", "") if post_data else ""
        print(f"[API Intercept] Auditing text: '{text[:50]}...'", flush=True)
        req = AuditRequest(text=text)
        res = audit_landlord_statement(req)
        res_json = res.model_dump()
        await route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(res_json)
        )
    else:
        await route.continue_()

async def record_screencast(durations):
    video_dir = os.path.abspath("video_temp")
    os.makedirs(video_dir, exist_ok=True)

    d1 = durations["vo1"]
    d2 = durations["vo2"]
    d3 = durations["vo3"]
    d4 = durations["vo4"]
    d5 = durations["vo5"]

    # Calculate dynamic offsets to perfectly synchronize voiceover and browser actions
    vo1_offset = 500
    sec1_dur = max(d1 + 1.0, 13.0)

    vo2_offset = vo1_offset + int(sec1_dur * 1000)
    sec2_partA_dur = max(d2 + 1.0, 12.5)

    vo3_offset = vo2_offset + int(sec2_partA_dur * 1000)
    sec2_partB_dur = max(d3 + 1.0, 8.5)

    vo4_offset = vo3_offset + int(sec2_partB_dur * 1000)
    sec3_dur = max(d4 + 1.0, 18.0)

    vo5_offset = vo4_offset + int(sec3_dur * 1000)

    offsets = {
        "vo1": vo1_offset,
        "vo2": vo2_offset,
        "vo3": vo3_offset,
        "vo4": vo4_offset,
        "vo5": vo5_offset,
    }

    print(f"[Timing Matrix] Dynamic offsets (ms): {offsets}", flush=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--window-size=1920,1080"]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=video_dir,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        video_obj = page.video
        await page.route("**/api/**", handle_api_route)

        print("[Playwright] Navigating to target site...", flush=True)
        await page.goto("https://deposit-rescue.vercel.app/", wait_until="networkidle")

        # === SECTION 1: Walkthrough ===
        print(f"[Playwright] Section 1: Walkthrough (Duration: {sec1_dur:.1f}s)", flush=True)
        await page.wait_for_timeout(1500)
        # Scroll down slowly to show Framer Motion 3D parallax UI & typography
        await page.evaluate("window.scrollTo({top: 450, behavior: 'smooth'})")
        await page.wait_for_timeout(3500)
        await page.evaluate("window.scrollTo({top: 850, behavior: 'smooth'})")
        await page.wait_for_timeout(3500)
        await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        await page.wait_for_timeout(3500)

        # Buffer wait to ensure VO1 finishes completely before Section 2
        elapsed_sec1 = 1.5 + 3.5 + 3.5 + 3.5
        if sec1_dur > elapsed_sec1:
            await page.wait_for_timeout(int((sec1_dur - elapsed_sec1) * 1000))

        # === SECTION 2: Live Testing & Edge Cases (Part A - Standard Input) ===
        print(f"[Playwright] Section 2 Part A: Standard Live Input (Duration: {sec2_partA_dur:.1f}s)", flush=True)
        textarea = page.locator("textarea")
        await textarea.click()
        valid_input = "Landlord says: $400 for painting, $150 for routine carpet cleaning, and $200 for a broken window."
        await textarea.type(valid_input, delay=45)

        # STRICT REQUIREMENT: PAUSE FOR 3 SECONDS so text is fully readable on screen
        print("[Playwright] Pausing 3 seconds for readability...", flush=True)
        await page.wait_for_timeout(3000)

        audit_btn = page.locator("button", has_text="AUDIT")
        await audit_btn.click()
        await page.wait_for_timeout(2000)

        # Scroll to view dispute ledger results
        await page.evaluate("window.scrollTo({top: 450, behavior: 'smooth'})")
        await page.wait_for_timeout(3000)

        elapsed_partA = (len(valid_input) * 0.045) + 3.0 + 2.0 + 3.0
        if sec2_partA_dur > elapsed_partA:
            await page.wait_for_timeout(int((sec2_partA_dur - elapsed_partA) * 1000))

        # === SECTION 2 Part B: Edge Case Test with Page Refresh ===
        print(f"[Playwright] Section 2 Part B: Edge Case Test (Duration: {sec2_partB_dur:.1f}s)", flush=True)
        await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        await page.wait_for_timeout(1000)

        # STRICT REQUIREMENT: Refresh the page before demonstrating edge case
        print("[Playwright] Refreshing page to demonstrate edge case state...", flush=True)
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(1500)

        textarea = page.locator("textarea")
        audit_btn = page.locator("button", has_text="AUDIT")

        await textarea.click()
        edge_input = "The landlord was just being mean"
        await textarea.type(edge_input, delay=40)
        await page.wait_for_timeout(1000)
        await audit_btn.click()
        await page.wait_for_timeout(2500)

        elapsed_partB = 1.0 + 1.5 + (len(edge_input) * 0.040) + 1.0 + 2.5
        if sec2_partB_dur > elapsed_partB:
            await page.wait_for_timeout(int((sec2_partB_dur - elapsed_partB) * 1000))

        # === SECTION 3: GenAI in Action ===
        print(f"[Playwright] Section 3: GenAI in Action (Duration: {sec3_dur:.1f}s)", flush=True)
        await textarea.fill("")
        complex_input = "Deducting $50 for leaving dust on the ceiling fan, $500 for a hole I punched in the wall, and $200 for normal wear on the hardwood floors."
        await textarea.type(complex_input, delay=40)
        await page.wait_for_timeout(1500)
        await audit_btn.click()
        await page.wait_for_timeout(2500)

        await page.evaluate("window.scrollTo({top: 480, behavior: 'smooth'})")
        await page.wait_for_timeout(1500)

        # Hover cursor smoothly over each result item card in the dispute ledger
        item_cards = page.locator("div[role='listitem']")
        card_count = await item_cards.count()
        for i in range(card_count):
            try:
                card = item_cards.nth(i)
                box = await card.bounding_box()
                if box:
                    await page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                    await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"[Playwright] Hover info item {i}:", e, flush=True)

        elapsed_sec3 = (len(complex_input) * 0.040) + 1.5 + 2.5 + 1.5 + (card_count * 2.0)
        if sec3_dur > elapsed_sec3:
            await page.wait_for_timeout(int((sec3_dur - elapsed_sec3) * 1000))

        # === SECTION 4: Clear Presentation & Conclusion ===
        sec4_dur = d5 + 3.0
        print(f"[Playwright] Section 4: Clear Presentation & Conclusion (Duration: {sec4_dur:.1f}s)", flush=True)
        await page.evaluate("window.scrollTo({top: 750, behavior: 'smooth'})")
        await page.wait_for_timeout(2000)

        # Hover over Statutory Recovery counter card
        recovery_box = page.locator("text=STATUTORY RECOVERY ESTIMATE")
        if await recovery_box.count() > 0:
            box = await recovery_box.bounding_box()
            if box:
                await page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)

        # Hold state until VO5 finishes plus a 3-second closing buffer
        print(f"[Playwright] Final pause for conclusion ({sec4_dur:.1f}s)...", flush=True)
        await page.wait_for_timeout(int(sec4_dur * 1000))

        # Close context BEFORE fetching video path to avoid deadlock
        print("[Playwright] Closing browser context...", flush=True)
        await context.close()
        await browser.close()

        video_path = await video_obj.path()
        print(f"[Playwright] Video recorded successfully to {video_path}", flush=True)
        return video_path, offsets

def assemble_final_video(video_path, offsets, durations):
    output_mp4 = os.path.abspath("deposit_rescue_demo.mp4")
    print(f"[FFmpeg] Stitching audio timeline and merging with video into {output_mp4}...", flush=True)

    # Build FFmpeg command to delay each audio track and mix them together
    inputs = []
    delay_filters = []
    for idx, (key, offset_ms) in enumerate(offsets.items()):
        audio_file = os.path.abspath(f"audio_temp/{key}.mp3")
        inputs.extend(["-i", audio_file])
        delay_filters.append(f"[{idx}:a]adelay={offset_ms}|{offset_ms}[a{idx+1}]")

    mix_inputs = "".join([f"[a{i+1}]" for i in range(len(offsets))])
    filter_complex = f"{'; '.join(delay_filters)}; {mix_inputs}amix=inputs={len(offsets)}:dropout_transition=0:normalize=0[aout]"

    audio_mix_file = os.path.abspath("audio_temp/full_soundtrack.mp3")
    cmd_audio = [
        FFMPEG_EXE, "-y"
    ] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        audio_mix_file
    ]

    subprocess.run(cmd_audio, check=True)
    print(f"[FFmpeg] Combined soundtrack created at {audio_mix_file}", flush=True)

    # Merge video webm and audio soundtrack into final mp4
    cmd_merge = [
        FFMPEG_EXE, "-y",
        "-i", video_path,
        "-i", audio_mix_file,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ]

    subprocess.run(cmd_merge, check=True)
    print(f"[FFmpeg] Final MP4 video successfully created at {output_mp4}", flush=True)
    
    if os.path.exists(output_mp4):
        size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
        print(f"[SUCCESS] Final Video Size: {size_mb:.2f} MB", flush=True)

async def main():
    durations = await generate_voiceovers()
    video_path, offsets = await record_screencast(durations)
    assemble_final_video(video_path, offsets, durations)

if __name__ == "__main__":
    asyncio.run(main())
