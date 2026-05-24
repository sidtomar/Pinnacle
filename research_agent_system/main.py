"""
Entry point for the Pinnacle Research Agent System.

Usage:
    python main.py "GLP-1 receptor agonists in Type 2 Diabetes"
    python main.py "GLP-1 agents" --specialty Diabetology --therapy-area "GLP-1 Therapy"
    python main.py "SGLT2 inhibitors" --provider openrouter --no-save
"""
import argparse
import json
import sys

from orchestrator import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Pinnacle Research Agent System — 4-agent LangChain pipeline"
    )

    # Research topic — positional or --topic flag
    parser.add_argument("topic", nargs="?", help="Research topic (positional)")
    parser.add_argument("--topic", "-t", dest="topic_flag",
                        help="Research topic (flag alternative)")

    # Portal categorisation — passed to Delta so the card is correctly tagged
    parser.add_argument("--specialty", "-s",
                        default="General Medicine",
                        help="Medical specialty (e.g. 'Diabetology'). Default: General Medicine")
    parser.add_argument("--therapy-area", "-ta",
                        default="General",
                        dest="therapy_area",
                        help="Therapy area (e.g. 'GLP-1 Therapy'). Default: General")

    # LLM provider override
    parser.add_argument("--provider", "-p",
                        choices=["openrouter", "claude", "openai"],
                        help="LLM provider override (default: from .env LLM_PROVIDER)")

    # Skip saving output files
    parser.add_argument("--no-save", action="store_true",
                        help="Don't save intermediate outputs to ./outputs/")

    args = parser.parse_args()

    topic = args.topic or args.topic_flag
    if not topic:
        print("Error: please provide a research topic.")
        print('  Example: python main.py "GLP-1 receptor agonists"')
        sys.exit(1)

    # Override LLM provider if specified
    if args.provider:
        import os
        os.environ["LLM_PROVIDER"] = args.provider

    # Run the full pipeline
    result = run_pipeline(
        topic=topic,
        specialty=args.specialty,
        therapy_area=args.therapy_area,
        save_outputs=not args.no_save,
    )

    # Exit with error code if any agent failed
    if result.errors:
        print("\nPipeline completed with errors:")
        for e in result.errors:
            print(f"  - {e}")
        sys.exit(1)

    # Print preview of the final portal content card
    print("\n── PINNACLE CONTENT CARD (preview) ──")
    preview_fields = ["id", "title", "specialty", "therapy_area", "sub_category",
                      "tags", "summary", "evidence_quality", "status"]
    preview = {k: result.content_card[k] for k in preview_fields if k in result.content_card}
    print(json.dumps(preview, indent=2))


if __name__ == "__main__":
    main()
