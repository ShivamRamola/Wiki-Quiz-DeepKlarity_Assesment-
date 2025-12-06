import random
from typing import Dict, Any, List

# Prompt templates for when a real LLM is wired via LangChain/OpenAI.
QUIZ_PROMPT_TEMPLATE = (
    "You are given the title, summary, sections and entities extracted from a Wikipedia article. "
    "Produce 5-8 multiple-choice questions grounded in the provided content. "
    "Each question must include exactly four options (A-D), the correct answer, a short explanation referencing where the answer appears in the article, "
    "and a difficulty tag (easy, medium, hard). Return strict JSON with keys: quiz (list) and related_topics (list)."
)


def _choose_distractors(correct: str, pool: List[str], n: int = 3) -> List[str]:
    """Choose n distractors from pool avoiding the correct answer. If pool is small,
    create plausible variants by adding or swapping words."""
    candidates = [p for p in pool if p and p != correct]
    picked = []
    random.shuffle(candidates)
    while len(picked) < n and candidates:
        picked.append(candidates.pop())

    # If not enough, generate slight variants
    while len(picked) < n:
        if len(correct) > 8:
            variant = correct + " (variant)"
        else:
            variant = correct + " X"
        if variant not in picked:
            picked.append(variant)

    return picked


def _build_question(template: str, correct: str, distractors: List[str], difficulty: str, explanation: str) -> Dict[str, Any]:
    options = [correct] + distractors
    random.shuffle(options)
    return {
        "question": template,
        "options": options,
        "answer": correct,
        "difficulty": difficulty,
        "explanation": explanation,
    }


def generate_quiz_from_text(scraped: Dict[str, Any]) -> Dict[str, Any]:
    """Primary generator used by the API. If an LLM is available this function
    can call out to LangChain/OpenAI and use QUIZ_PROMPT_TEMPLATE. In this
    implementation we provide a deterministic, quality-focused fallback that
    tries to produce varied, grounded questions without inventing facts.
    """
    title = scraped.get("title") or "the topic"
    summary = scraped.get("summary") or ""
    sections = scraped.get("sections") or []
    entities = scraped.get("entities", {}).get("links", [])

    pool = []
    # Build a pool of candidate answers from entities and section phrases
    for e in entities:
        pool.append(e)
    for s in sections:
        words = s.split()
        if len(words) <= 5:
            pool.append(s)

    # Ensure some diversity
    pool = [p for p in dict.fromkeys(pool) if p]
    if not pool:
        # fallback to words from title
        pool = [w for w in title.split() if len(w) > 3]

    num_questions = min(8, max(5, len(pool)))
    quiz = []

    # 1) Questions derived from sections (if any)
    used = set()
    idx = 0
    while len(quiz) < num_questions and idx < len(sections):
        sec = sections[idx]
        idx += 1
        # pick an answer from pool that appears related to this section
        candidates = [p for p in pool if p.lower() in sec.lower() or sec.lower() in p.lower()]
        if not candidates:
            candidates = pool
        correct = candidates[0]
        distractors = _choose_distractors(correct, pool, 3)
        qtext = f"According to the '{sec}' section of the article about {title}, which of the following is true?"
        explanation = f"Information referenced in the '{sec}' section."
        difficulty = random.choice(["easy", "medium"]) if len(sec) < 30 else "medium"
        quiz.append(_build_question(qtext, correct, distractors, difficulty, explanation))
        used.add(correct)

    # 2) Questions derived from entities
    idx = 0
    while len(quiz) < num_questions and idx < len(pool):
        correct = pool[idx]
        idx += 1
        if correct in used:
            continue
        distractors = _choose_distractors(correct, pool, 3)
        qtext = f"Which of the following is associated with {title}?"
        explanation = f"Mentioned in the article content: '{correct}'."
        difficulty = random.choice(["easy", "medium"])
        quiz.append(_build_question(qtext, correct, distractors, difficulty, explanation))
        used.add(correct)

    # 3) If still short, generate summary-based questions
    if len(quiz) < num_questions and summary:
        # try to pick a noun phrase from summary (simple approach)
        words = [w.strip('.,') for w in summary.split() if len(w) > 4]
        if words:
            correct = words[0]
            distractors = _choose_distractors(correct, pool + words, 3)
            qtext = f"From the article summary, which item is mentioned?"
            explanation = "Taken from the article summary."
            quiz.append(_build_question(qtext, correct, distractors, "medium", explanation))

    # Trim to requested number and ensure options are four each
    final_quiz = []
    for q in quiz[:num_questions]:
        options = q["options"]
        # ensure exactly 4 options
        if len(options) > 4:
            options = options[:4]
        while len(options) < 4:
            options.append(q["answer"] + " (alt)")
        q["options"] = options
        final_quiz.append(q)

    # Related topics: use section titles and top entities as suggestions
    related = []
    for s in sections[:6]:
        related.append(s)
    for e in entities[:6]:
        if e not in related:
            related.append(e)

    return {"quiz": final_quiz, "related_topics": related}
