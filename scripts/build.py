#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import shutil
from datetime import date, datetime
from pathlib import Path

import jinja2
import mistune
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
TEMPLATE_DIR = ROOT / "templates"

EXCLUDE_FROM_SITE = {
    ".git", ".github", "content", "templates", "scripts", "_site",
    "requirements.txt", "README_WRITING.md", "TAG_SCHEMA.md",
}

markdown = mistune.create_markdown(escape=False, plugins=["table", "strikethrough"])


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def join_pipe(value):
    return "|".join(as_list(value))


def join_display(value):
    return " / ".join(as_list(value))


def load_markdown(path: Path, kind: str):
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML front matter")
    try:
        _, front, body = raw.split("---", 2)
    except ValueError as exc:
        raise ValueError(f"{path}: invalid front matter") from exc
    data = yaml.safe_load(front) or {}
    data["kind"] = data.get("kind", kind)
    data["source_path"] = path
    data["body_markdown"] = body.strip()
    data["body_html"] = markdown(body.strip())
    data["slug"] = str(data.get("slug") or path.stem).strip()
    data["title"] = str(data.get("title") or data["slug"]).strip()
    data["description"] = str(data.get("description") or data.get("subtitle") or "").strip()
    data["subtitle"] = str(data.get("subtitle") or data["description"]).strip()
    data["category"] = str(data.get("category") or "音乐笔记").strip()
    for key in ("composer", "artist", "franchise", "instrument"):
        data[key] = as_list(data.get(key))
    data["info"] = data.get("info") or {}
    data["related_links"] = data.get("related_links") or []
    data["bilibili"] = data.get("bilibili") or []
    data["youtube"] = data.get("youtube") or {}
    data["sheet_music"] = data.get("sheet_music") or {}
    data["draft"] = bool(data.get("draft", False))
    data["weight"] = data.get("weight", None)
    return data


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value:
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            pass
    return date.min


def sort_key(item):
    # New posts without a weight appear first, newest date first.
    # Existing curated works can keep a stable explicit weight.
    if item.get("weight") is None:
        d = parse_date(item.get("date"))
        return (0, -d.toordinal(), item["title"])
    return (1, int(item["weight"]), item["title"])


def card_tags(item):
    tags = []
    if item.get("category"):
        tags.append(item["category"])
    if item.get("composer"):
        tags.append(join_display(item["composer"]))
    if item.get("artist"):
        tags.append(join_display(item["artist"]))
    if item.get("franchise"):
        tags.append(join_display(item["franchise"]))
    return tags[:4]


def thumbnail(item):
    explicit = str(item.get("thumbnail") or "").strip()
    if explicit:
        return explicit
    yt = item.get("youtube") or {}
    video_id = str(yt.get("id") or "").strip()
    if video_id:
        return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    return "img/default.JPG"


def output_href(item):
    folder = "works" if item["kind"] == "work" else "notes"
    return f"{folder}/{item['slug']}/index.html"


def copy_static(output: Path):
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for item in ROOT.iterdir():
        if item.name in EXCLUDE_FROM_SITE:
            continue
        dest = output / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    # Generated sections are authoritative; do not keep stale generated pages.
    for generated_dir in (output / "works", output / "notes"):
        if generated_dir.exists():
            shutil.rmtree(generated_dir)
        generated_dir.mkdir(parents=True, exist_ok=True)
    (output / ".nojekyll").write_text("", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Build SwZap static site from Markdown")
    parser.add_argument("--output", default="_site", help="output directory")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
        autoescape=jinja2.select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["join_pipe"] = join_pipe
    env.filters["join_display"] = join_display

    items = []
    for kind, subdir in (("work", "works"), ("note", "notes")):
        directory = CONTENT_DIR / subdir
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            item = load_markdown(path, kind)
            if not item["draft"]:
                items.append(item)

    items.sort(key=sort_key)
    for item in items:
        item["card_tags"] = card_tags(item)
        item["thumbnail_url"] = thumbnail(item)
        item["href"] = output_href(item)
        item["data_category"] = item["category"]
        item["data_composer"] = join_pipe(item["composer"])
        item["data_artist"] = join_pipe(item["artist"])
        item["data_franchise"] = join_pipe(item["franchise"])
        item["data_instrument"] = join_pipe(item["instrument"])

    copy_static(output)

    index_html = env.get_template("index.html").render(items=items)
    (output / "index.html").write_text(index_html, encoding="utf-8")

    for item in items:
        folder = output / ("works" if item["kind"] == "work" else "notes") / item["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        template = "work.html" if item["kind"] == "work" else "note.html"
        rendered = env.get_template(template).render(item=item)
        (folder / "index.html").write_text(rendered, encoding="utf-8")

    redirect = env.get_template("section_redirect.html").render()
    (output / "works" / "index.html").write_text(redirect, encoding="utf-8")
    (output / "notes" / "index.html").write_text(redirect, encoding="utf-8")

    print(f"Built {len(items)} Markdown pages into {output}")


if __name__ == "__main__":
    main()
