# Suivi du projet

## Jalons

| Jalon | Contenu | État |
|---|---|---|
| 0 | Initialisation du repo (structure, outils, CI) | ✅ Terminé |
| 1 | Charte graphique et design de Rago | 🔎 En validation |
| 2 | Voix robot (2 ou 3 variantes) | ⏳ À faire |
| 3 | Pipeline complet + épisode pilote S01E01 | ⏳ À faire |

## Épisodes

| Épisode | Notion | Script | Vidéo |
|---|---|---|---|
| S01E01 | L'hallucination des LLM | Brouillon | — |
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
