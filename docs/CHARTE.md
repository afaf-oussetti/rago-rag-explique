# Charte graphique et sonore

Les valeurs ci-dessous sont définies dans le code, dans [`src/rago/theme.py`](../src/rago/theme.py).
Pour voir la charte en image :

```bash
python -m rago preview      # crée output/charte/charte_ecran.png et charte_expressions.png
```

## Couleurs

Chaque couleur a un rôle, toujours le même d'un épisode à l'autre : le public apprend le code
sans s'en rendre compte.

| Rôle | Couleur | Code |
|---|---|---|
| Fond | bleu nuit | `#0E1A2B` |
| Rago | turquoise | `#2EC4B6` (contours `#1E8F86`) |
| Accent : titres, flèches, mots-clés | orange | `#FF9F1C` |
| **Invention, hallucination, erreur** | rose-violet | `#E056FD` |
| **Source fiable, bonne réponse** | vert | `#4ADE80` |
| Documents et fiches | jaune papier | `#FFE8A3` |
| Idée (ampoule) | jaune | `#FFD23F` |
| Texte principal | crème | `#FFF8E7` |
| Texte secondaire, signature | gris-bleu | `#8FA3BF` |

## Typographie

- **Fredoka** (Google Fonts, licence SIL OFL 1.1), stockée dans `assets/fonts/` : aucun besoin de l'installer.
- Titres en gras, sous-titres en « medium », textes secondaires en normal.
- Tailles de référence pour un écran de 1080 px de large : titre 44, sous-titre 40, étiquette 24, signature 22.

## Design de Rago

Rago est construit uniquement avec des formes simples ([`src/rago/character.py`](../src/rago/character.py)) :

- une tête turquoise aux coins arrondis, avec un **écran-visage** sombre. Les yeux et la bouche sont lumineux ;
- une **antenne-ampoule** et un **voyant sur le ventre**, de la même couleur, qui changent selon son état ;
- un petit corps arrondi, deux bras et deux jambes courtes. Il est mignon et rond, jamais inquiétant.

### Expressions

| Clé (YAML) | Visage | Ampoule | Bras |
|---|---|---|---|
| `neutre` | yeux ovales, petit sourire | cyan | repos |
| `content` | yeux fermés ^^, sourire | cyan | repos |
| `fier` | yeux fermés ^^, grand sourire | orange | mains sur les hanches |
| `gene` | yeux fuyants, bouche ondulée, joues roses | rose-violet | repos |
| `perdu` | yeux en spirale, bouche en « o » | rose-violet | repos |
| `pensif` | regard vers le haut, bouche de côté | jaune | repos |
| `excite` | yeux étoiles, grand sourire | jaune | bras levés |

Code couleur de l'ampoule : **rose-violet = Rago invente**, **jaune = Rago a une idée**.

## Mise en page

- Format : MP4 vertical 1080 × 1920, 30 fps, 40 à 60 s.
- **Zones recouvertes par Instagram** : les 250 px du haut et les 420 px du bas. On n'y met rien d'important.
- Titre de l'épisode : étiquette orange « S01E01 », puis le titre, juste sous la zone du haut.
- Sous-titres : sur fond sombre arrondi, juste au-dessus de la zone du bas, avec le mot-clé en orange.
- Signature « Afaf.IA » : petite, gris-bleu, semi-transparente, sous les sous-titres.

## Ton de la voix

Rago est un **petit robot malin** : il parle avec assurance (même quand il se trompe !), sur un ton
léger, chaleureux et bien compréhensible, jamais inquiétant.

Réglages officiels, préréglage `A` (`RAGO_VOICE` dans [`src/rago/voice.py`](../src/rago/voice.py)) :

| Réglage | Valeur |
|---|---|
| Voix edge-tts | `fr-FR-HenriNeural` |
| Vitesse | +5 % |
| Hauteur | +25 Hz (un peu plus aiguë, plus « petit robot ») |
| Écho | 45 ms, −16 dB (très court, effet « boîtier de robot ») |
| Touche métallique | aucune |

Les silences de début et de fin sont coupés, et le volume est normalisé.

Pour réécouter les variantes comparées au jalon 2 (A, B, C) :

```bash
python -m rago voices      # crée output/voix/variante_A.wav, _B.wav, _C.wav
```

### Écriture des répliques

- Des phrases courtes : environ 2,5 mots par seconde avec cette voix.
- Le hook tient en 3 s, soit 7 à 8 mots maximum.
- La ponctuation guide l'intonation : « ? » et « ! » sont bien rendus, et « … » crée une pause.
