# Web Redirection Scanner

## Description

Ce script Python permet de scanner un site web pour détecter des **redirections ouvertes**, qui peuvent potentiellement être exploitées dans des attaques de **phishing**. Le script explore automatiquement les pages d'un site, analyse les liens internes et détecte les redirections qui pointent vers un site malveillant.

Le script est conçu pour tester les redirections dans les URL, dans le JavaScript, ainsi que pour analyser les formulaires de soumission de pages. Il utilise une approche de **crawl** pour explorer tout le site et vérifier les redirections dans les liens.

---

## Fonctionnalités

- **Crawl automatique des pages** : Le script explore toutes les pages du site à partir de l'URL de départ.
- **Analyse des redirections** : Recherche et teste des redirections dans les liens, le JavaScript et les formulaires.
- **Gestion des erreurs** : Le script gère les erreurs HTTP, notamment les erreurs **429** (trop de requêtes), en réessayant après un délai.
- **Paramètres personnalisables** : Vous pouvez configurer l'URL cible et les paramètres de redirection malveillants.

---

## Prérequis

Assurez-vous d'avoir **Python 3.x** installé, ainsi que les bibliothèques nécessaires. Vous pouvez installer les dépendances via `pip` :

```bash
pip install requests beautifulsoup4
```

---

## Utilisation

1. Clonez ce repository sur votre ordinateur :

```bash
git clone https://github.com/SnufkinWanderer/Web-Redirection-Scanner.git
cd Web-Redirection-Scanner
```

2. Modifiez les variables dans le script pour spécifier l'URL cible à scanner (par défaut, c'est https://www.ovh.com).
3. Exécutez le script pour lancer le scan :
   
```bash
python scan.py
```

Le script explorera automatiquement le site et affichera les redirections ouvertes détectées.

---

## Configuration

Les principales variables de configuration sont les suivantes :

- TARGET_DOMAIN : L'URL du site à scanner. Par défaut, c'est https://www.ovh.com.
- EXTERNAL_URL : L'URL malveillante vers laquelle les redirections doivent pointer pour être considérées comme des redirections ouvertes.
- REDIRECT_PARAMS : Liste des paramètres d'URL souvent utilisés pour la redirection. Vous pouvez ajouter ou supprimer des paramètres selon vos besoins.

---

## Exemple d'Exécution

```bash
🔍 Scan complet du site https://www.ovh.com pour détecter les redirections ouvertes...

Scanning https://www.ovh.com
[⚠️ VULNÉRABLE] https://www.ovh.com/path?url=https://evil.com redirige vers https://evil.com
[✔️ SÛR] https://www.ovh.com/path?next=https://evil.com
...
```

---

## Gestion des erreurs

Le script gère automatiquement les erreurs courantes comme les erreurs de réseau et les erreurs de type 429 (trop de requêtes). En cas d'erreur, le script attend un délai avant de réessayer, pour ne pas surcharger le serveur.

---

## Contributions

Si vous souhaitez contribuer à ce projet, n'hésitez pas à ouvrir une pull request. Toute amélioration ou suggestion est la bienvenue.
