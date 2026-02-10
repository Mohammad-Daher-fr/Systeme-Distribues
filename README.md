# Mohammad Daher – Compte rendu – TP Stockage : modes d’accès (FS / Memcached / LRU)

## 1. Objectif du TP
L’objectif de ce TP est de comparer plusieurs modes de stockage et d’accès à des données binaires (ici une image) :
- stockage **sur système de fichiers** (disque),
- stockage **en mémoire** via un serveur **memcached**,
- ajout d’un mécanisme **LRU** (Least Recently Used) pour gérer l’éviction quand la capacité du cache est limitée.

L’idée est de vérifier la **fonctionnalité** (non-corruption des données) et d’observer des **temps d’accès**.

---

## 2. Environnement et outils
- Langage : **Python 3**
- Bibliothèques : `Pillow` (manipulation images), `pymemcache` (client memcached)
- Environnement : **WSL** (Windows Subsystem for Linux)
- Serveur cache : **memcached** sur `localhost:11211`
- Vérification intégrité : hash **SHA256**
- Vérification visuelle : génération d’images “preview” et ouverture automatique (WSL → `explorer.exe`)

---

## 3. Partie 1 — Stockage sur système de fichiers (FS)

### 3.1. Principe
On implémente une abstraction minimale du système de fichiers via une classe `FS` :
- `create(path, is_dir=True/False, data=...)`
- `list(path)`
- `read(path)`
- `delete(path)`

### 3.2. Expérimentation
Le script réalise :
1) création d’un répertoire de travail `work/` et d’un sous-dossier `work/R/`,  
2) lecture de l’image d’entrée `data/image.png` en bytes `T`,  
3) écriture de `T` dans un fichier `F` dans `work/R/`,  
4) relecture du fichier en bytes `T2`,  
5) comparaison `SHA256(T)` et `SHA256(T2)` + création de previews.

**Commande d’exécution :**
```bash
python -m scripts.demo_fs
```

**Vérification des résultats :**
- vérifier dans la sortie console que `SHA256(T) == SHA256(T2)` et/ou que le script indique l’absence de corruption,
- vérifier visuellement les fichiers de preview générés dans `work/` (ouverture automatique).

### 3.3. Résultat
- Les hashes SHA256 sont identiques → **pas de corruption**
- Les previews confirment visuellement que l’image copiée est correcte.

Remarque importante : les lectures sur disque peuvent être influencées par le **cache du système d’exploitation** (page cache), ce qui peut rendre certaines lectures très rapides si on relit plusieurs fois le même fichier.

---

## 4. Partie 2 — Stockage en RAM via Memcached

### 4.1. Principe
Au lieu d’écrire dans un fichier, on envoie les bytes `T` à un serveur memcached :
- `set(K, T)` (écriture sous une clé `K`)
- `get(K)` (lecture → `T2`)
On vérifie ensuite l’intégrité et on produit des previews.

**Commande d’exécution :**
```bash
python -m scripts.main_mem
```

**Vérification des résultats :**
- vérifier que le script affiche `T2` avec la même taille que `T`,
- vérifier que `SHA256(T) == SHA256(T2)`,
- vérifier visuellement les previews générées dans `work/previews_mem/` (ouverture automatique).

### 4.2. Problème rencontré
Avec une image de taille ~3.1 MB, l’écriture échouait (lecture renvoyait `None`).  
Cela vient du fait que memcached impose souvent une **limite de taille par item** (souvent autour de 1 MB par défaut).  
La solution choisie ici a été d’utiliser une image plus petite (~1 MB).

### 4.3. Résultat (mesures)
Exécution avec `T: size = 1 044 597 bytes` :
- Écriture memcached : **4.289 ms**
- Lecture memcached : **2.040 ms**
- `SHA256(T) == SHA256(T2)` → **pas de corruption**
- Previews générées correctement

Conclusion : memcached permet un stockage en RAM via un service, avec un temps d’accès faible, mais dépend de limites de configuration (taille max objet, mémoire disponible, etc.).

---

## 5. Partie 3 — LRU + intégration Memcached

### 5.1. Principe
On ajoute une politique d’éviction **LRU** pour limiter le nombre d’objets conservés.

Implémentation :
- structure LRU = **liste doublement chaînée**
  - `head` = élément le plus récemment utilisé (MRU)
  - `tail` = élément le moins récemment utilisé (LRU)
- un dictionnaire `key → node` permet les opérations en **O(1)**

Règles :
- `create(k)` insère `k` en MRU et renvoie les clés expulsées si capacité dépassée.
- `read(k)` si hit → `touch(k)` pour remonter la clé en MRU.
- Intégration avec memcached :
  - après `set(k, data)`, on appelle `LRU.create(k)`
  - pour chaque clé expulsée, on appelle `memcached.delete(expulsée)`

**Commande d’exécution (démo simple, sans images) :**
```bash
python -m scripts.main_lru_mem
```

**Vérification des résultats (démo simple) :**
- vérifier que l’ordre LRU évolue correctement (MRU → LRU),
- vérifier que `K2 exists: False` après insertion de `K3` (capacité=2),
- vérifier que `K1 exists: True` et `K3 exists: True`.

**Commande d’exécution (démo avec images) :**
```bash
python -m scripts.main_lru_mem_images
```

**Vérification des résultats (démo images) :**
- vérifier que le script affiche `Eviction OK: K2 absente, K1 et K3 présentes`,
- vérifier que `GET K2` affiche `hit=False`,
- vérifier visuellement les previews générées dans `work/previews_lru_mem/` (ouverture automatique).

### 5.2. Validation (démo simple)
Capacité LRU = 2 :
- insertion `K1`, `K2`
- lecture `K1` → `K1` devient MRU, `K2` devient LRU
- insertion `K3` → éviction de `K2`

Résultat observé :
- `K2 exists: False`
- `K1 exists: True`, `K3 exists: True`  
→ **éviction correcte**

### 5.3. Validation avec images
Même scénario mais avec bytes d’images sous `K1/K2/K3`.  
Résultats :
- éviction confirmée (`K2` absente)
- previews générées pour vérifier la validité des images restantes (`K1` et `K3`)

---

## 6. Conclusion
Ce TP montre trois modes de stockage :
1) **Système de fichiers (FS)** : simple, persistant, mais dépendant des performances disque et du cache OS.  
2) **Memcached** : accès rapide en mémoire, pratique pour cache, mais volatile et soumis à des limites (ex. taille max item).  
3) **Memcached + LRU** : ajout d’un contrôle explicite de la capacité du cache via une politique d’éviction **LRU**, garantissant que seules les données les plus récemment utilisées restent disponibles.

L’ensemble des tests a validé la **non-corruption** des données via SHA256 et la **cohérence fonctionnelle** de l’éviction LRU.
