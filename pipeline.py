import os
from datetime import datetime
from crawler import WebCrawler
from pdf_extractor import PDFExtractor
from embedding_processor import EmbeddingProcessor
import logging


class Pipeline:
    def __init__(self, start_url, openai_api_key, options=None):
        self.start_url = start_url
        self.openai_api_key = openai_api_key
        self.options = options or {}

        # Création du dossier principal avec timestamp
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = os.path.join(
            self.options.get('output_dir', 'pipeline_output'),
            f"run_{self.timestamp}"
        )

        # Création des sous-dossiers
        self.create_directories()

        # Configuration du logging
        self.setup_logging()

    def create_directories(self):
        """Crée la structure de dossiers nécessaire"""
        self.dirs = {
            'crawler': os.path.join(self.base_dir, 'crawler_output'),
            'pdf_processed': os.path.join(self.base_dir, 'pdf_processed'),
            'embeddings': os.path.join(self.base_dir, 'embeddings'),
            'logs': os.path.join(self.base_dir, 'logs')
        }

        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    def setup_logging(self):
        """Configure le système de logging"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(os.path.join(self.dirs['logs'], 'pipeline.log')),
                logging.StreamHandler()
            ]
        )

    def run(self, skip_crawling=False, skip_pdf=False, skip_embedding=False):
        """Exécute le pipeline complet avec options pour sauter des étapes"""
        try:
            crawler_pdf_dir = None
            crawler_content_dir = None

            # Étape 1: Crawling
            if not skip_crawling:
                logging.info("Démarrage du crawling...")
                crawler = WebCrawler(
                    start_url=self.start_url,
                    max_depth=self.options.get('max_depth', 2)
                )
                crawler.crawl()

                # Récupération du dossier de sortie du crawler
                crawler_pdf_dir = os.path.join(crawler.base_dir, 'PDF')
                crawler_content_dir = os.path.join(crawler.base_dir, 'content')
            else:
                logging.info("Étape de crawling sautée.")
                crawler_pdf_dir = os.path.join(self.dirs['crawler'], 'PDF')
                crawler_content_dir = os.path.join(self.dirs['crawler'], 'content')

            # Étape 2: Traitement des PDFs
            if not skip_pdf and crawler_pdf_dir and os.path.exists(crawler_pdf_dir):
                logging.info("Démarrage du traitement des PDFs...")
                pdf_extractor = PDFExtractor(
                    input_dir=crawler_pdf_dir,
                    output_dir=crawler_content_dir,
                    openai_api_key=self.openai_api_key
                )
                pdf_extractor.process_all_pdfs()
            else:
                logging.info("Étape de traitement PDF sautée ou aucun PDF trouvé.")

            # Étape 3: Création des embeddings
            if not skip_embedding and crawler_content_dir and os.path.exists(crawler_content_dir):
                logging.info("Démarrage de la création des embeddings...")
                embedding_processor = EmbeddingProcessor(
                    input_dir=crawler_content_dir,
                    output_dir=self.dirs['embeddings'],
                    openai_api_key=self.openai_api_key
                )
                embedding_processor.process_all_files()
            else:
                logging.info("Étape de création d'embeddings sautée ou aucun contenu trouvé.")

            logging.info("Pipeline terminé avec succès!")

        except Exception as e:
            logging.error(f"Erreur dans le pipeline: {str(e)}")
            raise


if __name__ == "__main__":
    # Configuration pour test direct
    start_url = "https://www.ouellet.com/fr-ca/"
    openai_api_key = "votre-cle-api"
    options = {
        'max_depth': 2,
        'output_dir': 'pipeline_output'
    }

    # Création et exécution du pipeline
    pipeline = Pipeline(start_url, openai_api_key, options)
    pipeline.run()
