"""
Segmentation Module
Handles text segmentation at different levels: sentences, words, and tokens
"""

import re
from typing import List, Dict, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Segmenter:
    """
    Text segmentation processor
    Breaks text into sentences, words, and tokens
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize segmenter
        
        Args:
            db_manager: DatabaseManager instance for storing results
        """
        self.db_manager = db_manager
        
        # Sentence boundary patterns
        self.sentence_endings = re.compile(r'([.!?]+[\s\'")\]]*)')
        
        # Common abbreviations that don't end sentences
        self.abbreviations = {
            'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
            'etc.', 'vs.', 'i.e.', 'e.g.', 'cf.', 'Inc.', 'Ltd.',
            'Ave.', 'St.', 'Rd.', 'Blvd.'
        }
        
        # Punctuation patterns
        self.punctuation = re.compile(r'[^\w\s]')
        
        # Common English stopwords
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for',
            'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on',
            'that', 'the', 'to', 'was', 'will', 'with', 'the'
        }
    
    def segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into sentences
        
        Args:
            text: Input text
        
        Returns:
            List of sentences
        """
        # Clean the text
        text = text.strip()
        if not text:
            return []
        
        # Split by sentence boundaries
        sentences = []
        current_sentence = []
        
        # Split text into potential sentences
        parts = self.sentence_endings.split(text)
        
        i = 0
        while i < len(parts):
            part = parts[i].strip()
            
            if not part:
                i += 1
                continue
            
            # Check if this is a sentence ending
            if self.sentence_endings.match(part):
                current_sentence.append(part)
                # Join and add sentence
                sentence = ''.join(current_sentence).strip()
                if sentence:
                    sentences.append(sentence)
                current_sentence = []
            else:
                # Check for abbreviations
                if i + 1 < len(parts) and parts[i + 1].strip() in ['.', '!', '?']:
                    # Check if current part ends with known abbreviation
                    is_abbr = False
                    for abbr in self.abbreviations:
                        if part.endswith(abbr[:-1]):  # Without the period
                            is_abbr = True
                            break
                    
                    if is_abbr:
                        current_sentence.append(part + parts[i + 1])
                        i += 2
                        continue
                
                current_sentence.append(part)
            
            i += 1
        
        # Add remaining sentence
        if current_sentence:
            sentence = ''.join(current_sentence).strip()
            if sentence:
                sentences.append(sentence)
        
        return sentences
    
    def segment_words(self, text: str) -> List[str]:
        """
        Segment text into words
        
        Args:
            text: Input text (sentence or phrase)
        
        Returns:
            List of words
        """
        # Split by whitespace and punctuation
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def tokenize(self, text: str, preserve_punctuation: bool = True) -> List[Dict[str, Any]]:
        """
        Tokenize text into detailed tokens
        
        Args:
            text: Input text
            preserve_punctuation: Include punctuation as separate tokens
        
        Returns:
            List of token dictionaries with metadata
        """
        tokens = []
        position = 0
        
        # Pattern to match words and punctuation separately
        if preserve_punctuation:
            pattern = r'\w+|[^\w\s]'
        else:
            pattern = r'\w+'
        
        for match in re.finditer(pattern, text):
            token_text = match.group()
            
            # Determine token properties
            is_punct = bool(self.punctuation.match(token_text))
            is_stopword = token_text.lower() in self.stopwords
            
            token = {
                'text': token_text,
                'position': position,
                'start_char': match.start(),
                'end_char': match.end(),
                'is_punctuation': is_punct,
                'is_stopword': is_stopword and not is_punct
            }
            
            tokens.append(token)
            position += 1
        
        return tokens
    
    def process_text(self, text: str, store_in_db: bool = True) -> Dict[str, Any]:
        """
        Complete text processing: segment and store
        
        Args:
            text: Input text
            store_in_db: Whether to store results in database
        
        Returns:
            Dictionary with processing results
        """
        # Segment sentences
        sentences = self.segment_sentences(text)
        
        results = {
            'original_text': text,
            'sentence_count': len(sentences),
            'sentences': [],
            'total_words': 0
        }
        
        # Process each sentence
        for idx, sentence in enumerate(sentences):
            words = self.segment_words(sentence)
            tokens = self.tokenize(sentence)
            
            sentence_data = {
                'text': sentence,
                'position': idx,
                'words': words,
                'word_count': len(words),
                'tokens': tokens
            }
            
            results['sentences'].append(sentence_data)
            results['total_words'] += len(words)
        
        # Store in database if requested
        if store_in_db and self.db_manager:
            self._store_segmentation(results)
        
        return results
    
    def _store_segmentation(self, results: Dict[str, Any]) -> Optional[int]:
        """
        Store segmentation results in database
        
        Args:
            results: Processing results dictionary
        
        Returns:
            Text segment ID or None if storage fails
        """
        if not self.db_manager:
            logger.warning("No database manager available, skipping storage")
            return None
        
        # Insert main text segment
        text_data = {
            'original_text': results['original_text'],
            'sentence_count': results['sentence_count'],
            'word_count': results['total_words']
        }
        
        text_id = self.db_manager.insert_one('text_segments', text_data)
        
        if not text_id:
            logger.error("Failed to store text segment")
            return None
        
        # Insert sentences and tokens
        for sentence_data in results['sentences']:
            sentence_record = {
                'text_segment_id': text_id,
                'sentence_text': sentence_data['text'],
                'sentence_position': sentence_data['position'],
                'word_count': sentence_data['word_count']
            }
            
            sentence_id = self.db_manager.insert_one('sentences', sentence_record)
            
            if sentence_id:
                # Insert tokens
                token_records = []
                for token in sentence_data['tokens']:
                    token_record = {
                        'sentence_id': sentence_id,
                        'token': token['text'],
                        'token_position': token['position'],
                        'is_punctuation': token['is_punctuation'],
                        'is_stopword': token['is_stopword']
                    }
                    token_records.append(token_record)
                
                if token_records:
                    self.db_manager.insert_many('tokens', token_records)
        
        logger.info(f"Stored segmentation results with ID: {text_id}")
        return text_id
    
    def get_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate statistics from segmentation results
        
        Args:
            results: Processing results
        
        Returns:
            Statistics dictionary
        """
        total_tokens = sum(len(s['tokens']) for s in results['sentences'])
        total_stopwords = sum(
            sum(1 for t in s['tokens'] if t['is_stopword'])
            for s in results['sentences']
        )
        
        avg_words_per_sentence = results['total_words'] / results['sentence_count'] if results['sentence_count'] > 0 else 0
        
        return {
            'total_sentences': results['sentence_count'],
            'total_words': results['total_words'],
            'total_tokens': total_tokens,
            'total_stopwords': total_stopwords,
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'unique_words': len(set(
                word for s in results['sentences'] for word in s['words']
            ))
        }
