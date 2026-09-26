import asyncio
import os
import subprocess
import re
import edge_tts
from imageio_ffmpeg import get_ffmpeg_exe

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

async def main():
    os.makedirs("audio_temp", exist_ok=True)
    durations = {}
    for key, text in VOICEOVERS.items():
        out_path = f"audio_temp/{key}.mp3"
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural", rate="-2%")
        await communicate.save(out_path)
        dur = get_audio_duration(out_path)
        durations[key] = dur
        print(f"Generated {out_path}: {dur:.2f} seconds")
    
    print("\nTotal audio duration:", sum(durations.values()), "seconds")

if __name__ == "__main__":
    asyncio.run(main())
