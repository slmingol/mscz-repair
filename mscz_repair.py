#!/usr/bin/env python3
"""
mscz-repair: fix MuseScore files that crash on load due to stale excerpts.

The crash symptom is an assertion failure in setTrack() triggered when
MuseScore tries to link excerpt elements to the main score by tick position
and the ticks don't match (score was edited after parts were generated).

Fix: strip excerpt references from META-INF/container.xml and repack.
After opening the repaired file, regenerate parts via the Parts panel and
re-save so MuseScore writes fresh, correctly-linked excerpts.
"""

import argparse
import os
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET


def repair(input_path: str, output_path: str) -> int:
    """Strip stale excerpt entries and repack the archive.

    Returns the number of rootfile entries removed from container.xml.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(tmpdir)

        container_path = os.path.join(tmpdir, "META-INF", "container.xml")
        if not os.path.exists(container_path):
            raise ValueError("META-INF/container.xml not found — is this a valid .mscz?")

        tree = ET.parse(container_path)
        root = tree.getroot()

        rootfiles_el = root.find("rootfiles")
        if rootfiles_el is None:
            raise ValueError("No <rootfiles> element found in container.xml")

        to_remove = [
            rf for rf in rootfiles_el.findall("rootfile")
            if (rf.get("full-path") or "").startswith("Excerpts/")
        ]
        for rf in to_remove:
            rootfiles_el.remove(rf)

        ET.indent(tree, space="  ")
        tree.write(container_path, encoding="unicode", xml_declaration=True)

        files_to_pack = []
        for dirpath, dirnames, filenames in os.walk(tmpdir):
            dirnames[:] = [d for d in dirnames if d != "Excerpts"]
            for fname in filenames:
                full = os.path.join(dirpath, fname)
                arcname = os.path.relpath(full, tmpdir)
                files_to_pack.append((full, arcname))

        tmp_out = output_path + ".tmp"
        try:
            with zipfile.ZipFile(tmp_out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                for full, arcname in files_to_pack:
                    zout.write(full, arcname)
            os.replace(tmp_out, output_path)
        except Exception:
            if os.path.exists(tmp_out):
                os.unlink(tmp_out)
            raise

    return len(to_remove)


def main():
    parser = argparse.ArgumentParser(
        prog="mscz-repair",
        description="Repair a .mscz file with stale excerpts that prevent loading.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "After opening the repaired file in MuseScore:\n"
            "  1. Regenerate parts via the Parts panel in the left sidebar.\n"
            "  2. Save (Ctrl/Cmd+S) — MuseScore rewrites the archive with fresh excerpts."
        ),
    )
    parser.add_argument("input", help="path to the broken .mscz file")
    parser.add_argument(
        "-o", "--output",
        help="output path (default: <input>_fixed.mscz next to the original)",
    )
    parser.add_argument(
        "-i", "--in-place",
        action="store_true",
        help="overwrite the input file instead of writing a new one",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.isfile(input_path):
        print(f"error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.in_place:
        output_path = input_path
    elif args.output:
        output_path = os.path.abspath(args.output)
    else:
        base, ext = os.path.splitext(input_path)
        output_path = base + "_fixed" + ext

    try:
        removed = repair(input_path, output_path)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if removed == 0:
        print("No excerpt entries found — file may not have this issue.")
    else:
        print(f"Removed {removed} stale excerpt entries.")

    print(f"Written: {output_path}")


if __name__ == "__main__":
    main()
