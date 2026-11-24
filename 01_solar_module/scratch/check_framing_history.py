import json

transcript_path = r"C:\Users\Jacob\.gemini\antigravity-cli\brain\b280d3b8-3862-41f6-810f-25b3e1478600\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        idx = data.get("step_index", 0)
        if 1040 <= idx <= 1260:
            calls = data.get("tool_calls", [])
            for c in calls:
                func = c.get("name") or c.get("function", {}).get("name")
                args = c.get("args") or c.get("function", {}).get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except:
                        pass
                if func in ("write_file", "run_command"):
                    if func == "write_file":
                        print(f"Step {idx} write_file: {args.get('Path')}")
                    elif func == "run_command":
                        cmd = str(args.get("CommandLine", ""))[:120].replace("\n", " ")
                        print(f"Step {idx} run_command: {cmd}")
