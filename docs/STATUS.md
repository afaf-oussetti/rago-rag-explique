# Suivi du projet

## Jalons

| Jalon | Contenu | Ã‰tat |
|---|---|---|
| 0 | Initialisation du repo (structure, outils, CI) | âœ… TerminÃ© |
| 1 | Charte graphique et design de Rago | âœ… TerminÃ© |
| 2 | Voix robot (2 ou 3 variantes) | âœ… TerminÃ© (variante A) |
| 3 | Pipeline complet + Ã©pisode pilote S01E01 | âœ… TerminÃ© |
| 4 | Guide PDF du RAG (enrichi Ã  chaque Ã©pisode) | ðŸ”Ž En validation |

## Ã‰pisodes

| Ã‰pisode | Notion | Script | VidÃ©o |
|---|---|---|---|
| S01E01 | L'hallucination des LLM | âœ… ValidÃ© | âœ… 66,8 s Â· chapitre du guide âœ… |
| S01E02 | Le principe du RAG | â€” | â€” |
| S01E03 | Le chunking | â€” | â€” |
| S01E04 | Les embeddings | â€” | â€” |
| S01E05 | Recherche vectorielle, similaritÃ© cosinus | â€” | â€” |
| S01E06 | Bases vectorielles (FAISS, Chroma, pgvector) | â€” | â€” |
| S01E07 | Prompt augmentÃ©, fenÃªtre de contexte | â€” | â€” |
| S02E01 | Recherche hybride (BM25 + vecteurs) | â€” | â€” |
| S02E02 | Reranking | â€” | â€” |
| S02E03 | RÃ©Ã©criture de requÃªte, HyDE | â€” | â€” |
| S02E04 | MÃ©tadonnÃ©es | â€” | â€” |
| S02E05 | Ã‰valuer un RAG | â€” | â€” |

## Journal des sessions

### 2026-10-28 Â· Jalon 0

- Structure du repo, `pyproject.toml`, ruff, pre-commit, CI GitHub Actions
- CLI minimale : `python -m rago build s01e01` trouve le script (pipeline Ã  venir)
- Premier brouillon du script S01E01
- Reste Ã  installer ffmpeg avant le jalon 2

### 2026-10-29 Â· Jalon 1

- Outils vidÃ©o installÃ©s (Manim 0.22, MoviePy, edge-tts, pydub) et ffmpeg
- Palette, police Fredoka (OFL), zones de sÃ©curitÃ© Instagram dans `theme.py`
- Rago et ses 7 expressions dans `character.py`, composants communs dans `components.py`
- `python -m rago preview` rend les planches de charte dans `output/charte/`
- Tests du personnage (ignorÃ©s en CI tant que Manim n'y est pas installÃ©)

### 2026-10-29 Â· Jalon 2

- `voice.py` : prÃ©rÃ©glages de voix, effet robot (mÃ©tal + Ã©cho), coupe des silences, cache, durÃ©es
- 3 variantes comparÃ©es (`python -m rago voices`) : **A Â· Petit robot malin** retenue (Henri, +25 Hz, +5 %, Ã©cho 45 ms)
- Ã€ prÃ©voir au jalon 3 : raccourcir le hook de S01E01 (~5,5 s actuellement, objectif 3 s)

### 2026-10-29 Â· Jalon 3

- Pipeline complet en une commande : `python -m rago build s01e01`
  (script YAML â†’ voix â†’ minutage â†’ animation Manim â†’ sous-titres â†’ assemblage MoviePy â†’ MP4 + SRT)
- `EpisodeScene` : chaque `with self.line(n)` est calÃ© automatiquement sur la voix ; Rago rebondit quand il parle
- DurÃ©e cible passÃ©e Ã  65-80 s (plus d'une minute : rÃ©munÃ©ration TikTok) ; `pause_apres` pour rÃ©gler le rythme
- Script S01E01 rÃ©Ã©crit et validÃ© (12 rÃ©pliques, appel Ã  s'abonner + Â« Commente RAG Â»)
- Ã‰pisode pilote S01E01 validÃ© (66,8 s) ; GIF d'aperÃ§u dans le README
- DÃ©cision : le PDF promis est un **guide complet du RAG**, enrichi Ã  chaque Ã©pisode (jalon dÃ©diÃ©)

### 2026-10-29 Â· Jalon 4

- Guide PDF Â« Le RAG expliquÃ© par Rago Â» : `python -m rago guide` â†’ `output/guide_rag.pdf`
- Version 1 (8 pages) : couverture, bienvenue, le RAG en une page, chapitre 1, programme, glossaire, suivre
- Contenu dans `guide/` (YAML) ; illustrations Â« photographiÃ©es Â» dans les scÃ¨nes Manim (`render_line_still`)
- ReportLab + Fredoka en versions fixes (fontTools) ; licence du PDF : CC BY-NC 4.0
- Ã€ chaque nouvel Ã©pisode : ajouter `guide/chapitres/<id>.yaml` puis rÃ©gÃ©nÃ©rer le guide
