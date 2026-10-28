# 🤖 Rago, le robot qui apprend à ne plus mentir

Une série de Reels Instagram qui explique le **RAG** (Retrieval-Augmented Generation) simplement,
par **Afaf.IA**.

Rago est un petit robot (un LLM) qui invente des réponses. À chaque épisode, il découvre une brique
du RAG pour arrêter d'halluciner.

**Toutes les vidéos sont générées à 100 % en Python** : animations, voix robot, sous-titres, montage.
Ce repo contient tout le code : tu peux le lire, le lancer et l'adapter à tes propres projets.

> 🎬 *Aperçu animé à venir.*

---

## Ce qu'il te faut

| Outil | À quoi il sert | Installation |
|---|---|---|
| **Python 3.11 ou plus** | faire tourner le code | [python.org/downloads](https://www.python.org/downloads/) (sous Windows, coche « Add Python to PATH ») |
| **ffmpeg** | lire et écrire l'audio et la vidéo | Windows : `winget install ffmpeg` · macOS : `brew install ffmpeg` · Linux : `sudo apt install ffmpeg` |
| **Git** | télécharger ce repo | [git-scm.com](https://git-scm.com/) |

Vérifie que tout est bien installé (chaque commande doit afficher un numéro de version) :

```bash
python --version
ffmpeg -version
git --version
```

## Installation pas à pas

**1. Télécharger le projet**

```bash
git clone https://github.com/afaf-oussetti/rago-rag-explique.git
cd rago-rag-explique
```

**2. Créer un environnement virtuel** (une « boîte » isolée pour les bibliothèques du projet)

```bash
python -m venv .venv
```

Puis l'activer :

- Windows (PowerShell) : `.venv\Scripts\Activate.ps1`
- macOS / Linux : `source .venv/bin/activate`

Le début de ta ligne de commande affiche maintenant `(.venv)`.

**3. Installer le projet**

```bash
pip install -e ".[video,dev]"
```

## Générer un épisode en une commande

```bash
python -m rago build s01e01
```

La vidéo finale arrive dans le dossier `output/`.

> 🚧 Le pipeline de génération est en cours de construction : voir [docs/STATUS.md](docs/STATUS.md).

## Comment ça marche

1. Le script de l'épisode est lu depuis `episodes/` (un fichier YAML : répliques + indications d'animation).
2. La voix de Rago est générée réplique par réplique (edge-tts + effet robot avec pydub), et chaque durée est mesurée.
3. L'animation Manim est calée sur ces durées.
4. MoviePy assemble animation, voix, sous-titres et signature, puis exporte le MP4 vertical (1080 × 1920, 30 fps).

## Structure du projet

```
episodes/        scripts des épisodes (YAML)
src/rago/        le code : personnage, thème, voix, scènes, sous-titres, assemblage, CLI
assets/          polices et sons libres de droits (sources citées)
docs/            charte graphique et suivi d'avancement
tests/           tests automatiques
```

## Les épisodes

**Saison 1 · Rago apprend à chercher**

1. Rago invente des réponses : l'hallucination des LLM
2. Rago reçoit une bibliothèque : le principe du RAG
3. Rago découpe les livres en fiches : le chunking
4. Rago transforme les mots en coordonnées : les embeddings
5. Rago trouve la fiche la plus proche : la recherche vectorielle
6. Rago range ses fiches : les bases vectorielles
7. Rago répond avec ses sources : le prompt augmenté

**Saison 2 · Rago devient expert**

1. Mots-clés et sens : la recherche hybride
2. Rago trie ses résultats : le reranking
3. Rago reformule la question : la réécriture de requête et HyDE
4. Rago filtre ses fiches : les métadonnées
5. Rago passe un examen : évaluer un RAG

## Pour contribuer

```bash
pre-commit install   # active les vérifications automatiques avant chaque commit
pytest               # lance les tests
ruff check .         # vérifie la qualité du code
```

## Licence

[MIT](LICENSE) : tu peux réutiliser ce code librement, en citant la source.
