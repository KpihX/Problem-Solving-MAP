# Problème Solving en Mathématiques Appliquées — TPs

Bienvenue dans ce dépôt regroupant mes travaux pratiques (TP) du cours « Problem Solving en Mathématiques Appliquées » (MODAL) à l’École polytechnique.

Ce README a pour objectifs de:

- donner une vue d’ensemble claire et illustrée des TPs,
- expliquer comment installer l’environnement et exécuter les notebooks,
- documenter la structure du dépôt et les conventions,
- rester modulaire et facile à mettre à jour au fur et à mesure des nouveaux TPs.

> Astuce: Plusieurs dossiers contiennent un sous-dossier `style/` avec un fichier `custom2.css` pour améliorer le rendu des notebooks. Pensez à l’activer si nécessaire (voir plus bas).

## Aperçu rapide

- Langage principal: Python (Notebooks Jupyter)
- Domaines couverts: valeurs propres, compression d’images (JPEG), bandits multi-bras et renforcement, tri aléatoire, maillage, arrêt optimal, équation d’Eikonale.
- Organisation: 1 dossier par TP, avec un ou plusieurs notebooks, éventuellement des sous-dossiers `figures/` ou `style/`.

## Structure du dépôt

```text
TP1_Eigenvalue/
  Eigenvalue.ipynb
TP2_Compression_Jpeg/
  Compression_Jpeg_.ipynb
TP3_Bandits_Renforcement/
  Bandits_Renforcement.ipynb
  figures/
  style/
    custom2.css
TP4_Tri_Randomisé/
  Alea2-AlgoRand/
  figures/
  style/
    custom2.css
TP5_Maillage/
  Maillage.ipynb
TP6_Arret_Optimal/
  Arret_Optimal.ipynb
  style/
    custom2.css
TP7_Eqn_Eikonale/
  Eqn_Eikonal.ipynb
```

Notes:

- `style/custom2.css` est utilisé par certains notebooks pour un rendu visuel plus agréable.

## Pré-requis

- Python 3.9+ conseillé
- Jupyter (Notebook ou Lab) et dépendances scientifiques courantes

Vous trouverez une base minimale de dépendances dans `requirements.txt`.

## Installation (Windows PowerShell)

- Créer un environnement virtuel local et installer les dépendances minimales:

```powershell
# À la racine du dépôt
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Lancer Jupyter (au choix):

```powershell
# Option 1: Jupyter Lab
jupyter lab

# Option 2: Jupyter Notebook classique
jupyter notebook
```

- Dans VS Code, vous pouvez simplement ouvrir un notebook `.ipynb` et sélectionner le kernel Python de l’environnement `.venv` (en bas à droite, sélecteur de kernel).

## Utiliser la feuille de style `custom2.css`

Certains notebooks référencent `style/custom2.css` pour améliorer la typographie et la mise en page. Si le notebook ne la charge pas automatiquement, vous pouvez insérer au début du notebook une cellule Markdown:

```markdown
<link rel="stylesheet" href="style/custom2.css">
```

Assurez-vous que le fichier existe dans le dossier `style/` du TP courant.

## Comment exécuter un TP

1) Ouvrez le dossier du TP, par exemple `TP2_Compression_Jpeg/`.
2) Ouvrez le notebook associé (`Compression_Jpeg_.ipynb`).
3) Sélectionnez le kernel Python de `.venv` si ce n’est pas déjà fait.
4) Exécutez les cellules dans l’ordre (ou section par section selon les consignes du notebook).

> Conseils:
>
> - Si des données ou chemins sont requis, vérifiez le haut du notebook (cellules d’imports et de configuration).
> - Si des images ne s’affichent pas, vérifiez que `matplotlib` est bien installé et que les chemins pointent vers des fichiers existants.

## Liste des TPs

Mettez à jour manuellement la liste ci-dessous lorsque vous ajoutez un nouveau TP.

- TP1 — Eigenvalue: méthodes numériques autour des valeurs propres de matrices (p. ex. méthode de la puissance, déflation, spectre de matrices symétriques). Notebook: `TP1_Eigenvalue/Eigenvalue.ipynb`.
- TP2 — Compression JPEG: transformée en cosinus discrète (DCT), quantification, parcours zig-zag, métriques (PSNR), et visualisation d’artéfacts. Notebook: `TP2_Compression_Jpeg/Compression_Jpeg_.ipynb`.
- TP3 — Bandits & Renforcement: bandits à K bras (ε-greedy, UCB, softmax, éventuellement Thompson sampling), exploration/exploitation, courbes de regret. Notebook: `TP3_Bandits_Renforcement/Bandits_Renforcement.ipynb`.
- TP4 — Tri Randomisé: algorithmes de tri à pivot aléatoire (type QuickSort), analyse de complexité moyenne, et effets du hasard. Dossier: `TP4_Tri_Randomisé/` (pas de notebook listé actuellement).
- TP5 — Maillage: notions de maillage/triangulation (p. ex. Delaunay), éventuellement relaxation de Lloyd et mesures de qualité. Notebook: `TP5_Maillage/Maillage.ipynb`.
- TP6 — Arrêt Optimal: problèmes d’arrêt optimal (ex: problème des secrétaires), stratégies, simulations et analyses probabilistes. Notebook: `TP6_Arret_Optimal/Arret_Optimal.ipynb`.
- TP7 — Équation d’Eikonale: schémas upwind, Fast Marching/Propagation de front, visualisation des champs de distance. Notebook: `TP7_Eqn_Eikonale/Eqn_Eikonal.ipynb`.

## Détails par TP (aperçu)

- TP1 Eigenvalue

  - Objectifs: manipuler des méthodes numériques de calcul de valeurs propres et vecteurs propres.
  - Points clés: méthode de la puissance, normalisation, convergences, déflation.
  - Fichier principal: `TP1_Eigenvalue/Eigenvalue.ipynb`.
- TP2 Compression JPEG

  - Objectifs: comprendre et ré-implémenter les étapes principales de JPEG.
  - Points clés: DCT bloc, quantification, zig-zag, sous-échantillonnage, reconstruction, PSNR.
  - Fichier principal: `TP2_Compression_Jpeg/Compression_Jpeg_.ipynb`.
- TP3 Bandits & Renforcement

  - Objectifs: étudier les politiques d’exploration/exploitation.
  - Points clés: ε-greedy, UCB, softmax, visualisation de courbes (récompenses cumulées, regret).
  - Fichier principal: `TP3_Bandits_Renforcement/Bandits_Renforcement.ipynb`.
- TP4 Tri Randomisé

  - Objectifs: analyser un tri aléatoire et ses performances.
  - Points clés: pivot aléatoire, complexité moyenne, robustesse.
  - Dossier: `TP4_Tri_Randomisé/`.
- TP5 Maillage

  - Objectifs: générer/qualifier des maillages triangulés et visualiser les résultats.
  - Points clés: triangulation, éventuellement Delaunay, métriques de qualité.
  - Fichier principal: `TP5_Maillage/Maillage.ipynb`.
- TP6 Arrêt Optimal

  - Objectifs: formuler une stratégie d’arrêt optimale dans un cadre probabiliste.
  - Points clés: règle 1/e (secrétaires), simulations Monte Carlo, compromis observation/décision.
  - Fichier principal: `TP6_Arret_Optimal/Arret_Optimal.ipynb`.
- TP7 Équation d’Eikonale

  - Objectifs: calculer un champ de distance répondant à |∇u| = f.
  - Points clés: schémas upwind, Fast Marching/Propagation, visualisations 2D.
  - Fichier principal: `TP7_Eqn_Eikonale/Eqn_Eikonal.ipynb`.

## Ajouter un nouveau TP (modulaire)

1) Créez un nouveau dossier à la racine avec le schéma `TPX_TitreCourt/` (ex: `TP8_Wavelet/`).
2) Ajoutez un ou plusieurs notebooks `.ipynb` dans ce dossier.
3) Optionnel: ajoutez `style/custom2.css` et un dossier `figures/` pour vos sorties.
4) Mettez à jour la section « Liste des TPs » ci-dessus en ajoutant une ligne pour votre nouveau TP.

## Stratégie .gitignore

- Tous les fichiers d’images (png, jpg, etc.) sont ignorés afin d’éviter d’alourdir l’historique.
- Les répertoires `images/` (à n’importe quel niveau) sont ignorés.
- Les artefacts temporaires de Python/Jupyter/OS/éditeur sont ignorés.

Si vous souhaitez versionner une image précise, placez-la dans un dossier non ignoré et ajustez `.gitignore` localement (ou servez-vous du tracking explicite via `git add -f chemin/vers/image.png`).

## Questions / aides

- Si un notebook ne s’exécute pas: vérifiez l’environnement (`pip list`), les versions de `numpy`, `scipy`, `matplotlib`, et les chemins d’accès.
- Vous pouvez également me signaler un problème en ouvrant une issue (si le dépôt est sur un gestionnaire Git) ou en me contactant directement.

Bon travail et bonne exploration !
