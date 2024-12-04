import os
from pathlib import Path
import logging
import pytesseract
from pdf2image import convert_from_path
import numpy as np
import cv2
from PIL import Image
import pypdf
import requests
import time

class PDFExtractor:
    def __init__(self, input_dir, output_dir, openai_api_key):
        # Configuration des chemins
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration OpenAI
        self.openai_api_key = openai_api_key
        self.headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # Dossier temporaire
        self.temp_dir = Path("temp_images")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pdf_extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def preprocess_image(self, image):
        """Prétraitement de l'image pour OCR"""
        if isinstance(image, Image.Image):
            image = np.array(image)

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        denoised = cv2.fastNlMeansDenoising(gray)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return binary

    def extract_text_with_ocr(self, pdf_path):
        """Extraction texte par OCR"""
        try:
            images = convert_from_path(pdf_path)
            ocr_texts = []

            for i, image in enumerate(images, 1):
                self.logger.info(f"OCR page {i}/{len(images)}")
                
                temp_path = self.temp_dir / f"temp_{i}.png"
                image.save(temp_path)
                
                img = cv2.imread(str(temp_path))
                processed_img = self.preprocess_image(img)
                
                text = pytesseract.image_to_string(
                    processed_img,
                    lang='fra+eng',
                    config='--psm 1'
                )
                
                if len(text.strip()) < 100:
                    text = pytesseract.image_to_string(
                        processed_img,
                        lang='fra+eng',
                        config='--psm 3 --oem 1'
                    )
                
                ocr_texts.append(text)
                temp_path.unlink(missing_ok=True)

            return ocr_texts
        except Exception as e:
            self.logger.error(f"Erreur OCR: {str(e)}")
            return None

    def extract_text_with_pypdf(self, pdf_path):
        """Extraction texte avec PyPDF"""
        try:
            text_content = []
            with open(pdf_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text() or ''
                    text_content.append(text)
            return text_content
        except Exception as e:
            self.logger.error(f"Erreur PyPDF: {str(e)}")
            return None

    def process_with_gpt(self, content):
        """Traitement du contenu avec GPT-4 pour structurer le texte en Markdown"""
        system_prompt = {
            "role": "system",
            "content": (
                "You are an expert analyst for Ouellet Canada. "
                "Analyze the following content and structure it using this exact format:\n\n"
                "# [Product Category/Line Name]\n"
                "- Description: [general product description]\n"
                "- Application: [product application]\n"
                "- General Features: [list of general features]\n\n"
                "## Product Specifications\n"
                "# [Model Number]\n"
                "- price: [value in CAD]\n"
                "- length: [value in ft]\n"
                "- watts: [value]\n"
                "- [other specifications]: [value]\n\n"
                "## Installation Instructions\n"
                "- [installation instruction 1]\n"
                "- [installation instruction 2]\n\n"
                "## Warranty\n"
                "- [warranty details]\n\n"
                "Example:\n"
                "# Câble chauffant à résistance fixe\n"
                "- Description: Câble chauffant pour déglaçage\n"
                "- Application: Déglaçage de toitures et gouttières\n"
                "- General Features:\n"
                "  - Surgaine PVC\n"
                "  - Conducteur en cuivre nickelé\n\n"
                "## Product Specifications\n"
                "# ORF-R020\n"
                "- price: 63.00\n"
                "- length: 20\n"
                "- watts: 150\n"
                "- voltage: 120V\n\n"
                "## Installation Instructions\n"
                "- Ne jamais couper le câble\n"
                "- Pour applications extérieures seulement\n\n"
                "## Warranty\n"
                "- Garantie de base de 1 an\n\n"
                "Extract and structure ALL information from the content. Dont skip anything "
                "Maintain the exact hierarchy and formatting. "
                "Include all general information, specifications, and additional details. "
                "Use bullet points for lists. "
                "Separate sections with blank lines."
            )
        }

        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    system_prompt,
                    {"role": "user", "content": content}
                ],
                "temperature": 0,
                "max_tokens": 5000,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            processed_content = response.json()['choices'][0]['message']['content']
            
            time.sleep(1)
            
            return processed_content
        except Exception as e:
            self.logger.error(f"Erreur GPT: {str(e)}")
            return None

    def process_pdf(self, pdf_path):
        """Traitement complet d'un PDF"""
        document_name = pdf_path.stem
        
        self.logger.info(f"Traitement de {pdf_path}")
        
        # Extraction de texte (OCR + PyPDF)
        ocr_texts = self.extract_text_with_ocr(pdf_path) or []
        pypdf_texts = self.extract_text_with_pypdf(pdf_path) or []
        
        # Déterminer le nombre de pages
        num_pages = max(len(ocr_texts), len(pypdf_texts))
        
        # Pour chaque page, combiner OCR et PyPDF
        for page_num in range(num_pages):
            self.logger.info(f"Traitement de la page {page_num + 1}")
            
            # Combiner les textes des deux méthodes
            page_text = ""
            if page_num < len(ocr_texts):
                page_text += ocr_texts[page_num] + "\n\n"
            if page_num < len(pypdf_texts):
                page_text += pypdf_texts[page_num]
            
            # Traiter le texte avec GPT
            processed_content = self.process_with_gpt(page_text)
            
            if processed_content:
                # Sauvegarder le résultat
                output_file_name = self.output_dir / f"{document_name}_page_{page_num + 1}.txt"
                try:
                    with open(output_file_name, 'w', encoding='utf-8') as f:
                        f.write(f"Document ID: {document_name}\n\n{processed_content}")
                    self.logger.info(f"Fichier créé: {output_file_name}")
                except Exception as e:
                    self.logger.error(f"Erreur sauvegarde page {page_num + 1}: {str(e)}")
        
        return True

    def process_all_pdfs(self):
        """Traitement de tous les PDF"""
        pdf_files = list(self.input_dir.glob('*.pdf'))
        total_files = len(pdf_files)
        
        self.logger.info(f"Début traitement de {total_files} fichiers")
        
        successful = 0
        for i, pdf_path in enumerate(pdf_files, 1):
            self.logger.info(f"Fichier {i}/{total_files}: {pdf_path.name}")
            if self.process_pdf(pdf_path):
                successful += 1
            
            time.sleep(2)
        
        self.logger.info(f"Terminé. {successful}/{total_files} fichiers traités")

def main():
    # Configuration
    input_directory = "input"
    output_directory = "output"
    openai_api_key = "votre-cle-api"
    
    try:
        extractor = PDFExtractor(input_directory, output_directory, openai_api_key)
        extractor.process_all_pdfs()
        
    except Exception as e:
        logging.error(f"Erreur principale: {str(e)}")
        raise

if __name__ == "__main__":
    main()
