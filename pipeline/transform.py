import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
import faiss

from config import PROCESSED_DIR, SPACY_MODEL, BERT_MODEL
from logger import setup_logger

# Setup logging
logger = setup_logger("transform")

# Load models
try:
    nlp = spacy.load(SPACY_MODEL)
    model = SentenceTransformer(BERT_MODEL)
    logger.info(f"Loaded models: SpaCy ({SPACY_MODEL}), BERT ({BERT_MODEL})")
except Exception as e:
    logger.error(f"Failed to load models: {e}")
    raise

class DataTransformer:
    """Transform and process extracted data."""
    
    def __init__(self):
        """Initialize the transformer."""
        self.nlp = nlp
        self.model = model
        
    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text with NLP and generate embeddings."""
        try:
            # Process with SpaCy
            doc = self.nlp(text)
            
            # Extract key information
            processed_data = {
                'sentences': [sent.text.strip() for sent in doc.sents],
                'entities': [{'text': ent.text, 'label': ent.label_} for ent in doc.ents],
                'keywords': [token.text for token in doc if token.is_alpha and not token.is_stop]
            }
            
            # Generate embeddings
            embeddings = self.model.encode(processed_data['sentences'])
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(np.array(embeddings).astype('float32'))
            
            return processed_data, embeddings, index
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            raise
            
    def process_charts(self, charts: List[Dict]) -> List[Dict]:
        """Process and analyze chart data."""
        try:
            processed_charts = []
            for chart in charts:
                if chart.get('contains_chart'):
                    processed_charts.append({
                        'image_path': chart['image_path'],
                        'confidence': chart['confidence'],
                        'type': 'chart',
                        'characteristics': chart['characteristics']
                    })
            return processed_charts
            
        except Exception as e:
            logger.error(f"Error processing charts: {e}")
            raise

def main():
    """Main execution function."""
    try:
        # Load extracted data
        with open(PROCESSED_DIR / "extracted_text.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        transformer = DataTransformer()
        
        # Process text and generate embeddings
        processed_text, embeddings, vector_index = transformer.process_text(data['text'])
        
        # Process charts
        processed_charts = transformer.process_charts(data.get('charts', []))
        
        # Save processed results
        output = {
            'text_analysis': processed_text,
            'charts': processed_charts
        }
        
        with open(PROCESSED_DIR / "processed_data.json", 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        logger.info("Data transformation complete!")
        
    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        raise

if __name__ == "__main__":
    main()