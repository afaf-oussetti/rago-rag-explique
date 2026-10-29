# 🤖 Rago, le robot qui apprend à ne plus mentir

Une série de Reels Instagram qui explique le **RAG** (Retrieval-Augmented Generation) simplement,
par **Afaf.IA**.

Rago est un petit robot (un LLM) qui invente des réponses. À chaque épisode, il découvre une brique
du RAG pour arrêter d'halluciner.

**Toutes les vidéos sont générées à 100 % en Python** : animations, voix robot, sous-titres, montage.
Ce repo contient tout le code : tu peux le lire, le lancer et l'adapter à tes propres projets.

<p align="center">
  <img src="docs/apercu.gif" alt="Aperçu de l'épisode S01E01 : Rago affirme que la tour Eiffel a été construite en 1972 par des pingouins" width="300">
</p>

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

Au bout de quelques minutes, tu obtiens dans le dossier `output/` :

- `s01e01.mp4` : la vidéo finale (verticale 1080 × 1920, 30 fps, avec voix, sous-titres et signature) ;
- `s01e01.srt` : les sous-titres, à importer sur YouTube ou TikTok si tu veux.

L'animation est l'étape la plus longue. Les épisodes déjà publiés sont listés dans
[docs/STATUS.md](docs/STATUS.md).

Pour voir Rago et la charte graphique en images (dans `output/charte/`) :

```bash
python -m rago preview
```

Pour entendre la voix de Rago et deux autres variantes (dans `output/voix/`) :

```bash
python -m rago voices
```

> 🌐 La voix est générée avec [edge-tts](https://github.com/rany2/edge-tts), qui utilise le service
> de voix de Microsoft Edge : gratuit, sans compte ni clé secrète, mais il faut **une connexion
> internet**. Chaque réplique générée est gardée dans `cache/voice/` et n'est plus redemandée.

## Comment ça marche

1. Le script de l'épisode est lu depuis `episodes/` (un fichier YAML : répliques + indications d'animation).
2. La voix de Rago est générée réplique par réplique (edge-tts + effet robot avec pydub), et chaque durée est mesurée.
3. L'animation Manim est calée sur ces durées.
4. MoviePy assemble animation, voix, sous-titres et signature, puis exporte le MP4 vertical (1080 × 1920, 30 fps).

## Le guide PDF

Le PDF promis dans les vidéos (« Commente RAG pour recevoir le PDF ») est généré lui aussi en Python,
avec les mêmes couleurs, la même police et des illustrations tirées directement des épisodes :

```bash
python -m rago guide      # crée output/guide_rag.pdf
```

Son contenu est dans [`guide/`](guide/) : `guide.yaml` pour les pages fixes et un fichier par
chapitre dans `guide/chapitres/`. Le guide grandit à chaque épisode : ajoute un chapitre, relance la
commande, et la version, le sommaire et le glossaire se mettent à jour tout seuls.

## Créer ton propre épisode

1. Écris le script dans `episodes/s09e01_mon_sujet.yaml`, en t'inspirant de
   [`s01e01_hallucination.yaml`](episodes/s01e01_hallucination.yaml) : une liste de répliques, chacune
   avec sa section, son texte et l'expression de Rago.
2. Crée la scène `src/rago/scenes/s09e01.py` : une classe qui hérite de `EpisodeScene`, avec un bloc
   `with self.line(n):` par réplique. Tout ce qui est écrit dans ce bloc est calé automatiquement
   sur la voix.
3. Lance `python -m rago build s09e01`.

## Structure du projet

```
episodes/        scripts des épisodes (YAML)
src/rago/        le code : personnage, thème, voix, scènes, sous-titres, assemblage, CLI
assets/          polices et sons libres de droits (sources citées)
guide/           contenu du guide PDF (pages fixes + un chapitre par épisode)
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
