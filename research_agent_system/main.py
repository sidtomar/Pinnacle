"""
Entry point for the Pinnacle Research Agent System.

Pipeline steps:
  Step 1 : Topic from Databricks (doctor specialty/interests) — optional
  Step 2 : Agent Alpha  — PubMed scraping + MA Content Library → paper list
  Step 3 : Agent Beta   — Per-paper clinical summaries
  Step 4 : Agent Gamma  — Shareable content (WhatsApp/email) with Read More links
  Step 5 : Agent Delta  — Portal content card (pending MA review)

Usage examples:
  python main.py "SGLT2 inhibitors heart failure"
  python main.py "GLP-1 receptor agonists" --specialty Diabetology --therapy-area "GLP-1 Therapy"
  python main.py --specialty Cardiology --therapy-area "Heart Failure" --use-databricks
  python main.py "semaglutide" --doctor-id DOC_001 --provider openrouter --no-save
"""

import argparse
import json
import sys

from orchestrator import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Pinnacle Research Agent System — Alpha→Beta→Gamma→Delta pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agent Pipeline:
  Alpha  — PubMed scraping + MA Content Library  → paper list with metadata
  Beta   — Per-paper clinical summaries           → key findings per paper
  Gamma  — Shareable WhatsApp/email content       → key points + Read More PubMed link
  Delta  — Pinnacle portal content card           → stored for MA review
        """,
    )

    # ── Topic ──────────────────────────────────────────────────────────────────
    parser.add_argument(
        "topic",
        nargs="?",
        help="Research topic — e.g. 'SGLT2 inhibitors heart failure' (positional)",
    )
    parser.add_argument(
        "--topic", "-t",
        dest="topic_flag",
        help="Research topic (flag alternative to positional arg)",
    )

    # ── Doctor / Specialty context ─────────────────────────────────────────────
    parser.add_argument(
        "--specialty", "-s",
        default="General Medicine",
        help="Doctor specialty (e.g. 'Diabetology', 'Cardiology'). Default: General Medicine",
    )
    parser.add_argument(
        "--therapy-area", "-ta",
        default="General",
        dest="therapy_area",
        help="Therapy area (e.g. 'GLP-1 Therapy', 'Heart Failure'). Default: General",
    )
    parser.add_argument(
        "--doctor-id", "-d",
        default="",
        dest="doctor_id",
        help="Doctor ID for Databricks profile lookup (optional)",
    )

    # ── Databricks topic override ──────────────────────────────────────────────
    parser.add_argument(
        "--use-databricks",
        action="store_true",
        dest="use_databricks",
        help=(
            "Fetch topic from Databricks doctor_profiles table based on "
            "specialty/interests instead of using the provided topic string"
        ),
    )

    # ── LLM provider override ──────────────────────────────────────────────────
    parser.add_argument(
        "--provider", "-p",
        choices=["openrouter", "claude", "openai"],
        help="LLM provider (default: reads LLM_PROVIDER from .env)",
    )

    # ── Save outputs ───────────────────────────────────────────────────────────
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save intermediate outputs to ./outputs/",
    )

    args = parser.parse_args()

    # Resolve topic
    topic = args.topic or args.topic_flag
    if not topic and not args.use_databricks:
        print("Error: please provide a research topic OR use --use-databricks.")
        print('  Examples:')
        print('    python main.py "SGLT2 inhibitors heart failure"')
        print('    python main.py --specialty Cardiology --therapy-area "Heart Failure" --use-databricks')
        sys.exit(1)

    topic = topic or ""   # may be empty if use_databricks=True (orchestrator resolves it)

    # Override LLM provider if specified
    if args.provider:
        import os
        os.environ["LLM_PROVIDER"] = args.provider

    # ── Run the full pipeline ─────────────────────────────────────────────────
    result = run_pipeline(
        topic=topic,
        specialty=args.specialty,
        therapy_area=args.therapy_area,
        doctor_id=args.doctor_id,
        save_outputs=not args.no_save,
        use_databricks_topics=args.use_databricks,
    )

    # ── Exit code ─────────────────────────────────────────────────────────────
    if result.errors:
        print("\nPipeline completed with errors:")
        for e in result.errors:
            print(f"  - {e}")
        sys.exit(1)

    # ── Final summary ─────────────────────────────────────────────────────────
    print("\n── PORTAL CARD PREVIEW ──")
    preview_keys = ["id", "title", "specialty", "therapy_area",
                    "sub_category", "tags", "summary", "evidence_quality", "status"]
    preview = {k: result.content_card.get(k) for k in preview_keys if k in result.content_card}
    if preview:
        print(json.dumps(preview, indent=2))
    else:
        print("  (Delta did not produce a card — check for errors above)")


if __name__ == "__main__":
    main()
