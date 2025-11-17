"""
Morphology Module
Handles morphological analysis: roots, affixes, lemmatization, and word formation
"""

import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class MorphologyAnalyzer:
    """
    Morphological analysis processor
    Analyzes word structure, identifies roots, prefixes, suffixes, and performs lemmatization
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize morphology analyzer
        
        Args:
            db_manager: DatabaseManager instance for accessing morpheme database
        """
        self.db_manager = db_manager
        
        # Load morphemes from database or use defaults
        self.prefixes = {}
        self.suffixes = {}
        self.roots = {}
        
        if db_manager:
            self._load_morphemes()
        else:
            self._load_default_morphemes()
        
        # English inflection rules
        self.inflection_rules = [
            # Plural rules
            (r'([^aeiou])y$', r'\1ies', 'plural'),  # baby -> babies
            (r'(s|x|z|ch|sh)$', r'\1es', 'plural'),  # box -> boxes
            (r'(f|fe)$', r'ves', 'plural'),  # leaf -> leaves
            (r'([^s])$', r'\1s', 'plural'),  # cat -> cats
            
            # Verb tenses
            (r'([^aeiou])y$', r'\1ied', 'past'),  # cry -> cried
            (r'e$', r'ed', 'past'),  # hope -> hoped
            (r'([^aeiouy])([aeiouy])([^aeiouy])$', r'\1\2\3\3ed', 'past'),  # stop -> stopped
            (r'$', r'ed', 'past'),  # walk -> walked
            
            # Progressive
            (r'ie$', r'ying', 'progressive'),  # die -> dying
            (r'e$', r'ing', 'progressive'),  # hope -> hoping
            (r'([^aeiouy])([aeiouy])([^aeiouy])$', r'\1\2\3\3ing', 'progressive'),  # run -> running
            (r'$', r'ing', 'progressive'),  # walk -> walking
            
            # Comparative/Superlative
            (r'([^aeiou])y$', r'\1ier', 'comparative'),  # happy -> happier
            (r'e$', r'er', 'comparative'),  # nice -> nicer
            (r'$', r'er', 'comparative'),  # fast -> faster
            
            (r'([^aeiou])y$', r'\1iest', 'superlative'),  # happy -> happiest
            (r'e$', r'est', 'superlative'),  # nice -> nicest
            (r'$', r'est', 'superlative'),  # fast -> fastest
        ]
        
        # Irregular forms (common English)
        self.irregular_verbs = {
            'was': 'be', 'were': 'be', 'been': 'be', 'being': 'be',
            'had': 'have', 'has': 'have', 'having': 'have',
            'did': 'do', 'does': 'do', 'done': 'do', 'doing': 'do',
            'went': 'go', 'gone': 'go', 'going': 'go',
            'saw': 'see', 'seen': 'see', 'seeing': 'see',
            'took': 'take', 'taken': 'take', 'taking': 'take',
            'came': 'come', 'coming': 'come',
            'got': 'get', 'gotten': 'get', 'getting': 'get',
            'made': 'make', 'making': 'make',
            'said': 'say', 'saying': 'say',
            'thought': 'think', 'thinking': 'think',
            'found': 'find', 'finding': 'find',
            'gave': 'give', 'given': 'give', 'giving': 'give',
            'told': 'tell', 'telling': 'tell',
            'felt': 'feel', 'feeling': 'feel',
            'knew': 'know', 'known': 'know', 'knowing': 'know',
            'left': 'leave', 'leaving': 'leave',
            'kept': 'keep', 'keeping': 'keep',
            'held': 'hold', 'holding': 'hold',
            'wrote': 'write', 'written': 'write', 'writing': 'write',
            'stood': 'stand', 'standing': 'stand',
            'heard': 'hear', 'hearing': 'hear',
            'brought': 'bring', 'bringing': 'bring',
            'began': 'begin', 'begun': 'begin', 'beginning': 'begin',
            'ran': 'run', 'running': 'run',
            'sat': 'sit', 'sitting': 'sit',
            'spoke': 'speak', 'spoken': 'speak', 'speaking': 'speak',
            'ate': 'eat', 'eaten': 'eat', 'eating': 'eat',
        }
        
        self.irregular_plurals = {
            'children': 'child',
            'men': 'man',
            'women': 'woman',
            'feet': 'foot',
            'teeth': 'tooth',
            'mice': 'mouse',
            'geese': 'goose',
            'people': 'person',
        }
    
    def _load_default_morphemes(self):
        """Load default morpheme dictionaries"""
        self.prefixes = {
            'un': 'not, opposite of',
            're': 'again, back',
            'pre': 'before',
            'post': 'after',
            'dis': 'not, opposite',
            'mis': 'wrongly',
            'anti': 'against',
            'auto': 'self',
            'co': 'together',
            'de': 'remove, reduce',
            'ex': 'out of, former',
            'in': 'not, in',
            'inter': 'between',
            'non': 'not',
            'over': 'excessive',
            'sub': 'under',
            'super': 'above',
            'trans': 'across',
            'under': 'below',
        }
        
        self.suffixes = {
            'ed': 'past tense',
            'ing': 'present participle',
            's': 'plural/3rd person',
            'es': 'plural',
            'er': 'comparative/agent',
            'est': 'superlative',
            'ly': 'adverb',
            'ness': 'state/quality',
            'tion': 'action/process',
            'sion': 'action/process',
            'ment': 'action/result',
            'able': 'capable of',
            'ible': 'capable of',
            'ful': 'full of',
            'less': 'without',
            'ous': 'possessing',
            'ive': 'tending to',
            'al': 'relating to',
            'ity': 'state/quality',
            'ize': 'make/become',
            'ise': 'make/become',
        }
    
    def _load_morphemes(self):
        """Load morphemes from database"""
        try:
            # Load prefixes
            prefixes_query = "SELECT morpheme, meaning FROM morphemes WHERE type = 'prefix'"
            prefix_results = self.db_manager.fetch_all(prefixes_query)
            self.prefixes = {r['morpheme']: r['meaning'] for r in prefix_results}
            
            # Load suffixes
            suffixes_query = "SELECT morpheme, meaning FROM morphemes WHERE type = 'suffix'"
            suffix_results = self.db_manager.fetch_all(suffixes_query)
            self.suffixes = {r['morpheme']: r['meaning'] for r in suffix_results}
            
            # Load roots
            roots_query = "SELECT morpheme, meaning FROM morphemes WHERE type = 'root'"
            root_results = self.db_manager.fetch_all(roots_query)
            self.roots = {r['morpheme']: r['meaning'] for r in root_results}
            
            logger.info(f"Loaded {len(self.prefixes)} prefixes, {len(self.suffixes)} suffixes, {len(self.roots)} roots")
        except Exception as e:
            logger.error(f"Failed to load morphemes from database: {e}")
            self._load_default_morphemes()
    
    def analyze_word(self, word: str) -> Dict[str, any]:
        """
        Perform complete morphological analysis of a word
        
        Args:
            word: Input word
        
        Returns:
            Dictionary with morphological analysis
        """
        word_lower = word.lower()
        
        analysis = {
            'original': word,
            'lemma': self.lemmatize(word_lower),
            'prefix': None,
            'root': None,
            'suffix': None,
            'morphemes': [],
            'possible_pos': []
        }
        
        # Check for irregular forms first
        if word_lower in self.irregular_verbs:
            analysis['lemma'] = self.irregular_verbs[word_lower]
            analysis['root'] = self.irregular_verbs[word_lower]
            analysis['possible_pos'] = ['verb']
            analysis['morphemes'].append({
                'type': 'root',
                'form': self.irregular_verbs[word_lower],
                'meaning': 'verb root (irregular)'
            })
            return analysis
        
        if word_lower in self.irregular_plurals:
            analysis['lemma'] = self.irregular_plurals[word_lower]
            analysis['root'] = self.irregular_plurals[word_lower]
            analysis['possible_pos'] = ['noun']
            analysis['morphemes'].append({
                'type': 'root',
                'form': self.irregular_plurals[word_lower],
                'meaning': 'noun root (irregular plural)'
            })
            return analysis
        
        # Identify prefix
        prefix_result = self._identify_prefix(word_lower)
        if prefix_result:
            analysis['prefix'] = prefix_result['prefix']
            analysis['morphemes'].append({
                'type': 'prefix',
                'form': prefix_result['prefix'],
                'meaning': prefix_result['meaning']
            })
            remaining = prefix_result['remaining']
        else:
            remaining = word_lower
        
        # Identify suffix
        suffix_result = self._identify_suffix(remaining)
        if suffix_result:
            analysis['suffix'] = suffix_result['suffix']
            analysis['morphemes'].append({
                'type': 'suffix',
                'form': suffix_result['suffix'],
                'meaning': suffix_result['meaning']
            })
            analysis['root'] = suffix_result['remaining']
            
            # Infer POS from suffix
            analysis['possible_pos'] = self._infer_pos_from_suffix(suffix_result['suffix'])
        else:
            analysis['root'] = remaining
        
        # Add root morpheme
        if analysis['root']:
            analysis['morphemes'].insert(
                1 if analysis['prefix'] else 0,
                {
                    'type': 'root',
                    'form': analysis['root'],
                    'meaning': self.roots.get(analysis['root'], 'word root')
                }
            )
        
        return analysis
    
    def _identify_prefix(self, word: str) -> Optional[Dict[str, str]]:
        """Identify prefix in a word"""
        for prefix, meaning in sorted(self.prefixes.items(), key=lambda x: len(x[0]), reverse=True):
            if word.startswith(prefix):
                remaining = word[len(prefix):]
                # Ensure remaining part is substantial
                if len(remaining) >= 3:
                    return {
                        'prefix': prefix,
                        'meaning': meaning,
                        'remaining': remaining
                    }
        return None
    
    def _identify_suffix(self, word: str) -> Optional[Dict[str, str]]:
        """Identify suffix in a word"""
        for suffix, meaning in sorted(self.suffixes.items(), key=lambda x: len(x[0]), reverse=True):
            if word.endswith(suffix):
                remaining = word[:-len(suffix)]
                # Ensure remaining part is substantial
                if len(remaining) >= 3:
                    return {
                        'suffix': suffix,
                        'meaning': meaning,
                        'remaining': remaining
                    }
        return None
    
    def _infer_pos_from_suffix(self, suffix: str) -> List[str]:
        """Infer possible parts of speech from suffix"""
        pos_map = {
            'ly': ['adverb'],
            'ness': ['noun'],
            'tion': ['noun'],
            'sion': ['noun'],
            'ment': ['noun'],
            'ity': ['noun'],
            'er': ['noun', 'adjective'],
            'est': ['adjective'],
            'able': ['adjective'],
            'ible': ['adjective'],
            'ful': ['adjective'],
            'less': ['adjective'],
            'ous': ['adjective'],
            'ive': ['adjective'],
            'al': ['adjective'],
            'ed': ['verb', 'adjective'],
            'ing': ['verb', 'noun', 'adjective'],
            's': ['noun', 'verb'],
            'es': ['noun', 'verb'],
            'ize': ['verb'],
            'ise': ['verb'],
        }
        return pos_map.get(suffix, [])
    
    def lemmatize(self, word: str) -> str:
        """
        Convert word to its base/dictionary form (lemma)
        
        Args:
            word: Input word
        
        Returns:
            Lemmatized form
        """
        word_lower = word.lower()
        
        # Check irregular forms
        if word_lower in self.irregular_verbs:
            return self.irregular_verbs[word_lower]
        if word_lower in self.irregular_plurals:
            return self.irregular_plurals[word_lower]
        
        # Try removing common suffixes
        lemma = word_lower
        
        # Remove inflectional suffixes
        suffixes_to_try = [
            ('ies', 'y'),    # babies -> baby
            ('ied', 'y'),    # cried -> cry
            ('ying', 'ie'),  # dying -> die
            ('sses', 'ss'),  # classes -> class
            ('xes', 'x'),    # boxes -> box
            ('zes', 'z'),    # buzzes -> buzz
            ('ches', 'ch'),  # watches -> watch
            ('shes', 'sh'),  # wishes -> wish
            ('ves', 'f'),    # leaves -> leaf
            ('ing', ''),     # walking -> walk
            ('ed', ''),      # walked -> walk
            ('es', ''),      # boxes -> box
            ('s', ''),       # cats -> cat
        ]
        
        for suffix, replacement in suffixes_to_try:
            if lemma.endswith(suffix):
                potential_lemma = lemma[:-len(suffix)] + replacement
                # Simple validation: lemma should be at least 2 chars
                if len(potential_lemma) >= 2:
                    lemma = potential_lemma
                    break
        
        return lemma
    
    def segment_morphemes(self, word: str) -> List[str]:
        """
        Segment word into constituent morphemes
        
        Args:
            word: Input word
        
        Returns:
            List of morphemes
        """
        analysis = self.analyze_word(word)
        morphemes = []
        
        for morpheme in analysis['morphemes']:
            morphemes.append(morpheme['form'])
        
        return morphemes
    
    def analyze_batch(self, words: List[str], store_in_db: bool = True) -> List[Dict[str, any]]:
        """
        Analyze multiple words
        
        Args:
            words: List of words
            store_in_db: Whether to store results in database
        
        Returns:
            List of analysis results
        """
        results = []
        
        for word in words:
            analysis = self.analyze_word(word)
            results.append(analysis)
        
        # Store in database if requested
        if store_in_db and self.db_manager:
            self._store_analyses(results)
        
        return results
    
    def _store_analyses(self, analyses: List[Dict[str, any]]):
        """Store morphological analyses in database"""
        records = []
        
        for analysis in analyses:
            record = {
                'word': analysis['original'],
                'root': analysis['root'],
                'prefix': analysis['prefix'],
                'suffix': analysis['suffix'],
                'lemma': analysis['lemma'],
                'pos_tag': ','.join(analysis['possible_pos']) if analysis['possible_pos'] else None
            }
            records.append(record)
        
        if records:
            self.db_manager.insert_many('word_analysis', records)
            logger.info(f"Stored {len(records)} morphological analyses")
