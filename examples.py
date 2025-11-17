"""
Example usage of the NLU System
Demonstrates segmentation and morphology modules
"""

from nlu_system import NLUSystem, analyze_text
from config import DB_CONFIG
import json


def example_basic_usage():
    """Basic usage example"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Text Analysis")
    print("=" * 60)
    
    # Initialize NLU system
    nlu = NLUSystem(DB_CONFIG)
    
    # Sample text
    text = """
    Natural language processing is fascinating! It enables computers to 
    understand, interpret, and generate human language. Modern NLP systems 
    use advanced techniques like deep learning and transformers.
    """
    
    # Process text
    results = nlu.process_text(text, analyze_morphology=True, store_results=False)
    
    # Display results
    print(f"\nOriginal Text:\n{text.strip()}\n")
    
    print(f"Statistics:")
    for key, value in results['statistics'].items():
        print(f"  {key}: {value}")
    
    print(f"\nSentences ({results['segmentation']['sentence_count']}):")
    for i, sentence in enumerate(results['segmentation']['sentences'], 1):
        print(f"  {i}. {sentence['text']}")
        print(f"     Words: {sentence['word_count']}")
    
    nlu.close()
    print("\n")


def example_segmentation():
    """Segmentation-focused example"""
    print("=" * 60)
    print("EXAMPLE 2: Segmentation Analysis")
    print("=" * 60)
    
    nlu = NLUSystem(DB_CONFIG)
    
    text = "Dr. Smith went to Washington D.C. on Jan. 5th. He met Ms. Johnson there!"
    
    # Get segmentation results
    results = nlu.segmenter.process_text(text, store_in_db=False)
    
    print(f"\nText: {text}\n")
    print("Sentences:")
    for i, sent in enumerate(results['sentences'], 1):
        print(f"  {i}. {sent['text']}")
    
    print(f"\nTokens from first sentence:")
    if results['sentences']:
        for token in results['sentences'][0]['tokens']:
            print(f"  '{token['text']}' - Punct: {token['is_punctuation']}, "
                  f"Stopword: {token['is_stopword']}")
    
    nlu.close()
    print("\n")


def example_morphology():
    """Morphology-focused example"""
    print("=" * 60)
    print("EXAMPLE 3: Morphological Analysis")
    print("=" * 60)
    
    nlu = NLUSystem(DB_CONFIG)
    
    words = ['unhappiness', 'running', 'preprocessing', 'beautiful', 
             'children', 'went', 'carefully', 'reorganization']
    
    print("\nMorphological Analysis:\n")
    for word in words:
        analysis = nlu.morphology.analyze_word(word)
        
        print(f"Word: {word}")
        print(f"  Lemma: {analysis['lemma']}")
        print(f"  Morphemes: {' + '.join(m['form'] for m in analysis['morphemes'])}")
        
        if analysis['prefix']:
            print(f"  Prefix: {analysis['prefix']}")
        if analysis['root']:
            print(f"  Root: {analysis['root']}")
        if analysis['suffix']:
            print(f"  Suffix: {analysis['suffix']}")
        if analysis['possible_pos']:
            print(f"  Possible POS: {', '.join(analysis['possible_pos'])}")
        print()
    
    nlu.close()
    print()


def example_sentence_analysis():
    """Single sentence analysis"""
    print("=" * 60)
    print("EXAMPLE 4: Sentence Analysis")
    print("=" * 60)
    
    nlu = NLUSystem(DB_CONFIG)
    
    sentence = "The researchers carefully analyzed the preprocessing techniques."
    
    results = nlu.analyze_sentence(sentence)
    
    print(f"\nSentence: {sentence}\n")
    print(f"Word count: {results['word_count']}\n")
    
    print("Tokens:")
    for token in results['tokens']:
        print(f"  {token['text']:<20} Punct: {token['is_punctuation']:<5} "
              f"Stop: {token['is_stopword']}")
    
    print("\nMorphological Analysis:")
    for morph in results['morphology']:
        print(f"\n  {morph['original']}:")
        print(f"    Lemma: {morph['lemma']}")
        print(f"    Morphemes: {[m['form'] for m in morph['morphemes']]}")
    
    nlu.close()
    print("\n")


def example_lemmatization():
    """Lemmatization example"""
    print("=" * 60)
    print("EXAMPLE 5: Text Lemmatization")
    print("=" * 60)
    
    nlu = NLUSystem(DB_CONFIG)
    
    text = "The children were running quickly through the beautiful gardens."
    
    print(f"\nOriginal: {text}")
    print(f"Lemmatized: {nlu.lemmatize_text(text)}\n")
    
    nlu.close()
    print()


def example_add_morpheme():
    """Example of adding custom morphemes"""
    print("=" * 60)
    print("EXAMPLE 6: Adding Custom Morphemes")
    print("=" * 60)
    
    nlu = NLUSystem(DB_CONFIG)
    
    # Add a custom prefix
    print("\nAdding custom morpheme 'cyber' as prefix...")
    morpheme_id = nlu.add_morpheme('cyber', 'prefix', 'relating to computers or internet')
    
    if morpheme_id:
        print(f"Successfully added morpheme with ID: {morpheme_id}")
        
        # Test it
        analysis = nlu.analyze_word('cybersecurity')
        print(f"\nAnalysis of 'cybersecurity':")
        print(f"  Prefix: {analysis['prefix']}")
        print(f"  Root: {analysis['root']}")
    
    nlu.close()
    print("\n")


def example_statistics():
    """Text statistics example"""
    print("=" * 60)
    print("EXAMPLE 7: Comprehensive Statistics")
    print("=" * 60)
    
    nlu = NLUSystem(DB_CONFIG)
    
    text = """
    Artificial intelligence and machine learning are transforming industries.
    These technologies enable computers to learn from data and make intelligent
    decisions. The applications are endless and continuously expanding.
    """
    
    stats = nlu.get_text_statistics(text)
    
    print("\nText Statistics:")
    print(json.dumps(stats, indent=2))
    
    nlu.close()
    print("\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("NLU SYSTEM - EXAMPLE USAGE")
    print("=" * 60 + "\n")
    
    print("Note: Make sure to update config.py with your database credentials!\n")
    
    try:
        example_basic_usage()
        example_segmentation()
        example_morphology()
        example_sentence_analysis()
        example_lemmatization()
        # example_add_morpheme()  # Uncomment to test database insertion
        example_statistics()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Please check your database configuration in config.py")


if __name__ == "__main__":
    main()
