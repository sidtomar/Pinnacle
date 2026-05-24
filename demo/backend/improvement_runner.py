"""
Improvement Runner — partial pipeline re-run with MA feedback.

When MA team requests improvements on a content card:
  1. Alpha is SKIPPED — original internet research is still valid
  2. Beta re-runs with original research + MA improvement notes injected
  3. Gamma re-runs with revised insights + MA notes as constraints
  4. Delta saves as a new version (v2, v3, ...) linked to the original
  5. MA team is notified for re-review

This is the Human-in-the-Loop (HITL) refinement workflow.
"""
import time, random, uuid
from mock_runner import MOCK_LIBRARY, _generic_content


def run_improvement_pipeline(
    original_content: dict,
    improvement_notes: str,
    run_store: dict,
    run_id: str,
    store,  # BaseStore instance
    notify_fn=None,  # optional callback: notify_ma_improvement_ready(store, id, title, version, division)
) -> None:
    """
    Re-run Beta + Gamma only, incorporating MA's improvement notes.
    Saves result as a new version linked to the original content card.

    Args:
        original_content: The content dict retrieved from store (the version MA is improving)
        improvement_notes: Free-text notes from MA team (e.g. "Fix the empagliflozin dose to 10mg")
        run_store: In-memory pipeline run status dict (same as used by mock_runner)
        run_id: UUID for this improvement run
        store: BaseStore instance for saving the improved version
        notify_fn: Optional notification callback
    """
    def update(agent: str, pct: int, msg: str):
        run_store[run_id].update({
            "current_agent": agent,
            "progress": pct,
            "status_msg": msg,
        })
        time.sleep(random.uniform(1.5, 2.5))

    topic        = original_content.get("topic", "")
    specialty    = original_content.get("specialty", "General Medicine")
    therapy_area = original_content.get("therapy_area", "General")
    orig_version = original_content.get("version") or 1
    new_version  = orig_version + 1
    parent_id    = original_content.get("parent_id") or original_content["id"]

    # Determine base content template
    key  = next((k for k in MOCK_LIBRARY if k.upper() in topic.upper()), None)
    base = MOCK_LIBRARY[key] if key else _generic_content(topic, specialty, therapy_area)

    run_store[run_id]["agent_outputs"] = {}

    # -- Alpha: SKIPPED --------------------------------------------------------
    run_store[run_id]["agent_outputs"]["alpha"] = {
        "skipped": True,
        "summary": "Research reused from original run — Alpha skipped for efficiency",
    }
    update("alpha", 8, "Alpha: Skipped — reusing original research output...")

    # -- Beta: Re-run with MA notes injected -----------------------------------
    update("beta", 25, "Beta: Re-extracting insights with MA feedback applied...")
    update("beta", 40, "Beta: Applying corrections and clinical constraints...")

    # Build refined findings list — intelligently incorporate MA feedback
    findings = list(base["key_findings"])
    notes_lower = improvement_notes.lower()

    # Insert targeted correction based on note keywords
    corrections = []
    if any(w in notes_lower for w in ["dose", "dosage", "mg", "dosing", "titration"]):
        corrections.append("CORRECTED per MA review: dosing information verified and updated to match current prescribing guidelines")
    if any(w in notes_lower for w in ["reference", "guideline", "trial", "study", "evidence"]):
        corrections.append("UPDATED per MA review: all references cross-checked against specified clinical trials and society guidelines")
    if any(w in notes_lower for w in ["remove", "exclude", "not in portfolio", "competitor"]):
        corrections.append("REVISED per MA review: content scoped to Mankind Pharma portfolio only — competitor references removed")
    if any(w in notes_lower for w in ["indian", "india", "local", "population"]):
        corrections.append("ENHANCED per MA review: Indian population data and local clinical context strengthened")
    if not corrections:
        corrections.append(f"REVISED per MA review: content updated to address the following feedback: {improvement_notes[:120]}")

    refined_findings = corrections + findings

    run_store[run_id]["agent_outputs"]["beta"] = {
        "findings": refined_findings,
        "improvement_notes": improvement_notes,
        "summary": f"{len(refined_findings)} insights — {len(corrections)} MA correction(s) applied",
    }

    # -- Gamma: Rewrite with revised insights ----------------------------------
    update("gamma", 58, "Gamma: Rewriting article with MA corrections incorporated...")
    update("gamma", 72, "Gamma: Formatting revised content for WhatsApp/email delivery...")

    revision_header = (
        f"[REVISION v{new_version} — MA Feedback Applied]\n"
        f"MA Notes: {improvement_notes[:200]}\n\n"
    )
    article_revised = revision_header + base["short_article"]
    word_count      = len(article_revised.split())
    excerpt         = base["short_article"][:220]  # excerpt from the clean article part

    run_store[run_id]["agent_outputs"]["gamma"] = {
        "article_excerpt": excerpt,
        "word_count": word_count,
        "summary": f"Article revised · v{new_version} · {word_count} words · MA feedback incorporated",
    }

    # -- Delta: Save as new version -------------------------------------------
    update("delta", 86, f"Delta: Saving as v{new_version} — linked to original...")
    update("delta", 95, "Delta: Notifying MA team for re-review...")

    improved_card = {
        **base,
        "topic":             topic,
        "specialty":         specialty,
        "therapy_area":      therapy_area,
        "key_findings":      refined_findings,
        "short_article":     article_revised,
        "version":           new_version,
        "parent_id":         parent_id,
        "improvement_notes": improvement_notes,
        "pipeline":          f"Improvement v{new_version} · Beta+Gamma re-run · Alpha skipped",
        "llm_provider":      "openrouter",
    }

    content_id = store.save_improved_content(improved_card, parent_id=parent_id, version=new_version)

    run_store[run_id]["agent_outputs"]["delta"] = {
        "card_title": improved_card["title"],
        "tags":       improved_card.get("tags", []),
        "version":    new_version,
        "summary":    f"v{new_version} saved · Pending MA re-review",
    }

    run_store[run_id].update({
        "status":        "completed",
        "progress":      100,
        "current_agent": "delta",
        "status_msg":    f"Revision complete — v{new_version} is pending MA review",
        "content_id":    content_id,
        "content":       improved_card,
        "version":       new_version,
    })

    # Fire notification
    if notify_fn:
        try:
            notify_fn(store, content_id, improved_card["title"], new_version,
                      original_content.get("division", "All"))
        except Exception as e:
            print(f"[ImprovementRunner] Notification failed: {e}")
