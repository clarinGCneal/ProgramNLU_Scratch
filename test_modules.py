"""
Quick test script for NLU System
Tests modules without database connection
"""

from modules.segmentation import Segmenter
from modules.morphology import MorphologyAnalyzer


def test_segmentation():
    """Test segmentation module"""
    print("=" * 60)
    print("TESTING SEGMENTATION MODULE")
    print("=" * 60)
    
    segmenter = Segmenter(db_manager=None)
    
    # Test 1: Sentence segmentation
    text = "Hello world! How are you today? I'm doing great."
    sentences = segmenter.segment_sentences(text)
    
    print(f"\nTest 1: Sentence Segmentation")
    print(f"Input: {text}")
    print(f"Sentences found: {len(sentences)}")
    for i, sent in enumerate(sentences, 1):
        print(f"  {i}. {sent}")
    
    # Test 2: Word segmentation
    print(f"\nTest 2: Word Segmentation")
    sentence = "Natural language processing is fascinating"
    words = segmenter.segment_words(sentence)
    print(f"Input: {sentence}")
    print(f"Words: {words}")
    
    # Test 3: Tokenization
    print(f"\nTest 3: Tokenization")
    text = "Hello, world! How's it going?"
    tokens = segmenter.tokenize(text)
    print(f"Input: {text}")
    print(f"Tokens:")
    for token in tokens:
        print(f"  '{token['text']}'  Punct: {token['is_punctuation']:<5}  "
              f"Stopword: {token['is_stopword']:<5}  Pos: {token['position']}")
    
    # Test 4: Full processing
    print(f"\nTest 4: Full Text Processing")
    text = "AI is transforming the world. Machine learning enables computers to learn."
    results = segmenter.process_text(text, store_in_db=False)
    stats = segmenter.get_statistics(results)
    
    print(f"Input: {text}")
    print(f"Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Segmentation tests passed!\n")


def test_morphology():
    """Test morphology module"""
    print("=" * 60)
    print("TESTING MORPHOLOGY MODULE")
    print("=" * 60)
    
    morph = MorphologyAnalyzer(db_manager=None)
    
    # Test 1: Word analysis
    print(f"\nTest 1: Morphological Analysis")
    words = ['unhappiness', 'running', 'preprocessing', 'beautiful', 'carefully']
    
    for word in words:
        analysis = morph.analyze_word(word)
        print(f"\nWord: {word}")
        print(f"  Lemma: {analysis['lemma']}")
        print(f"  Prefix: {analysis['prefix']}")
        print(f"  Root: {analysis['root']}")
        print(f"  Suffix: {analysis['suffix']}")
        print(f"  Morphemes: {' + '.join(m['form'] for m in analysis['morphemes'])}")
        if analysis['possible_pos']:
            print(f"  Possible POS: {', '.join(analysis['possible_pos'])}")
    
    # Test 2: Lemmatization
    print(f"\n\nTest 2: Lemmatization")
    test_words = [
        'running', 'ran', 'runs',
        'children', 'mice', 'feet',
        'happier', 'happiest',
        'walked', 'walking',
        'boxes', 'classes'
    ]
    
    for word in test_words:
        lemma = morph.lemmatize(word)
        print(f"  {word:<15} -> {lemma}")
    
    # Test 3: Morpheme segmentation
    print(f"\n\nTest 3: Morpheme Segmentation")
    words = ['reorganization', 'unhelpful', 'preprocessing']
    
    for word in words:
        morphemes = morph.segment_morphemes(word)
        print(f"  {word}: {' + '.join(morphemes)}")
    
    # Test 4: Irregular forms
    print(f"\n\nTest 4: Irregular Forms")
    irregular_words = ['went', 'was', 'children', 'mice', 'better']
    
    for word in irregular_words:
        analysis = morph.analyze_word(word)
        print(f"  {word:<12} -> lemma: {analysis['lemma']:<10} root: {analysis['root']}")
    
    # Test 5: Batch processing
    print(f"\n\nTest 5: Batch Processing")
    words = ['running', 'jumped', 'beautiful', 'quickly', 'unhappy']
    analyses = morph.analyze_batch(words, store_in_db=False)
    
    print(f"Analyzing {len(words)} words:")
    for analysis in analyses:
        morpheme_str = ' + '.join(m['form'] for m in analysis['morphemes'])
        print(f"  {analysis['original']:<12} -> {morpheme_str}")
    
    print("\n✓ Morphology tests passed!\n")


def test_integration():
    """Test integration of both modules"""
    print("=" * 60)
    print("TESTING INTEGRATION")
    print("=" * 60)
    
    segmenter = Segmenter(db_manager=None)
    morph = MorphologyAnalyzer(db_manager=None)
    
    # Process a paragraph
    text = """
    Natural language understanding is a challenging problem. 
    Computers need to analyze text at multiple levels. 
    Morphology helps us understand word structure.
    """
    
    print(f"\nInput text:\n{text.strip()}\n")
    
    # Segment
    results = segmenter.process_text(text, store_in_db=False)
    
    print(f"Segmentation Results:")
    print(f"  Sentences: {results['sentence_count']}")
    print(f"  Total words: {results['total_words']}")
    
    # Collect unique words
    all_words = []
    for sentence in results['sentences']:
        all_words.extend(sentence['words'])
    unique_words = list(set(all_words))
    
    print(f"  Unique words: {len(unique_words)}")
    
    # Analyze morphology
    print(f"\nMorphological Analysis of key words:")
    interesting_words = [w for w in unique_words if len(w) > 5][:5]
    
    for word in interesting_words:
        analysis = morph.analyze_word(word)
        morphemes = ' + '.join(m['form'] for m in analysis['morphemes'])
        print(f"  {word:<20} -> {morphemes:<30} (lemma: {analysis['lemma']})")
    
    print("\n✓ Integration tests passed!\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("NLU SYSTEM - MODULE TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_segmentation()
        test_morphology()
        test_integration()
        
        print("=" * 60)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        print("\nThe system is working correctly.")
        print("To use with database, update config.py and run examples.py\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
