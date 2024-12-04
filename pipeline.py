import os
import json
import numpy as np
import requests
from pathlib import Path
import logging
import time

class EmbeddingProcessor:
    def __init__(self, input_dir, output_dir, openai_api_key):
        # Configuration des chemins
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialisation des listes globales pour tous les fichiers
        self.all_embeddings = []
        self.all_metadata = []

        # Configuration OpenAI
        self.openai_api_key = openai_api_key
        self.headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }

        # Configuration logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('embedding_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def chunk_text(self, text, chunk_size=400, overlap_size=100):
        """Découpe le texte en chunks avec un chevauchement."""
        tokens = text.split(' ')
        chunks = []
        for i in range(0, len(tokens), chunk_size - overlap_size):
            chunk = ' '.join(tokens[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def get_contextualized_chunk(self, chunk, full_text):
        """Demande à GPT-4o-mini de contextualiser chaque chunk."""
        system_prompt = {
            "role": "system",
            "content": (
                "You are an expert analyst. The following is an excerpt from a larger document. "
                "Your task is to provide context to the following section by referencing the content of the entire document. "
                "Ensure that the context helps understand the chunk more thoroughly."
            )
        }
        user_prompt = {
            "role": "user",
            "content": f"Document: {full_text}\n\nChunk: {chunk}\n\nPlease provide context for this chunk."
        }
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [system_prompt, user_prompt],
                "temperature": 0.7,
                "max_tokens": 16000,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            context = response.json()['choices'][0]['message']['content']
            return context
        except Exception as e:
            self.logger.error(f"Erreur lors de la contextualisation du chunk: {str(e)}")
            return None

    def get_embedding(self, text):
        """Obtenir l'embedding pour un texte."""
        try:
            payload = {
                "input": text,
                "model": "text-embedding-ada-002",
                "encoding_format": "float"
            }

            response = requests.post(
                'https://api.openai.com/v1/embeddings',
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            embedding = response.json()['data'][0]['embedding']
            return embedding
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de l'embedding: {str(e)}")
            return None

    def process_file(self, txt_file_path):
        """Processus pour un fichier texte."""
        self.logger.info(f"Traitement du fichier: {txt_file_path}")

        # Lecture du fichier texte
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            full_text = file.read()

        # Découpe du texte en chunks
        chunks = self.chunk_text(full_text)

        # Traitement de chaque chunk
        for i, text_raw in enumerate(chunks):
            # Contextualiser chaque chunk
            context = self.get_contextualized_chunk(text_raw, full_text)
            if context:
                # Créer le texte complet (text_raw + context)
                text = f"{context}\n\nContext:\n{text_raw}"

                # Récupérer l'embedding pour le texte complet
                embedding = self.get_embedding(text)
                if embedding:
                    self.all_embeddings.append(embedding)
                    self.all_metadata.append({
                        "filename": txt_file_path.name,
                        "chunk_id": i,
                        "text_raw": text_raw,
                        "context": context,
                        "text": text
                    })

            # Pause pour éviter les limites de taux de l'API
            time.sleep(1)

    def process_all_files(self):
        """Processus pour tous les fichiers dans le dossier d'entrée."""
        txt_files = list(self.input_dir.glob('*.txt'))
        total_files = len(txt_files)

        self.logger.info(f"Début du traitement de {total_files} fichiers")

        for i, txt_file_path in enumerate(txt_files, 1):
            self.logger.info(f"Traitement du fichier {i}/{total_files}: {txt_file_path.name}")
            self.process_file(txt_file_path)

        # Sauvegarde de tous les résultats à la fin
        if self.all_embeddings:
            # Sauvegarde du fichier JSON unique
            chunks_json_path = self.output_dir / "chunks.json"
            with open(chunks_json_path, 'w', encoding='utf-8') as json_file:
                json.dump({
                    "metadata": self.all_metadata
                }, json_file, ensure_ascii=False, indent=4)
            self.logger.info(f"Fichier JSON créé: {chunks_json_path}")

            # Sauvegarde du fichier .npy unique
            embeddings_npy_path = self.output_dir / "embeddings.npy"
            np.save(embeddings_npy_path, np.array(self.all_embeddings))
            self.logger.info(f"Fichier NPY créé: {embeddings_npy_path}")

        self.logger.info("Traitement terminé")

def main():
    # Configuration
    input_directory = "input"
    output_directory = "output"
    openai_api_key = "votre-cle-api"

    try:
        # Création du processeur
        processor = EmbeddingProcessor(input_directory, output_directory, openai_api_key)

        # Traitement des fichiers
        processor.process_all_files()

    except Exception as e:
        logging.error(f"Erreur principale: {str(e)}")
        raise

if __name__ == "__main__":
    main()
