"""Guide PDF « Le RAG expliqué par Rago » : un chapitre par épisode publié.

Le contenu est dans ``guide/`` (``guide.yaml`` pour les pages fixes, ``chapitres/`` pour les
chapitres). Les illustrations sont des « photos » des scènes Manim, identiques aux vidéos.

    python -m rago guide      # crée output/guide_rag.pdf
"""

from __future__ import annotations

import datetime as dt
import html
import importlib
import logging
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from rago import theme

DEFAULT_GUIDE_DIR = Path("guide")
DEFAULT_CACHE_DIR = Path("cache") / "guide"

# Couleurs des pages intérieures (fond clair : on reprend la charte en version « papier »).
PAGE_BG = theme.TEXT
INK = theme.BACKGROUND
INK_MUTED = "#5B6B82"
HEADING = theme.RAGO_SHADE

_MONTHS = (
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
)  # fmt: skip


class GuideError(ValueError):
    """Erreur dans le contenu du guide, avec un message lisible pour corriger le YAML."""


# --- Contenu ----------------------------------------------------------------------


@dataclass(frozen=True)
class Section:
    """Une partie d'un chapitre, avec éventuellement une illustration tirée de l'épisode."""

    titre: str
    paragraphes: tuple[str, ...]
    illustration: int | None = None
    legende: str = ""


@dataclass(frozen=True)
class Chapter:
    """Un chapitre du guide, associé à un épisode."""

    episode: str
    titre: str
    sous_titre: str
    en_bref: str
    sections: tuple[Section, ...]
    analogie: str
    a_retenir: tuple[str, ...]
    exercice: str
    glossaire: dict[str, str] = field(default_factory=dict)

    @property
    def code(self) -> str:
        """Code de l'épisode, par exemple ``S01E01``."""
        return self.episode.upper()


def _require(data: dict[str, Any], key: str, where: str) -> Any:
    if not isinstance(data, dict) or data.get(key) in (None, "", [], {}):
        raise GuideError(f"{where} : le champ « {key} » est obligatoire.")
    return data[key]


def _as_list(value: Any) -> tuple[str, ...]:
    items = value if isinstance(value, list) else [value]
    return tuple(str(item).strip() for item in items)


def parse_chapter(data: Any, where: str = "Chapitre") -> Chapter:
    """Transforme le contenu YAML d'un chapitre en ``Chapter`` vérifié.

    Raises:
        GuideError: si un champ obligatoire manque ou est mal formé.
    """
    sections = []
    for number, section in enumerate(_require(data, "sections", where), start=1):
        section_where = f"{where}, section {number}"
        illustration = section.get("illustration") if isinstance(section, dict) else None
        if illustration is not None and (not isinstance(illustration, int) or illustration < 1):
            raise GuideError(
                f"{section_where} : « illustration » doit être un numéro de réplique (1, 2…)."
            )
        sections.append(
            Section(
                titre=str(_require(section, "titre", section_where)),
                paragraphes=_as_list(_require(section, "texte", section_where)),
                illustration=illustration,
                legende=str(section.get("legende", "")).strip(),
            )
        )

    glossaire = data.get("glossaire") or {}
    if not isinstance(glossaire, dict):
        raise GuideError(f"{where} : « glossaire » doit associer chaque mot à sa définition.")

    return Chapter(
        episode=str(_require(data, "episode", where)).lower(),
        titre=str(_require(data, "titre", where)),
        sous_titre=str(data.get("sous_titre", "")),
        en_bref=str(_require(data, "en_bref", where)).strip(),
        sections=tuple(sections),
        analogie=str(_require(data, "analogie", where)).strip(),
        a_retenir=_as_list(_require(data, "a_retenir", where)),
        exercice=str(_require(data, "exercice", where)).strip(),
        glossaire={str(k): str(v).strip() for k, v in glossaire.items()},
    )


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise GuideError(f"{path.name} : YAML invalide ({error}).") from error


def load_guide(guide_dir: Path = DEFAULT_GUIDE_DIR) -> tuple[dict[str, Any], list[Chapter]]:
    """Lit les pages fixes et tous les chapitres du guide, dans l'ordre des épisodes.

    Returns:
        Les pages fixes (contenu de ``guide.yaml``) et la liste des chapitres.
    """
    pages = _load_yaml(guide_dir / "guide.yaml")
    for key in ("titre", "bienvenue", "rag_une_page", "programme", "suivre", "licence"):
        _require(pages, key, "guide.yaml")
    chapters = [
        parse_chapter(_load_yaml(path), where=path.name)
        for path in sorted((guide_dir / "chapitres").glob("*.yaml"))
    ]
    return pages, chapters


def _sort_key(term: str) -> str:
    decomposed = unicodedata.normalize("NFKD", term.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def merge_glossary(chapters: list[Chapter]) -> list[tuple[str, str]]:
    """Rassemble les glossaires de tous les chapitres, sans doublon, par ordre alphabétique.

    Si un mot est défini dans plusieurs chapitres, la première définition est gardée.
    """
    merged: dict[str, tuple[str, str]] = {}
    for chapter in chapters:
        for term, definition in chapter.glossaire.items():
            merged.setdefault(_sort_key(term), (term, definition))
    return [merged[key] for key in sorted(merged)]


def markup(text: str, emphasis_color: str = HEADING) -> str:
    """Convertit la mise en forme simple du YAML (``**gras**``, ``*mot*``) pour ReportLab.

    La police Fredoka n'a pas d'italique : ``*mot*`` est affiché en couleur.
    """
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"\*(.+?)\*", rf'<font color="{emphasis_color}">\1</font>', text)


def version_label(chapters: list[Chapter], programme: list[Any]) -> str:
    """Texte de version affiché sur la couverture, par exemple « Version 1 · 1 chapitre sur 12 »."""
    count = len(chapters)
    noun = "chapitre" if count <= 1 else "chapitres"
    return f"Version {count} · {count} {noun} sur {len(programme)}"


# --- Illustrations (Manim) --------------------------------------------------------


@dataclass(frozen=True)
class GuideImages:
    """Les images du guide, déjà rendues en PNG."""

    cover: Path
    schema: Path
    lines: dict[tuple[str, int], Path]


# Partie de l'écran gardée pour les illustrations de chapitre : sous le bandeau du haut,
# jusqu'aux pieds de Rago (au-dessus des sous-titres).
_CROP_TOP_PX = 345
_CROP_BOTTOM_PX = 1275


def _crop_to_content(path: Path, margin: int = 40) -> None:
    from PIL import Image, ImageChops

    image = Image.open(path).convert("RGB")
    background = Image.new("RGB", image.size, theme.BACKGROUND)
    box = ImageChops.difference(image, background).getbbox()
    if box:
        left, top, right, bottom = box
        image = image.crop(
            (
                max(0, left - margin),
                max(0, top - margin),
                min(image.width, right + margin),
                min(image.height, bottom + margin),
            )
        )
    image.save(path)


def render_images(
    chapters: list[Chapter], episodes_dir: Path, cache_dir: Path = DEFAULT_CACHE_DIR
) -> GuideImages:
    """Rend toutes les illustrations du guide avec Manim.

    Les illustrations de chapitre « photographient » l'épisode à la fin d'une réplique. Le
    minutage est recalculé à partir de la voix (déjà en cache si la vidéo a été générée).
    """
    from PIL import Image

    from rago.scenes.base import render_line_still, render_still
    from rago.scenes.guide import CouvertureGuide, SchemaRag
    from rago.script import load_episode
    from rago.timing import build_timeline
    from rago.voice import RAGO_VOICE, generate_line

    cover = render_still(CouvertureGuide, cache_dir / "couverture.png")
    schema = render_still(SchemaRag, cache_dir / "schema_rag.png")
    _crop_to_content(cover)
    _crop_to_content(schema)

    lines: dict[tuple[str, int], Path] = {}
    for chapter in chapters:
        wanted = [s.illustration for s in chapter.sections if s.illustration is not None]
        if not wanted:
            continue
        scripts = sorted(episodes_dir.glob(f"{chapter.episode}_*.yaml"))
        if not scripts:
            raise GuideError(f"Chapitre {chapter.code} : script d'épisode introuvable.")
        episode = load_episode(scripts[0])
        clips = [generate_line(line.texte, RAGO_VOICE) for line in episode.lines]
        timeline = build_timeline(
            [clip.duration for clip in clips], [line.pause_apres for line in episode.lines]
        )
        scene_class = importlib.import_module(f"rago.scenes.{episode.id}").SCENE
        for number in wanted:
            if number > len(episode.lines):
                raise GuideError(f"Chapitre {chapter.code} : la réplique {number} n'existe pas.")
            path = cache_dir / f"{episode.id}_replique{number}.png"
            render_line_still(scene_class, episode, timeline, number - 1, path)
            image = Image.open(path)
            image.crop((0, _CROP_TOP_PX, image.width, _CROP_BOTTOM_PX)).save(path)
            lines[(chapter.episode, number)] = path

    return GuideImages(cover=cover, schema=schema, lines=lines)


# --- Polices ----------------------------------------------------------------------

_FONT_WEIGHTS = {"Fredoka": 400, "Fredoka-Medium": 500, "Fredoka-Bold": 600}


def register_fonts(cache_dir: Path = DEFAULT_CACHE_DIR) -> None:
    """Enregistre Fredoka auprès de ReportLab, en créant ses versions fixes si besoin.

    ReportLab ne sait pas lire les polices « variables » : on en extrait une version par graisse.
    """
    from fontTools.ttLib import TTFont as FontToolsFont
    from fontTools.varLib.instancer import instantiateVariableFont
    from reportlab.lib.fonts import addMapping
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    logging.getLogger("fontTools").setLevel(logging.WARNING)
    fonts_dir = cache_dir / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    for name, weight in _FONT_WEIGHTS.items():
        path = fonts_dir / f"{name}.ttf"
        if not path.exists():
            variable = FontToolsFont(str(theme.FONT_PATH))
            static = instantiateVariableFont(variable, {"wght": weight, "wdth": 100})
            # Chaque graisse reçoit son propre nom : sinon le PDF n'en garderait qu'une.
            for name_id, value in ((1, name), (2, "Regular"), (4, name), (6, name)):
                static["name"].setName(value, name_id, 3, 1, 0x409)
                static["name"].setName(value, name_id, 1, 0, 0)
            static.save(str(path))
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(path)))
    addMapping("Fredoka", 0, 0, "Fredoka")
    addMapping("Fredoka", 1, 0, "Fredoka-Bold")
    addMapping("Fredoka", 0, 1, "Fredoka")
    addMapping("Fredoka", 1, 1, "Fredoka-Bold")


# --- Mise en page (ReportLab) -----------------------------------------------------


def build_pdf(
    pages: dict[str, Any],
    chapters: list[Chapter],
    images: GuideImages,
    output_path: Path,
    today: dt.date | None = None,
) -> Path:
    """Met en page le guide et écrit le fichier PDF.

    Args:
        pages: Les pages fixes (contenu de ``guide.yaml``).
        chapters: Les chapitres, dans l'ordre.
        images: Les illustrations déjà rendues.
        output_path: Le fichier PDF à créer.
        today: Date affichée sur la couverture (aujourd'hui par défaut).

    Returns:
        Le chemin du PDF créé.
    """
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader, simpleSplit
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        Image,
        KeepTogether,
        ListFlowable,
        ListItem,
        NextPageTemplate,
        PageBreak,
        PageTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    register_fonts()
    today = today or dt.date.today()
    page_width, page_height = A4
    margin = 2 * cm
    content_width = page_width - 2 * margin
    color = colors.HexColor

    styles = {
        "kicker": ParagraphStyle(
            "kicker",
            fontName="Fredoka-Bold",
            fontSize=10,
            leading=13,
            textColor=color(theme.ACCENT),
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName="Fredoka-Bold",
            fontSize=26,
            leading=31,
            textColor=color(INK),
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Fredoka",
            fontSize=13,
            leading=17,
            textColor=color(INK_MUTED),
            spaceAfter=14,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Fredoka-Bold",
            fontSize=15,
            leading=19,
            textColor=color(HEADING),
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Fredoka",
            fontSize=11,
            leading=16.5,
            textColor=color(INK),
            spaceAfter=7,
        ),
        "box_title": ParagraphStyle(
            "box_title",
            fontName="Fredoka-Bold",
            fontSize=11.5,
            leading=15,
            textColor=color(INK),
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Fredoka",
            fontSize=9,
            leading=12.5,
            textColor=color(INK_MUTED),
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "small": ParagraphStyle(
            "small", fontName="Fredoka", fontSize=9, leading=12.5, textColor=color(INK_MUTED)
        ),
        "big": ParagraphStyle(
            "big",
            fontName="Fredoka-Bold",
            fontSize=20,
            leading=26,
            textColor=color(theme.ACCENT),
            alignment=TA_CENTER,
            spaceBefore=6,
            spaceAfter=12,
        ),
    }

    def p(text: str, style: str = "body") -> Paragraph:
        return Paragraph(markup(text), styles[style])

    def box(flowables: list, background: str, border: str) -> Table:
        table = Table([[flowables]], colWidths=[content_width])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), color(background)),
                    ("BOX", (0, 0), (-1, -1), 1.5, color(border)),
                    ("ROUNDEDCORNERS", [8, 8, 8, 8]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return table

    def bullets(items: tuple[str, ...] | list[str]) -> ListFlowable:
        return ListFlowable(
            [ListItem(p(item), leftIndent=12, value="•") for item in items],
            bulletType="bullet",
            bulletColor=color(theme.ACCENT),
            bulletFontName="Fredoka",
            leftIndent=12,
        )

    def picture(path: Path, width: float) -> Image:
        reader = ImageReader(str(path))
        img_width, img_height = reader.getSize()
        return Image(str(path), width=width, height=width * img_height / img_width)

    def heading(kicker: str, title: str, subtitle: str = "") -> list:
        items = [p(kicker.upper(), "kicker"), p(title, "h1")]
        items.append(p(subtitle, "subtitle") if subtitle else Spacer(1, 10))
        return items

    # Décor des pages : couverture sombre, pages intérieures claires avec pied de page.
    version = version_label(chapters, pages["programme"])
    date_label = f"{_MONTHS[today.month - 1]} {today.year}"

    def draw_cover(canvas, _doc) -> None:
        canvas.saveState()
        canvas.setFillColor(color(theme.BACKGROUND))
        canvas.rect(0, 0, page_width, page_height, stroke=0, fill=1)

        reader = ImageReader(str(images.cover))
        img_width, img_height = reader.getSize()
        draw_width = 11 * cm
        draw_height = draw_width * img_height / img_width
        canvas.drawImage(
            reader,
            (page_width - draw_width) / 2,
            page_height - 3 * cm - draw_height,
            width=draw_width,
            height=draw_height,
            mask="auto",
        )

        y = page_height - 4.4 * cm - draw_height
        canvas.setFillColor(color(theme.TEXT))
        canvas.setFont("Fredoka-Bold", 34)
        for line in simpleSplit(pages["titre"], "Fredoka-Bold", 34, content_width):
            canvas.drawCentredString(page_width / 2, y, line)
            y -= 40
        canvas.setFillColor(color(theme.TEXT_MUTED))
        canvas.setFont("Fredoka", 14)
        canvas.drawCentredString(page_width / 2, y - 2, pages.get("sous_titre", ""))

        canvas.setFont("Fredoka-Bold", 12)
        pill_width = canvas.stringWidth(version, "Fredoka-Bold", 12) + 30
        pill_y = y - 50
        canvas.setFillColor(color(theme.ACCENT))
        canvas.roundRect(
            (page_width - pill_width) / 2, pill_y, pill_width, 26, 13, stroke=0, fill=1
        )
        canvas.setFillColor(color(theme.BACKGROUND))
        canvas.drawCentredString(page_width / 2, pill_y + 8.5, version)

        canvas.setFillColor(color(theme.TEXT))
        canvas.setFont("Fredoka-Medium", 14)
        canvas.drawCentredString(
            page_width / 2, 2.6 * cm, f"par {pages.get('auteur', theme.SIGNATURE)}"
        )
        canvas.setFillColor(color(theme.TEXT_MUTED))
        canvas.setFont("Fredoka", 10)
        canvas.drawCentredString(page_width / 2, 2.0 * cm, date_label)
        canvas.restoreState()

    def draw_page(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFillColor(color(PAGE_BG))
        canvas.rect(0, 0, page_width, page_height, stroke=0, fill=1)
        canvas.setStrokeColor(color(theme.RAGO_BODY))
        canvas.setLineWidth(1)
        canvas.line(margin, 1.4 * cm, page_width - margin, 1.4 * cm)
        canvas.setFillColor(color(INK_MUTED))
        canvas.setFont("Fredoka", 8.5)
        canvas.drawString(margin, 0.95 * cm, f"{pages['titre']} · {pages.get('auteur', '')}")
        canvas.drawRightString(page_width - margin, 0.95 * cm, str(doc.page))
        canvas.restoreState()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=pages["titre"],
        author=pages.get("auteur", ""),
        subject=version,
    )
    frame = Frame(margin, margin, content_width, page_height - 2 * margin, id="content")
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[frame], onPage=draw_cover),
            PageTemplate(id="page", frames=[frame], onPage=draw_page),
        ]
    )

    story: list = [NextPageTemplate("page"), PageBreak()]

    # Bienvenue
    story += heading("Bienvenue", "Salut, moi c'est Rago !")
    story += [p(text) for text in pages["bienvenue"]]
    if pages.get("comment_lire"):
        story += [
            Spacer(1, 8),
            box(
                [p("Comment lire ce guide", "box_title"), bullets(pages["comment_lire"])],
                "#E3F7F4",
                theme.RAGO_BODY,
            ),
        ]
    story.append(PageBreak())

    # Le RAG en une page
    overview = pages["rag_une_page"]
    story += heading("Vue d'ensemble", "Le RAG en une page")
    story.append(p(overview["intro"]))
    steps = []
    for number, step in enumerate(overview["etapes"], start=1):
        steps.append(p(f"{number}. {step['nom']} ({step['anglais']})", "box_title"))
        steps.append(p(step["texte"]))
    schema_width = 7 * cm
    layout = Table(
        [[picture(images.schema, schema_width), steps]],
        colWidths=[schema_width + 0.6 * cm, content_width - schema_width - 0.6 * cm],
    )
    layout.setStyle(
        TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)])
    )
    story += [Spacer(1, 6), layout, Spacer(1, 10), p(overview["conclusion"])]

    # Chapitres
    for number, chapter in enumerate(chapters, start=1):
        story.append(PageBreak())
        story += heading(f"Chapitre {number} · {chapter.code}", chapter.titre, chapter.sous_titre)
        story.append(
            box([p("En bref", "box_title"), p(chapter.en_bref)], "#E3F7F4", theme.RAGO_BODY)
        )
        for section in chapter.sections:
            block = [p(section.titre, "h2"), *(p(text) for text in section.paragraphes)]
            if section.illustration is not None:
                block.append(Spacer(1, 4))
                block.append(
                    picture(images.lines[(chapter.episode, section.illustration)], 8.5 * cm)
                )
                if section.legende:
                    block.append(Spacer(1, 4))
                    block.append(p(section.legende, "caption"))
            story.append(KeepTogether(block))
        story += [
            Spacer(1, 8),
            KeepTogether(
                box([p("L'analogie", "box_title"), p(chapter.analogie)], "#FFF1C9", theme.IDEA)
            ),
            Spacer(1, 10),
            KeepTogether(
                box(
                    [p("À retenir", "box_title"), bullets(chapter.a_retenir)],
                    "#FFE9CC",
                    theme.ACCENT,
                )
            ),
            Spacer(1, 10),
            KeepTogether(
                box(
                    [p("À toi de jouer", "box_title"), p(chapter.exercice)],
                    "#E3F7F4",
                    theme.RAGO_BODY,
                )
            ),
        ]

    # Programme
    story.append(PageBreak())
    story += heading("La suite", "Les prochains chapitres")
    published = {chapter.episode for chapter in chapters}
    rows = []
    for item in pages["programme"]:
        done = item["id"] in published
        status = '<font color="#1E9E5A"><b>Dans ce guide</b></font>' if done else "Bientôt"
        rows.append(
            [
                p(f"**{item['id'].upper()}**"),
                p(item["titre"]),
                Paragraph(status, styles["small"]),
            ]
        )
    table = Table(rows, colWidths=[2.3 * cm, content_width - 5.3 * cm, 3 * cm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, color("#E4D9C2")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    story.append(table)

    # Glossaire
    story.append(PageBreak())
    story += heading("Les mots à connaître", "Glossaire")
    story += [p(f"**{term}** : {definition}") for term, definition in merge_glossary(chapters)]

    # Suivre l'histoire
    follow = pages["suivre"]
    story.append(PageBreak())
    story += heading("Et maintenant ?", "Pour suivre l'histoire")
    story.append(p(follow["texte"]))
    story += [p(account, "big") for account in follow.get("comptes", [])]
    if follow.get("repo"):
        repo = html.escape(follow["repo"])
        story.append(p(follow.get("code", "")))
        story.append(
            Paragraph(f'<link href="{repo}" color="{HEADING}"><u>{repo}</u></link>', styles["body"])
        )
    story += [Spacer(1, 24), p(pages["licence"], "small"), p(f"{version} · {date_label}", "small")]

    doc.build(story)
    return output_path


def build_guide(
    guide_dir: Path = DEFAULT_GUIDE_DIR,
    episodes_dir: Path = Path("episodes"),
    output_path: Path = Path("output") / "guide_rag.pdf",
) -> Path:
    """Génère le guide PDF complet : lecture du contenu, illustrations, mise en page."""
    print("1/3 · Lecture du contenu du guide")
    pages, chapters = load_guide(guide_dir)
    print(f"      {len(chapters)} chapitre(s) : {', '.join(c.code for c in chapters)}")
    print("2/3 · Illustrations (Manim)")
    images = render_images(chapters, episodes_dir)
    print("3/3 · Mise en page du PDF")
    build_pdf(pages, chapters, images, output_path)
    print(f"✅ Guide : {output_path}")
    return output_path
