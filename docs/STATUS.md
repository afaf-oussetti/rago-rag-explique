# Suivi du projet

## Jalons

| Jalon | Contenu | État |
|---|---|---|
| 0 | Initialisation du repo (structure, outils, CI) | ✅ Terminé |
| 1 | Charte graphique et design de Rago | ✅ Terminé |
| 2 | Voix robot (2 ou 3 variantes) | ✅ Terminé (variante A) |
| 3 | Pipeline complet + épisode pilote S01E01 | ✅ Terminé |
| 4 | Guide PDF du RAG (enrichi à chaque épisode) | ✅ Terminé (version 1) |

## Épisodes

| Épisode | Notion | Script | Vidéo |
|---|---|---|---|
| S01E01 | L'hallucination des LLM | ✅ Validé | ✅ 66,8 s · chapitre du guide ✅ |
| S01E02 | Le principe du RAG | — | — |
| S01E03 | Le chunking | — | — |
| S01E04 | Les embeddings | — | — |
| S01E05 | Recherche vectorielle, similarité cosinus | — | — |
| S01E06 | Bases vectorielles (FAISS, Chroma, pgvector) | — | — |
| S01E07 | Prompt augmenté, fenêtre de contexte | — | — |
| S02E01 | Recherche hybride (BM25 + vecteurs) | — | — |
| S02E02 | Reranking | — | — |
| S02E03 | Réécriture de requête, HyDE | — | — |
| S02E04 | Métadonnées | — | — |
| S02E05 | Évaluer un RAG | — | — |

## Journal des sessions

### 2026-10-28 · Jalon 0

- Structure du repo, `pyproject.toml`, ruff, pre-commit, CI GitHub Actions
- CLI minimale : `python -m rago build s01e01` trouve le script (pipeline à venir)
- Premier brouillon du script S01E01
- Reste à installer ffmpeg avant le jalon 2

### 2026-10-29 · Jalon 1

- Outils vidéo installés (Manim 0.22, MoviePy, edge-tts, pydub) et ffmpeg
- Palette, police Fredoka (OFL), zones de sécurité Instagram dans `theme.py`
- Rago et ses 7 expressions dans `character.py`, composants communs dans `components.py`
- `python -m rago preview` rend les planches de charte dans `output/charte/`
- Tests du personnage (ignorés en CI tant que Manim n'y est pas installé)

### 2026-10-29 · Jalon 2

- `voice.py` : préréglages de voix, effet robot (métal + écho), coupe des silences, cache, durées
- 3 variantes comparées (`python -m rago voices`) : **A · Petit robot malin** retenue (Henri, +25 Hz, +5 %, écho 45 ms)
- À prévoir au jalon 3 : raccourcir le hook de S01E01 (~5,5 s actuellement, objectif 3 s)

### 2026-10-29 · Jalon 3

- Pipeline complet en une commande : `python -m rago build s01e01`
  (script YAML → voix → minutage → animation Manim → sous-titres → assemblage MoviePy → MP4 + SRT)
- `EpisodeScene` : chaque `with self.line(n)` est calé automatiquement sur la voix ; Rago rebondit quand il parle
- Durée cible passée à 65-80 s (plus d'une minute : rémunération TikTok) ; `pause_apres` pour régler le rythme
- Script S01E01 réécrit et validé (12 répliques, appel à s'abonner + « Commente RAG »)
- Épisode pilote S01E01 validé (66,8 s) ; GIF d'aperçu dans le README
- Décision : le PDF promis est un **guide complet du RAG**, enrichi à chaque épisode (jalon dédié)

### 2026-10-29 · Jalon 4

- Guide PDF « Le RAG expliqué par Rago » : `python -m rago guide` → `output/guide_rag.pdf`
- Version 1 (8 pages) : couverture, bienvenue, le RAG en une page, chapitre 1, programme, glossaire, suivre
- Contenu dans `guide/` (YAML) ; illustrations « photographiées » dans les scènes Manim (`render_line_still`)
- ReportLab + Fredoka en versions fixes (fontTools) ; licence du PDF : CC BY-NC 4.0
- À chaque nouvel épisode : ajouter `guide/chapitres/<id>.yaml` puis régénérer le guide
