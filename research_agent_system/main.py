"""
Entry point for the Pinnacle Research Agent System.

Usage:
    python main.py "GLP-1 receptor agonists in Type 2 Diabetes"
    python main.py --topic "SGLT2 inhibitors heart failure" --provider openai
"""
import argparse
import json
import sys

from orchestrator import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Pinnacle Research Agent System — 4-agent LangChain pipeline"
    )
    parser.add_argument(
        "topic",
        nargs="?",
        help="Research topic or keywords",
    )
    parser.add_argument(
        "--topic", "-t",
        dest="topic_flag",
        help="Research topic (alternative to positional argument)",
    )
    parser.add_argument(
        "--provider", "-p",
        choices=["claude", "openai"],
        help="LLM provider override (default: from .env LLM_PROVIDER)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save intermediate outputs to ./outputs/",
    )

    args = parser.parse_args()

    topic = args.topic or args.topic_flag
    if not topic:
        print("Error: please provide a research topic.")
        print("  Example: python main.py \"GLP-1 receptor agonists\"")
        sys.exit(1)

    if args.provider:
        import os
        os.environ["LLM_PROVIDER"] = args.provider

    result = run_pipeline(topic=topic, save_outputs=not args.no_save)

    if result.errors:
        print("\nPipeline completed with errors:")
        for e in result.errors:
            print(f"  - {e}")
        sys.exit(1)

    print("\n── FINAL JSON REPORT (preview) ──")
    preview = {k: result.report[k] for k in ["report_id", "topic", "summary", "key_findings"] if k in result.report}
    print(json.dumps(preview, indent=2))


if __name__ == "__main__":
    main()
