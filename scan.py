"""Regenerate manifest.json from the images/music/sounds folders.

Run this after adding or removing files so HappeyOS picks them up locally:
    python scan.py
(On the deployed site the file list comes from GitHub automatically.)
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def ls(d):
    p = os.path.join(ROOT, d)
    if not os.path.isdir(p):
        return []
    return sorted(
        f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))
    )


manifest = {
    "images": ls(os.path.join("assets", "images")),
    "music": ls(os.path.join("assets", "music")),
    "sounds": ls(os.path.join("assets", "sounds")),
    "documents": ["documents/" + f for f in ls(os.path.join("assets", "images", "documents"))],
}

with open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=1)
    f.write("\n")

print("wrote manifest.json:", {k: len(v) for k, v in manifest.items()})
