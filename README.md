# Projet de Traitement de Contenu Web et Génération d'Embeddings
[![Description de l'image](https://raw.githubusercontent.com/M-Lai-ai/logo/refs/heads/main/favicon.ico)](https://votre-lien-cible.com)

### *Pour Jeff dans le cadre de la modification du pipeline CHATBOT OUELLET*
#### *dans le code tu as les 3 processus integres:*
1. Crawling + pdf download
   
   Le **Crawler Web** de ce projet est conçu pour explorer de manière efficace les sites web spécifiés, en extrayant les URLs pertinentes et en téléchargeant les fichiers nécessaires tels que les PDF, images et documents. Il gère les exclusions d'URL basées sur des chemins définis, respecte les limites de profondeur configurables pour éviter de surcharger les serveurs cibles, et implémente des délais entre les requêtes pour minimiser les risques de blocage. Grâce à une gestion robuste des erreurs et des retries, le crawler assure une collecte fiable des données tout en maintenant des performances optimales. De plus, il convertit les liens relatifs en liens absolus, nettoie le contenu HTML en supprimant les éléments non pertinents, et organise les fichiers téléchargés dans des répertoires structurés pour faciliter les étapes ultérieures de traitement et d'analyse.
   
2. PDF extraction with optical caracter recognition + llm Restructuration

   Le **Processeur PDF** de ce projet est conçu pour extraire et structurer efficacement le contenu des fichiers PDF. Il utilise une combinaison d'OCR (Reconnaissance Optique de Caractères) via Tesseract et de la bibliothèque PyPDF pour extraire le texte des documents, même ceux contenant des images ou des formats complexes. Chaque page du PDF est prétraitée pour améliorer la précision de l'OCR en appliquant des techniques de nettoyage et d'amélioration de l'image, telles que la conversion en niveaux de gris, la débruitage et le seuillage adaptatif. Une fois le texte extrait, le contenu est structuré en Markdown à l'aide de l'API GPT-4, permettant une organisation claire et hiérarchisée des informations. Le processeur gère également les erreurs et les exceptions de manière robuste, assurant une extraction fiable même en cas de documents mal formatés ou endommagés. Les résultats sont sauvegardés dans des fichiers `.txt` structurés, facilitant les étapes ultérieures de traitement et d'analyse des données. De plus, le système de journalisation intégré fournit un suivi détaillé des opérations, aidant à identifier et à résoudre rapidement tout problème rencontré lors du traitement des PDF.


3. Contextual embedding processes
   
Le **Processeur d'Embeddings** de ce projet est conçu pour transformer les textes extraits en représentations vectorielles riches et exploitables. Il commence par découper les textes en segments (chunks) de taille configurable avec un chevauchement pour maintenir le contexte entre les segments. Chaque segment est ensuite contextualisé à l'aide de l'API GPT-4, qui enrichit le texte brut avec des informations supplémentaires pertinentes provenant de l'ensemble du document. Cette contextualisation améliore la qualité des embeddings générés en assurant que chaque vecteur capture non seulement le contenu immédiat du segment mais aussi son contexte global. Ensuite, le processeur envoie ces segments enrichis à l'API d'OpenAI pour générer des embeddings à l'aide du modèle spécifié (par exemple, `text-embedding-ada-002`). Les embeddings résultants sont stockés de manière efficace dans des fichiers `.npy` pour une récupération rapide, tandis que les métadonnées associées (telles que le nom du fichier, l'identifiant du chunk, le texte brut, le contexte et le texte complet) sont sauvegardées dans un fichier JSON structuré. Le processeur gère également les erreurs et les limites de taux de l'API en implémentant des pauses entre les requêtes et des mécanismes de retry, assurant ainsi une exécution fluide et fiable. De plus, le système de journalisation intégré permet de suivre les opérations en temps réel et de générer des rapports détaillés sur le traitement des embeddings, facilitant ainsi la maintenance et l'optimisation continue du pipeline.

![GitHub Repo stars](https://img.shields.io/github/stars/M-Lai-ai/Ouellet-pipeline-v01.svg?style=social&label=Stars) ![GitHub issues](https://img.shields.io/github/issues/M-Lai-ai/Ouellet-pipeline-v01.svg)

## Table des Matières
- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Architecture du Projet](#architecture-du-projet)
- [Configuration](#configuration)
- [Installation](#installation)
- [Utilisation](#utilisation)
  - [Modes d'Exécution](#modes-dexécution)
    - [1. Pipeline Complet](#1-pipeline-complet)
    - [2. Crawler Seul](#2-crawler-seul)
    - [3. Processeur PDF Seul](#3-processeur-pdf-seul)
    - [4. Embedding Seul](#4-embedding-seul)
  - [Exécution Programmatique](#exécution-programmatique)
- [Journal des Modifications](#journal-des-modifications)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Description

Ce projet est une suite d'outils Python conçus pour crawler des sites web, extraire et traiter du contenu (y compris les fichiers PDF), et générer des embeddings de texte à l'aide de l'API OpenAI. Il est idéal pour des applications telles que l'indexation de contenu, la recherche sémantique, ou l'analyse de documents.

**Auteur :** M-LAI

## Fonctionnalités

- **Crawler Web** : Explore les sites web, extrait les URLs, télécharge des fichiers (PDF, images, documents), et nettoie le contenu HTML.
- **Extraction de PDF** : Utilise l'OCR et PyPDF pour extraire du texte à partir de fichiers PDF, puis structure le contenu en Markdown à l'aide de GPT-4.
- **Traitement des Embeddings** : Découpe le texte en segments, contextualise chaque chunk avec GPT-4, et génère des embeddings via l'API OpenAI.
- **Configuration Flexible** : Paramètres configurables via un fichier JSON pour adapter le comportement du crawler, les options d'OCR, et les paramètres des embeddings.
- **Journalisation** : Suivi détaillé des opérations avec des logs et génération de rapports.

## Architecture du Projet

Le projet est structuré en trois principaux modules :

1. **WebCrawler** : Responsable de l'exploration et du téléchargement du contenu web.
2. **PDFExtractor** : Gère l'extraction et la structuration du texte à partir des PDF.
3. **EmbeddingProcessor** : Traite les textes extraits pour générer des embeddings.

Chaque module est conçu de manière modulaire, permettant une utilisation indépendante ou intégrée selon les besoins.

## Configuration

La configuration du projet est gérée via un fichier JSON. Voici un exemple de configuration :

```json
{
    "excluded_paths": [
        "selecteur-de-produits",
        "login",
        "cart",
        "search"
    ],
    "downloadable_extensions": {
        "PDF": [".pdf"],
        "Image": [".png", ".jpg", ".jpeg", ".gif", ".svg"],
        "Doc": [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]
    },
    "content_type_mapping": {
        "PDF": {
            "application/pdf": ".pdf"
        },
        "Image": {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/svg+xml": ".svg"
        },
        "Doc": {
            "application/msword": ".doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/vnd.ms-excel": ".xls",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
            "application/vnd.ms-powerpoint": ".ppt",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx"
        }
    },
    "retry_config": {
        "total": 5,
        "backoff_factor": 1,
        "status_forcelist": [429, 500, 502, 503, 504]
    },
    "crawler_options": {
        "max_depth": 1,
        "delay_between_requests": 1,
        "timeout": 30,
        "verify_ssl": false
    },
    "pdf_options": {
        "ocr_enabled": true,
        "ocr_language": "fra+eng",
        "chunk_size": 5000,
        "overlap_size": 500
    },
    "embedding_options": {
        "chunk_size": 400,
        "overlap_size": 100,
        "batch_size": 50,
        "model": "text-embedding-ada-002"
    }
}
```

### Explications des Paramètres

- **excluded_paths** : Segments d'URL à exclure lors du crawling.
- **downloadable_extensions** : Types de fichiers à télécharger, classés par catégorie.
- **content_type_mapping** : Mappage des types de contenu HTTP aux extensions de fichiers.
- **retry_config** : Configuration des retries pour les requêtes HTTP.
- **crawler_options** : Options de configuration pour le crawler web (profondeur maximale, délai entre les requêtes, etc.).
- **pdf_options** : Options spécifiques pour l'extraction de PDF (activation de l'OCR, langues, tailles de chunks).
- **embedding_options** : Paramètres pour le traitement des embeddings (taille des chunks, modèle à utiliser, etc.).

## Installation

### Prérequis

- Python 3.7 ou supérieur
- pip

### Étapes d'Installation

1. **Cloner le Répertoire**
    ```bash
    git clone https://github.com/M-Lai-ai/Ouellet-pipeline-v01.git
    cd Ouellet-pipeline-v01
    ```

2. **Créer un Environnement Virtuel**
    ```bash
    python -m venv env
    source env/bin/activate  # Sur Windows : env\Scripts\activate
    ```

3. **Installer les Dépendances**
    ```bash
    pip install -r requirements.txt
    ```

    *Contenu possible de `requirements.txt`* :
    ```
    requests
    beautifulsoup4
    numpy
    pytesseract
    pdf2image
    opencv-python
    Pillow
    pypdf
    html2text
    ```

4. **Installer Tesseract OCR**

    - **Windows** : Téléchargez l'installateur depuis [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) et suivez les instructions.
    - **macOS** :
        ```bash
        brew install tesseract
        ```
    - **Linux** :
        ```bash
        sudo apt-get install tesseract-ocr
        sudo apt-get install libtesseract-dev
        ```

## Utilisation

### Modes d'Exécution

Le pipeline peut être utilisé de différentes manières, soit en exécutant l'ensemble du pipeline, soit en exécutant des composants individuellement. Voici comment procéder :

#### 1. Pipeline Complet

Exécute tous les modules dans l'ordre : crawler web, extraction de PDF, puis génération d'embeddings.

```bash
python main.py pipeline --start-url "https://www.example.com" --openai-key "your-key" --max-depth 3
```

#### 2. Crawler Seul

Exécute uniquement le crawler web pour explorer les sites et télécharger les fichiers pertinents.

```bash
python main.py crawler --start-url "https://www.example.com" --max-depth 3
```

#### 3. Processeur PDF Seul

Exécute uniquement l'extracteur de PDF pour traiter les fichiers PDF téléchargés.

```bash
python main.py pdf --input-dir "pdfs" --output-dir "output" --openai-key "your-key"
```

#### 4. Embedding Seul

Exécute uniquement le processeur d'embeddings pour générer des embeddings à partir des textes extraits.

```bash
python main.py embedding --input-dir "texts" --output-dir "embeddings" --openai-key "your-key"
```

### Avantages de cette Structure

1. **Exécution Modulaire de Chaque Composant** : Permet d'exécuter ou de développer indépendamment chaque partie du pipeline.
2. **Exécution du Pipeline Complet** : Facilite le traitement de bout en bout sans avoir à exécuter chaque module manuellement.
3. **Configuration via Fichier JSON** : Centralise les paramètres de configuration, facilitant les ajustements et la maintenance.
4. **Logging Détaillé** : Assure un suivi précis des opérations avec des logs et des rapports.
5. **Gestion des Erreurs** : Implémente des mécanismes de retry et de gestion des exceptions pour une robustesse accrue.
6. **Personnalisation des Chemins d'Entrée/Sortie** : Permet de spécifier facilement où les données sont lues et écrites.
7. **Utilisation en Tant que Module Python** : Offre la flexibilité d'intégrer les composants dans d'autres scripts ou applications Python.

### Exécution Programmatique

Vous pouvez également utiliser les composants du pipeline directement dans vos propres scripts Python en important le module `Pipeline`. Voici un exemple :

```python
from pipeline import Pipeline

# Créer une instance du pipeline avec des options personnalisées
pipeline = Pipeline(options={'output_dir': 'custom_output'})

# Exécuter des composants individuellement
crawler_output = pipeline.run_crawler(custom_start_url="https://example.com")
pdf_output = pipeline.run_pdf_processor(input_dir="pdfs", output_dir="texts")
embedding_output = pipeline.run_embedding(input_dir="texts", output_dir="embeddings")
```

**Explications :**

- **Création d'une Instance du Pipeline** : Vous pouvez initialiser le pipeline avec des options spécifiques, telles que des chemins d'entrée/sortie personnalisés.
- **Exécution des Composants Individuellement** : Permet de contrôler finement le flux de travail en exécutant uniquement les parties nécessaires selon le contexte de votre application.

## Journal des Modifications

### Version 1.0.0
- Initialisation du projet avec les trois modules principaux : WebCrawler, PDFExtractor, EmbeddingProcessor.
- Ajout de la configuration JSON pour une personnalisation flexible.
- Mise en place des systèmes de logging et génération de rapports.
- Ajout des modes d'exécution en ligne de commande et programmatique.

## Contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. **Fork le Projet**
2. **Créer une Branche de Feature**
    ```bash
    git checkout -b feature/nom-de-la-feature
    ```
3. **Commit vos Changements**
    ```bash
    git commit -m "Description de la feature"
    ```
4. **Push sur la Branche**
    ```bash
    git push origin feature/nom-de-la-feature
    ```
5. **Ouvrir une Pull Request**

Veuillez vous assurer que votre code respecte les standards de codage et passe les tests existants.

## Licence

Ce projet est sous licence [MIT](LICENSE).

---

*Pour toute question ou suggestion, veuillez ouvrir une [issue](https://github.com/M-Lai-ai/Ouellet-pipeline-v01/issues) sur le dépôt GitHub.*

## Ressources

- [Répertoire GitHub](https://github.com/M-Lai-ai/Ouellet-pipeline-v01.git)
- **Auteur :** M-LAI
