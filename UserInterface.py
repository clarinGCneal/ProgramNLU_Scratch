"""
Interactive test for segmentation, morphology, and database storage
"""

from nlu_system import NLUSystem
from config import DB_CONFIG
import json


def process_and_store_sentence(nlu, sentence):
    """
    Process a sentence and store in database
    
    Args:
        nlu: NLUSystem instance
        sentence: Input sentence to process
    """
    print(f"\n{'='*60}")
    print(f"Processing: {sentence}")
    print(f"{'='*60}\n")
    
    # Process with morphology and store results
    results = nlu.process_text(
        sentence, 
        analyze_morphology=True, 
        store_results=True  # This stores in database
    )
    
    # Display segmentation results
    print("SEGMENTATION:")
    print("-" * 40)
    seg = results.get('segmentation', {})
    print(f"Sentences: {seg.get('sentence_count', 0)}")
    
    # Get sentences list
    sentences = seg.get('sentences', [])
    if sentences:
        first_sent = sentences[0]
        tokens = first_sent.get('tokens', [])
        print(f"Tokens: {len(tokens)}")
        
        print(f"\nToken details:")
        for token in tokens:
            text = token.get('text', '')
            is_punct = token.get('is_punctuation', False)
            is_stop = token.get('is_stopword', False)
            print(f"  '{text:15}' - Punct: {is_punct}, Stop: {is_stop}")
    
    # Display morphological analysis
    print("\nMORPHOLOGICAL ANALYSIS:")
    print("-" * 40)
    morphology = results.get('morphology', [])
    
    if not morphology:
        print("  No morphological analysis available")
    else:
        for morph in morphology:
            original = morph.get('original', '')
            lemma = morph.get('lemma', '')
            morphemes = morph.get('morphemes', [])
            
            print(f"\n  Word: {original}")
            print(f"    Lemma: {lemma}")
            
            if morphemes:
                morpheme_forms = [m.get('form', '') for m in morphemes]
                print(f"    Morphemes: {' + '.join(morpheme_forms)}")
            
            prefix = morph.get('prefix')
            root = morph.get('root')
            suffix = morph.get('suffix')
            possible_pos = morph.get('possible_pos', [])
            
            if prefix:
                print(f"    Prefix: {prefix}")
            if root:
                print(f"    Root: {root}")
            if suffix:
                print(f"    Suffix: {suffix}")
            if possible_pos:
                print(f"    Possible POS: {', '.join(possible_pos)}")
    
    # Display statistics
    print("\nSTATISTICS:")
    print("-" * 40)
    stats = results.get('statistics', {})
    if stats:
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print("  No statistics available")
    
    print(f"\n✓ Data stored in database successfully!\n")
    
    return results


def verify_database_storage(nlu):
    """
    Verify what's stored in the database
    """
    print(f"\n{'='*60}")
    print("DATABASE CONTENTS")
    print(f"{'='*60}\n")
    
    try:
        # Get table counts using DatabaseManager method
        counts = nlu.db_manager.get_table_counts()
        
        print(f"Total text segments in database: {counts.get('text_segments', 0)}")
        print(f"Total sentences in database: {counts.get('sentences', 0)}")
        print(f"Total tokens in database: {counts.get('tokens', 0)}")
        print(f"Total morphemes in dictionary: {counts.get('morphemes', 0)}")
        print(f"Total word analyses: {counts.get('word_analysis', 0)}")
        
        # Show recent text segments
        print("\nRecent text segments (last 5):")
        print("-" * 60)
        segments = nlu.db_manager.get_recent_text_segments(5)
        for seg in segments:
            print(f"  [{seg['id']:3d}] Sentences: {seg['sentence_count']} | "
                  f"Words: {seg['word_count']:3d} | {seg['text_preview']}...")
            print(f"         Processed: {seg['processed_at']}")
        
        # Show recent sentences
        print("\nRecent sentences (last 10):")
        print("-" * 60)
        sentences = nlu.db_manager.get_recent_sentences(10)
        for sent in sentences:
            print(f"  [{sent['id']:3d}] Pos: {sent['sentence_position']} | "
                  f"Words: {sent['word_count']:2d} | {sent['text']}")
        
        # Show tokens from most recent sentence
        print("\nTokens from most recent sentence:")
        print("-" * 60)
        tokens = nlu.db_manager.get_tokens_by_sentence(limit=15)
        
        if tokens:
            for token in tokens:
                markers = []
                if token['is_punctuation']:
                    markers.append("PUNCT")
                if token['is_stopword']:
                    markers.append("STOP")
                marker_str = f" [{', '.join(markers)}]" if markers else ""
                print(f"    {token['token_position']:2d}. {token['token']:15s}{marker_str}")
        else:
            print("    No tokens found")
        
        # Show recent word analyses
        print("\nRecent word analyses (last 10):")
        print("-" * 60)
        analyses = nlu.db_manager.get_recent_word_analyses(10)
        
        if analyses:
            for analysis in analyses:
                parts = []
                if analysis['prefix']:
                    parts.append(f"prefix:{analysis['prefix']}")
                if analysis['root']:
                    parts.append(f"root:{analysis['root']}")
                if analysis['suffix']:
                    parts.append(f"suffix:{analysis['suffix']}")
                
                morphology_str = " + ".join(parts) if parts else "N/A"
                pos_str = f"[{analysis['pos_tag']}]" if analysis['pos_tag'] else ""
                lemma_str = f"→ {analysis['lemma']}" if analysis['lemma'] and analysis['lemma'] != analysis['word'] else ""
                
                print(f"  {analysis['word']:20s} {pos_str:10s} {lemma_str:15s} | {morphology_str}")
        else:
            print("    No word analyses found")
            
    except Exception as e:
        print(f"Error querying database: {e}")
        import traceback
        traceback.print_exc()


def clear_database_data(nlu):
    """
    Clear data from analysis tables (keeps morpheme dictionary)
    """
    print(f"\n{'='*60}")
    print("CLEAR DATABASE DATA")
    print(f"{'='*60}\n")
    
    print("⚠️  WARNING: This will delete all stored analysis data!")
    print("\nTables that will be cleared:")
    print("  • text_segments (processed texts)")
    print("  • sentences (segmented sentences)")
    print("  • tokens (word tokens)")
    print("  • word_analysis (morphological analyses)")
    print("\nNote: The morpheme dictionary will NOT be deleted.")
    
    confirm = input("\nAre you sure you want to clear all data? Type 'YES' to confirm: ").strip()
    
    if confirm != 'YES':
        print("Operation cancelled.")
        return
    
    try:
        # Use DatabaseManager method to clear data
        result = nlu.db_manager.clear_analysis_data()
        
        if result['success']:
            print(f"\nDeleting:")
            for table, count in result['deleted_counts'].items():
                print(f"  • {count} records from {table}")
            
            print("\nClearing data...")
            print("  ✓ Tokens cleared")
            print("  ✓ Word analyses cleared")
            print("  ✓ Sentences cleared")
            print("  ✓ Text segments cleared")
            print("  ✓ Auto-increment counters reset")
            
            print("\n✓ Database cleared successfully!")
            print("\nThe morpheme dictionary has been preserved.")
            
            # Verify morpheme count
            morpheme_count = nlu.db_manager.get_morpheme_count()
            print(f"  Morphemes in dictionary: {morpheme_count}")
        else:
            print(f"\n✗ Error clearing database: {result['error']}")
            
    except Exception as e:
        print(f"\n✗ Error clearing database: {e}")
        import traceback
        traceback.print_exc()


def interactive_mode():
    """Interactive mode for entering sentences"""
    print("=" * 60)
    print("INTERACTIVE SEGMENTATION & MORPHOLOGY TEST")
    print("=" * 60)
    print("\nNote: Make sure config.py has correct database credentials!")
    print()
    
    try:
        # Initialize NLU system
        nlu = NLUSystem(DB_CONFIG)
        print("✓ NLU System initialized successfully\n")
        
        while True:
            print("-" * 60)
            sentence = input("\nEnter a sentence (or 'quit'/'show'/'clear'): ").strip()
            
            if sentence.lower() in ['quit', 'exit', 'q']:
                print("\nExiting...")
                break
            
            if sentence.lower() == 'show':
                verify_database_storage(nlu)
                continue
            
            if sentence.lower() == 'clear':
                clear_database_data(nlu)
                continue
            
            if not sentence:
                print("Please enter a valid sentence.")
                continue
            
            # Process the sentence
            try:
                results = process_and_store_sentence(nlu, sentence)
                
                # Ask if user wants to see detailed results
                show_details = input("\nShow detailed JSON results? (y/n): ").strip().lower()
                if show_details == 'y':
                    print("\nDetailed Results:")
                    print(json.dumps(results, indent=2, default=str))
                
            except Exception as e:
                print(f"\n✗ Error processing sentence: {e}")
                import traceback
                traceback.print_exc()
        
        # Final database summary
        print("\n" + "=" * 60)
        verify_database_storage(nlu)
        print("=" * 60)
        
        nlu.close()
        print("\n✓ System closed successfully")
        
    except Exception as e:
        print(f"\n✗ Error initializing NLU System: {e}")
        print("Please check your database configuration in config.py")
        import traceback
        traceback.print_exc()


def test_mode():
    """Test mode with predefined sentences"""
    print("=" * 60)
    print("TEST MODE - Predefined Sentences")
    print("=" * 60)
    
    # Ask if user wants to clear database first
    clear_first = input("\nClear database before testing? (y/n): ").strip().lower()
    
    test_sentences = [
        "The cat sits on the mat.",
        "She quickly ran towards the beautiful house.",
        "Unbelievable preprocessing capabilities are essential.",
        "Children were playing happily in the gardens."
    ]
    
    try:
        nlu = NLUSystem(DB_CONFIG)
        print("✓ NLU System initialized successfully\n")
        
        # Clear if requested
        if clear_first == 'y':
            clear_database_data(nlu)
            print()
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"\n[Test {i}/{len(test_sentences)}]")
            
            try:
                process_and_store_sentence(nlu, sentence)
            except Exception as e:
                print(f"\n✗ Error processing sentence: {e}")
                import traceback
                traceback.print_exc()
            
            if i < len(test_sentences):
                input("\nPress Enter to continue...")
        
        print("\n" + "=" * 60)
        verify_database_storage(nlu)
        print("=" * 60)
        
        nlu.close()
        print("\n✓ All tests completed successfully")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("NLU SYSTEM - SEGMENTATION & MORPHOLOGY TEST")
    print("=" * 60 + "\n")
    
    mode = input("Choose mode:\n1. Interactive (enter your own sentences)\n2. Test (use predefined sentences)\n3. Clear database only\n\nEnter choice (1/2/3): ").strip()
    
    if mode == '1':
        interactive_mode()
    elif mode == '2':
        test_mode()
    elif mode == '3':
        try:
            nlu = NLUSystem(DB_CONFIG)
            clear_database_data(nlu)
            nlu.close()
        except Exception as e:
            print(f"\n✗ Error: {e}")
    else:
        print("Invalid choice. Please run again and select 1, 2, or 3.")


if __name__ == "__main__":
    main()