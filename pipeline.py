import os
from datetime import datetime
from crawler import WebCrawler
from pdf_extractor import PDFExtractor
from embedding_processor import EmbeddingProcessor
import logging
from pathlib import Path

class Pipeline:
    def __init__(self, start_url=None, openai_api_key=None, options=None):
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
        log_file = os.path.join(self.dirs['logs'], f'pipeline_{self.timestamp}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def run_crawler(self, custom_start_url=None):
        """Exécute uniquement le crawler"""
        logging.info("Démarrage du crawling...")
        crawler = WebCrawler(
            start_url=custom_start_url or self.start_url,
            max_depth=self.options.get('max_depth', 2)
        )
        crawler.crawl()
        return crawler.base_dir
        
    def run_pdf_processor(self, input_dir=None, output_dir=None):
        """Exécute uniquement le traitement PDF"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for PDF processing")
            
        logging.info("Démarrage du traitement des PDFs...")
        pdf_extractor = PDFExtractor(
            input_dir=input_dir or os.path.join(self.dirs['crawler'], 'PDF'),
            output_dir=output_dir or os.path.join(self.dirs['crawler'], 'content'),
            openai_api_key=self.openai_api_key
        )
        pdf_extractor.process_all_pdfs()
        return pdf_extractor.output_dir
        
    def run_embedding(self, input_dir=None, output_dir=None):
        """Exécute uniquement la création d'embeddings"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for embedding creation")
            
        logging.info("Démarrage de la création des embeddings...")
        embedding_processor = EmbeddingProcessor(
            input_dir=input_dir or os.path.join(self.dirs['crawler'], 'content'),
            output_dir=output_dir or self.dirs['embeddings'],
            openai_api_key=self.openai_api_key
        )
        embedding_processor.process_all_files()
        return embedding_processor.output_dir
        
    def run(self, skip_crawling=False, skip_pdf=False, skip_embedding=False):
        """Exécute le pipeline complet"""
        try:
            crawler_output_dir = None
            pdf_output_dir = None
            
            # Étape 1: Crawling
            if not skip_crawling:
                crawler_output_dir = self.run_crawler()
            
            # Étape 2: Traitement des PDFs
            if not skip_pdf:
                pdf_output_dir = self.run_pdf_processor(
                    input_dir=os.path.join(crawler_output_dir, 'PDF') if crawler_output_dir else None
                )
            
            # Étape 3: Création des embeddings
            if not skip_embedding:
                self.run_embedding(
                    input_dir=pdf_output_dir if pdf_output_dir else None
                )
            
            logging.info("Pipeline terminé avec succès!")
            
        except Exception as e:
            logging.error(f"Erreur dans le pipeline: {str(e)}")
            raise
