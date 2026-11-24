import json

transcript_path = r"C:\Users\Jacob\.gemini\antigravity-cli\brain\b280d3b8-3862-41f6-810f-25b3e1478600\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = str(data.get("content", "")).replace("\n", " ")
            print(f"Step {data.get('step_index')}: {content[:120]}")
