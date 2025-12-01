#!/usr/bin/env python3
import argparse
import os

def split_emails(input_path: str, output_prefix: str, chunk_size: int) -> None:
    """
    Split a big all-emails.txt file into multiple smaller files.

    - Splits on lines starting with '==== EMAIL '
    - Writes up to `chunk_size` emails per output file
    - Output files: {output_prefix}-part-001.txt, {output_prefix}-part-002.txt, ...
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        emails = []
        current_email_lines = []

        for line in f:
            if line.startswith("==== EMAIL "):
                # New email starts; store previous one if it exists
                if current_email_lines:
                    emails.append("".join(current_email_lines))
                    current_email_lines = []
            current_email_lines.append(line)

        # Add the last email if any
        if current_email_lines:
            emails.append("".join(current_email_lines))

    total = len(emails)
    print(f"Total emails found: {total}")
    if total == 0:
        print("WARNING: No emails found. Check that the input file has '==== EMAIL ' markers.")
        return

    # Create chunks
    part = 1
    for i in range(0, total, chunk_size):
        chunk_emails = emails[i:i + chunk_size]
        out_name = f"{output_prefix}-part-{part:03d}.txt"
        with open(out_name, "w", encoding="utf-8") as out:
            for email_text in chunk_emails:
                out.write(email_text)
                # Ensure clear separation between emails (already included, but double-safe)
                if not email_text.endswith("\n\n"):
                    out.write("\n\n")
        print(f"Wrote {len(chunk_emails)} emails to {out_name}")
        part += 1

def main():
    parser = argparse.ArgumentParser(
        description="Split a large all-emails.txt into smaller parts for ChatGPT."
    )
    parser.add_argument("input_path", help="Path to the big all-emails.txt file")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100,
        help="Number of emails per output file (default: 100)",
    )
    parser.add_argument(
        "--output-prefix",
        default="emails",
        help="Prefix for output files (default: 'emails')",
    )
    args = parser.parse_args()

    print(f"Reading: {args.input_path}")
    print(f"Chunk size: {args.chunk_size} emails per file")
    split_emails(args.input_path, args.output_prefix, args.chunk_size)
    print("Done.")

if __name__ == "__main__":
    main()
