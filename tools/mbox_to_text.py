#!/usr/bin/env python3
import argparse
import mailbox
from email.header import decode_header, make_header

def decode_header_value(value: str) -> str:
    """Decode MIME-encoded email headers into readable Unicode."""
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value

def extract_body(msg) -> str:
    """
    Extract a readable body from an email.message.Message.
    Prefers text/plain, skips attachments.
    """
    # Multipart: walk parts and pick text/plain
    if msg.is_multipart():
        parts = []
        for part in msg.walk():
            content_type = part.get_content_type()
            disp = part.get("Content-Disposition", "")

            # Skip attachments
            if "attachment" in (disp or "").lower():
                continue

            if content_type == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                try:
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    parts.append(payload.decode(charset, errors="replace"))
                except Exception:
                    # Fallback: try raw payload
                    try:
                        parts.append(part.get_payload())
                    except Exception:
                        pass

        if parts:
            return "\n\n".join(parts).strip()

        # Fallback: if no text/plain, try first text/html as raw text
        for part in msg.walk():
            content_type = part.get_content_type()
            disp = part.get("Content-Disposition", "")
            if "attachment" in (disp or "").lower():
                continue
            if content_type == "text/html":
                charset = part.get_content_charset() or "utf-8"
                try:
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    return payload.decode(charset, errors="replace").strip()
                except Exception:
                    try:
                        return part.get_payload().strip()
                    except Exception:
                        pass

        return ""
    else:
        # Single-part message
        content_type = msg.get_content_type()
        if content_type in ("text/plain", "text/html"):
            charset = msg.get_content_charset() or "utf-8"
            try:
                payload = msg.get_payload(decode=True)
                if payload is not None:
                    return payload.decode(charset, errors="replace").strip()
            except Exception:
                try:
                    return msg.get_payload().strip()
                except Exception:
                    pass
        return ""

def convert_mbox_to_text(mbox_path: str, output_path: str) -> None:
    mbox = mailbox.mbox(mbox_path)
    with open(output_path, "w", encoding="utf-8") as out:
        for idx, msg in enumerate(mbox, start=1):
            subject = decode_header_value(msg.get("Subject", ""))
            from_ = decode_header_value(msg.get("From", ""))
            to = decode_header_value(msg.get("To", ""))
            date = decode_header_value(msg.get("Date", ""))

            body = extract_body(msg)

            out.write(f"==== EMAIL {idx} ====\n")
            out.write(f"Date: {date}\n")
            out.write(f"From: {from_}\n")
            out.write(f"To:   {to}\n")
            out.write(f"Subject: {subject}\n\n")
            out.write(body)
            out.write("\n\n\n")  # spacing between messages

def main():
    parser = argparse.ArgumentParser(
        description="Convert a Gmail .mbox export into a single readable .txt file."
    )
    parser.add_argument("mbox_path", help="Path to the input .mbox file")
    parser.add_argument(
        "output_path",
        nargs="?",
        default="all-emails.txt",
        help="Path to the output text file (default: all-emails.txt)",
    )
    args = parser.parse_args()

    print(f"Reading mbox: {args.mbox_path}")
    print(f"Writing output: {args.output_path}")
    convert_mbox_to_text(args.mbox_path, args.output_path)
    print("Done.")

if __name__ == "__main__":
    main()
