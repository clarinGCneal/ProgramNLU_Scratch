"""
Natural Language Understanding System
Main orchestrator for NLU pipeline
"""

import logging
from typing import Dict, List, Optional, Any
from core.database import DatabaseManager
from modules.segmentation import Segmenter
from modules.morphology import MorphologyAnalyzer
from config import DB_CONFIG, LOGGING_CONFIG

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file']),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class NLUSystem:
    """
    Main NLU System orchestrator
    Coordinates all NLU modules for complete text understanding
    """
    
    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """
        Initialize NLU System
        
        Args:
            db_config: Database configuration dictionary
        """
        logger.info("Initializing NLU System...")
        
        # Initialize database manager
        config = db_config or DB_CONFIG
        self.db_manager = DatabaseManager(**config)
        
        if not self.db_manager.connect():
            raise ConnectionError("Failed to connect to database")
        
        # Initialize modules
        self.segmenter = Segmenter(db_manager=self.db_manager)
        self.morphology = MorphologyAnalyzer(db_manager=self.db_manager)
        
        logger.info("NLU System initialized successfully")
    
    def initialize_database(self, schema_file: str = 'database/schema.sql'):
        """
        Initialize database with schema
        
        Args:
            schema_file: Path to SQL schema file
        """
        logger.info("Initializing database schema...")
        self.db_manager.initialize_database(schema_file)
        logger.info("Database initialized")
    
    def process_text(self, text: str, analyze_morphology: bool = True, 
                    store_results: bool = True) -> Dict[str, Any]:
        """
        Complete text processing pipeline
        
        Args:
            text: Input text
            analyze_morphology: Whether to perform morphological analysis
            store_results: Whether to store results in database
        
        Returns:
            Complete processing results
        """
        logger.info(f"Processing text: {text[:50]}...")
        
        # Step 1: Segmentation
        segmentation_results = self.segmenter.process_text(text, store_in_db=store_results)
        
        # Step 2: Morphological Analysis (if requested)
        morphology_results = []
        if analyze_morphology:
            # Collect all words from all sentences
            all_words = []
            for sentence in segmentation_results['sentences']:
                all_words.extend(sentence['words'])
            
            # Analyze unique words
            unique_words = list(set(all_words))
            morphology_results = self.morphology.analyze_batch(
                unique_words, 
                store_in_db=store_results
            )
        
        # Compile complete results
        results = {
            'text': text,
            'segmentation': segmentation_results,
            'morphology': morphology_results,
            'statistics': self._compile_statistics(segmentation_results, morphology_results)
        }
        
        logger.info("Text processing completed")
        return results
    
    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        """
        Analyze a single sentence
        
        Args:
            sentence: Input sentence
        
        Returns:
            Sentence analysis
        """
        # Tokenize
        tokens = self.segmenter.tokenize(sentence)
        
        # Extract words
        words = [t['text'] for t in tokens if not t['is_punctuation']]
        
        # Morphological analysis
        morphology = self.morphology.analyze_batch(words, store_in_db=False)
        
        return {
            'sentence': sentence,
            'tokens': tokens,
            'word_count': len(words),
            'morphology': morphology
        }
    
    def analyze_word(self, word: str) -> Dict[str, Any]:
        """
        Detailed analysis of a single word
        
        Args:
            word: Input word
        
        Returns:
            Word analysis
        """
        return self.morphology.analyze_word(word)
    
    def lemmatize_text(self, text: str) -> str:
        """
        Lemmatize all words in text
        
        Args:
            text: Input text
        
        Returns:
            Lemmatized text
        """
        # Segment into words
        words = self.segmenter.segment_words(text)
        
        # Lemmatize each word
        lemmas = [self.morphology.lemmatize(word) for word in words]
        
        return ' '.join(lemmas)
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics about text
        
        Args:
            text: Input text
        
        Returns:
            Statistics dictionary
        """
        results = self.process_text(text, analyze_morphology=True, store_results=False)
        return results['statistics']
    
    def _compile_statistics(self, segmentation: Dict[str, Any], 
                           morphology: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compile comprehensive statistics
        
        Args:
            segmentation: Segmentation results
            morphology: Morphology results
        
        Returns:
            Statistics dictionary
        """
        stats = self.segmenter.get_statistics(segmentation)
        
        if morphology:
            # Morphology statistics
            total_morphemes = sum(len(m['morphemes']) for m in morphology)
            words_with_prefix = sum(1 for m in morphology if m['prefix'])
            words_with_suffix = sum(1 for m in morphology if m['suffix'])
            
            stats.update({
                'analyzed_words': len(morphology),
                'total_morphemes': total_morphemes,
                'avg_morphemes_per_word': round(total_morphemes / len(morphology), 2) if morphology else 0,
                'words_with_prefix': words_with_prefix,
                'words_with_suffix': words_with_suffix,
                'prefix_percentage': round(words_with_prefix / len(morphology) * 100, 2) if morphology else 0,
                'suffix_percentage': round(words_with_suffix / len(morphology) * 100, 2) if morphology else 0
            })
        
        return stats
    
    def add_morpheme(self, morpheme: str, morpheme_type: str, meaning: str, language: str = 'en'):
        """
        Add a new morpheme to the database
        
        Args:
            morpheme: The morpheme text
            morpheme_type: Type (root, prefix, suffix, infix)
            meaning: Meaning/definition
            language: Language code (default 'en')
        """
        data = {
            'morpheme': morpheme,
            'type': morpheme_type,
            'meaning': meaning,
            'language': language
        }
        
        morpheme_id = self.db_manager.insert_one('morphemes', data)
        if morpheme_id:
            logger.info(f"Added morpheme: {morpheme} ({morpheme_type})")
            # Reload morphemes
            self.morphology._load_morphemes()
        return morpheme_id
    
    def search_word_analyses(self, word: str) -> List[Dict[str, Any]]:
        """
        Search for previous analyses of a word
        
        Args:
            word: Word to search for
        
        Returns:
            List of previous analyses
        """
        query = "SELECT * FROM word_analysis WHERE word = %s"
        return self.db_manager.fetch_all(query, (word,))
    
    def get_recent_texts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently processed texts
        
        Args:
            limit: Number of texts to retrieve
        
        Returns:
            List of text segments
        """
        query = f"""
        SELECT id, original_text, sentence_count, word_count, processed_at 
        FROM text_segments 
        ORDER BY processed_at DESC 
        LIMIT {limit}
        """
        return self.db_manager.fetch_all(query)
    
    def close(self):
        """Close database connection and cleanup"""
        self.db_manager.disconnect()
        logger.info("NLU System closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience function for quick text analysis
def analyze_text(text: str, db_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick text analysis function
    
    Args:
        text: Input text
        db_config: Database configuration
    
    Returns:
        Analysis results
    """
    with NLUSystem(db_config) as nlu:
        return nlu.process_text(text, store_results=False)
