import os
from transformers import pipeline

os.environ["TOKENIZERS_PARALLELISM"] = "false"

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def split_into_bullets(text, bullet_count=6):
    sentences = text.replace(" - ", ". ").replace("–", "-").split(". ")
    bullets = [f"- {s.strip().rstrip('.')}" for s in sentences if s.strip()]
    return "\n".join(bullets[:bullet_count]) if bullets else f"- {text}"

def extract_key_phrases(summary_text: str, keywords=("decide", "agreement", "approve", "plan", "confirm")):
    sentences = summary_text.split(". ")
    decisions = [f"- {s.strip().rstrip('.')}" for s in sentences if any(k in s.lower() for k in keywords)]
    actions = [f"- {s.strip().rstrip('.')}" for s in sentences if "should" in s.lower() or "need to" in s.lower()]
    return decisions[:3], actions[:3]

def summarize_text(input_text: str) -> str:
    input_words = input_text.split()
    if len(input_words) > 1000:
        input_text = " ".join(input_words[:1000])

    try:
        result = summarizer(input_text, max_length=300, min_length=100, do_sample=False)
        raw_summary = result[0]["summary_text"].strip()

        bullet_summary = split_into_bullets(raw_summary)
        decisions, actions = extract_key_phrases(raw_summary)

        decision_text = "\n".join(decisions) if decisions else "- [No clear decisions extracted.]"
        action_text = "\n".join(actions) if actions else "- [No specific action items detected.]"

        structured_output = (
            f"### Summary:\n{bullet_summary}\n\n"
            f"### Key Decisions:\n{decision_text}\n\n"
            f"### Action Items:\n{action_text}"
        )

        return structured_output

    except Exception as e:
        print(f"[ERROR] Summarization failed: {e}")
        return "[ERROR] Summarization failed. Please try again later."
