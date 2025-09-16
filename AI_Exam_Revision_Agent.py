
from datetime import date, timedelta, datetime
import os
import json
import argparse
import sys

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_LLM = bool(OPENAI_API_KEY)

def parse_input(text):
    parts = {"subject":"", "topics":[], "days":0, "style":""}
    text = text.strip()
    if not text:
        return parts
    segments = [s.strip() for s in text.split(';') if s.strip()]
    for s in segments:
        low = s.lower()
        if "days" in low or "day" in low or "week" in low:
            nums = [int(tok) for tok in s.split() if tok.isdigit()]
            if nums:
                parts["days"] = nums[0]
            else:
                nums = []
                for tok in s.replace(',', ' ').split():
                    try:
                        n = int(tok)
                        nums.append(n)
                    except:
                        pass
                if nums:
                    parts["days"] = nums[0]
        elif "topics:" in low or "topic:" in low or ',' in s:
            cleaned = s.split(':',1)[-1].strip() if ':' in s else s
            parts["topics"] = [t.strip() for t in cleaned.split(',') if t.strip()]
        elif "style:" in low:
            parts["style"] = s.split(':',1)[-1].strip()
        elif "subject:" in low:
            parts["subject"] = s.split(':',1)[-1].strip()
        else:
            if not parts["subject"]:
                parts["subject"] = s
    if parts["days"] == 0:
        parts["days"] = 7
    if not parts["topics"] and parts["subject"]:
        parts["topics"] = [parts["subject"] + " - General"]
    return parts

def sm2_schedule(topics, days):
    schedule = []
    for i, topic in enumerate(topics):
        interval = max(1, (i % days) + 1)
        day = (i % days) + 1
        schedule.append({"day": day, "topic": topic, "interval": interval})
    return schedule

def local_quiz_generator(topic, kb=None, n=5):
    topic_key = topic.lower()
    if kb and topic_key in kb:
        return kb[topic_key][:n]
    base = [
        f"What is the core concept of {topic}?",
        f"Explain a key example/problem for {topic}.",
        f"List 3 important definitions in {topic}.",
        f"Why does {topic} matter? Provide a short answer.",
        f"Give one practice question on {topic}."
    ]
    return base[:n]

def call_llm_build(parsed, model="gpt-4o-mini", max_tokens=800, temp=0.2):
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        system = "You are a concise study planner. Output strict JSON with key 'daily' as list of {day,topic,quiz_questions}."
        prompt = f"Subject: {parsed['subject']}\nTopics: {parsed['topics']}\nDays: {parsed['days']}\nStyle: {parsed['style']}\nProduce a compact daily schedule as JSON."
        resp = openai.ChatCompletion.create(model=model, messages=[{"role":"system","content":system},{"role":"user","content":prompt}], max_tokens=max_tokens, temperature=temp)
        txt = resp['choices'][0]['message']['content']
        return json.loads(txt)
    except Exception as e:
        return None

def build_plan(parsed, progress_log=None, kb=None):
    if USE_LLM:
        out = call_llm_build(parsed)
        if out:
            return out
    topics = parsed["topics"] or ["General"]
    days = max(1, int(parsed.get("days", 7)))
    evenly = []
    for i in range(days):
        topic = topics[i % len(topics)]
        qs = local_quiz_generator(topic, kb)
        evenly.append({"day": i+1, "topic": topic, "quiz": qs})
    spaced = sm2_schedule(topics, days)
    for s in spaced:
        for e in evenly:
            if e["day"] == s["day"]:
                e["priority"] = s["interval"]
    return {"daily": evenly}

def pretty_print(plan):
    lines = []
    lines.append("\n📘 Personalized Revision Plan\n")
    lines.append("| Day | Topic | Sample Quiz Questions |")
    lines.append("|-----|-------|------------------------|")
    for d in plan.get("daily", []):
        qtxt = " || ".join(d.get("quiz", [])[:3])
        lines.append(f"| {d.get('day')} | {d.get('topic')} | {qtxt} |")
    lines.append("\nGood luck! Keep reviewing and update progress after each session.\n")
    print("\n".join(lines))

def save_progress(path, progress):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def load_progress(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_cli(args):
    if args.input:
        parsed = parse_input(args.input)
    else:
        raw = input("Enter input (format: Subject; topics: A,B,C; days: 10; style: active):\n")
        parsed = parse_input(raw)
    kb = {}
    sample_kb = {
        "genetics":["What is DNA?","Describe Mendelian inheritance","Define allele","Explain mutation","Describe replication"],
        "cell biology":["Name organelles","Function of mitochondria","Cell membrane structure","Describe mitosis","Cell transport mechanisms"]
    }
    kb.update(sample_kb)
    progress = load_progress(args.progress) if args.progress else {}
    plan = build_plan(parsed, progress_log=progress, kb=kb)
    pretty_print(plan)
    if args.save_progress:
        date_key = datetime.now().isoformat()
        progress.setdefault("logs", []).append({"timestamp": date_key, "parsed": parsed, "plan": plan})
        save_progress(args.save_progress, progress)
        print(f"Progress saved to {args.save_progress}")

def make_arg_parser():
    p = argparse.ArgumentParser(description="Advanced AI Exam Revision Agent - CLI")
    p.add_argument("--input", "-i", type=str, help="Input string e.g. 'Subject; topics: A,B; days:10; style: active'")
    p.add_argument("--progress", "-p", type=str, help="Path to existing progress json")
    p.add_argument("--save-progress", "-s", type=str, help="Path to save progress json")
    return p

def main():
    parser = make_arg_parser()
    args = parser.parse_args()
    run_cli(args)

if __name__ == "__main__":
    main()
