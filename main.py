import argparse
import logging
import json
import os
from pipeline import Pipeline

def load_config(config_path):
    """Charge la configuration depuis un fichier JSON"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def main():
    parser = argparse.ArgumentParser(description='Pipeline de traitement de données')
    
    # Arguments généraux
    parser.add_argument('--config', default='config.json', help='Chemin du fichier de configuration')
    parser.add_argument('--output-dir', default='pipeline_output', help='Dossier de sortie')
    parser.add_argument('--debug', action='store_true', help='Active le mode debug')
    
    # Sous-parsers pour les différentes commandes
    subparsers = parser.add_subparsers(dest='command', help='Commande à exécuter')
    
    # Parser pour le pipeline complet
    pipeline_parser = subparsers.add_parser('pipeline', help='Exécute le pipeline complet')
    pipeline_parser.add_argument('--start-url', required=True, help='URL de départ')
    pipeline_parser.add_argument('--openai-key', required=True, help='Clé API OpenAI')
    pipeline_parser.add_argument('--max-depth', type=int, default=2, help='Profondeur max du crawling')
    pipeline_parser.add_argument('--skip-crawling', action='store_true')
    pipeline_parser.add_argument('--skip-pdf', action='store_true')
    pipeline_parser.add_argument('--skip-embedding', action='store_true')
    
    # Parser pour le crawler seul
    crawler_parser = subparsers.add_parser('crawl', help='Exécute uniquement le crawler')
    crawler_parser.add_argument('--start-url', required=True, help='URL de départ')
    crawler_parser.add_argument('--max-depth', type=int, default=2)
    
    # Parser pour le traitement PDF seul
    pdf_parser = subparsers.add_parser('pdf', help='Exécute uniquement le traitement PDF')
    pdf_parser.add_argument('--input-dir', required=True, help='Dossier contenant les PDFs')
    pdf_parser.add_argument('--output-dir', required=True, help='Dossier de sortie')
    pdf_parser.add_argument('--openai-key', required=True, help='Clé API OpenAI')
    
    # Parser pour l'embedding seul
    embedding_parser = subparsers.add_parser('embed', help='Exécute uniquement la création d\'embeddings')
    embedding_parser.add_argument('--input-dir', required=True, help='Dossier contenant les fichiers texte')
    embedding_parser.add_argument('--output-dir', required=True, help='Dossier de sortie')
    embedding_parser.add_argument('--openai-key', required=True, help='Clé API OpenAI')
    
    args = parser.parse_args()
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Chargement de la configuration
    config = load_config(args.config)
    
    try:
        if args.command == 'pipeline':
            # Exécution du pipeline complet
            pipeline = Pipeline(
                start_url=args.start_url,
                openai_api_key=args.openai_key,
                options={
                    'max_depth': args.max_depth,
                    'output_dir': args.output_dir,
                    **config
                }
            )
            pipeline.run(
                skip_crawling=args.skip_crawling,
                skip_pdf=args.skip_pdf,
                skip_embedding=args.skip_embedding
            )
            
        elif args.command == 'crawl':
            # Exécution du crawler seul
            pipeline = Pipeline(options={'output_dir': args.output_dir, **config})
            pipeline.run_crawler(custom_start_url=args.start_url)
            
        elif args.command == 'pdf':
            # Exécution du traitement PDF seul
            pipeline = Pipeline(
                openai_api_key=args.openai_key,
                options={'output_dir': args.output_dir, **config}
            )
            pipeline.run_pdf_processor(
                input_dir=args.input_dir,
                output_dir=args.output_dir
            )
            
        elif args.command == 'embed':
            # Exécution de l'embedding seul
            pipeline = Pipeline(
                openai_api_key=args.openai_key,
                options={'output_dir': args.output_dir, **config}
            )
            pipeline.run_embedding(
                input_dir=args.input_dir,
                output_dir=args.output_dir
            )
            
        else:
            parser.print_help()
            
    except Exception as e:
        logging.error(f"Erreur: {str(e)}")
        raise

if __name__ == "__main__":
    main()
