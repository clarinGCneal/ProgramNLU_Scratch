# Natural Language Understanding (NLU) System

A modular, scalable Natural Language Understanding system built from scratch using Python and MySQL. This system implements core NLU components starting with **Segmentation** and **Morphology** modules.

## Features

### 1. Segmentation Module
- **Sentence Segmentation**: Intelligently splits text into sentences, handling abbreviations and edge cases
- **Word Segmentation**: Extracts words from text
- **Tokenization**: Detailed tokenization with metadata (position, punctuation flags, stopword detection)
- **Statistics**: Comprehensive text statistics (word count, sentence count, unique words, etc.)

### 2. Morphology Module
- **Morphological Analysis**: Decomposes words into constituent morphemes (prefixes, roots, suffixes)
- **Lemmatization**: Converts words to their base/dictionary forms
- **Irregular Forms**: Handles irregular verbs and plurals
- **POS Inference**: Infers possible parts of speech from morphological structure
- **Batch Processing**: Efficient analysis of multiple words

## Architecture

```
nlu_system/
├── core/
│   └── database.py          # Database connection manager
├── modules/
│   ├── segmentation.py      # Segmentation module
│   └── morphology.py        # Morphology module
├── database/
│   └── schema.sql           # Database schema
├── config.py                # Configuration settings
├── nlu_system.py            # Main orchestrator
├── examples.py              # Usage examples
├── requirements.txt         # Dependencies
└── test_modules.py          # Test Module connection w/o db
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup MySQL Database

Create a MySQL database:

```sql
CREATE DATABASE nlu_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure Database Connection

Edit `config.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'nlu_system',
    'port': 3306
}
```

### 4. Initialize Database Schema

```python
from nlu_system import NLUSystem

nlu = NLUSystem()
nlu.initialize_database('database/schema.sql')
nlu.close()
```

## Usage

### Basic Text Analysis

```python
from nlu_system import NLUSystem

# Initialize system
nlu = NLUSystem()

# Process text
text = "Natural language processing is fascinating!"
results = nlu.process_text(text)

# Access results
print(f"Sentences: {results['segmentation']['sentence_count']}")
print(f"Words: {results['statistics']['total_words']}")

nlu.close()
```

### Segmentation Only

```python
from nlu_system import NLUSystem

nlu = NLUSystem()

# Segment into sentences
text = "Hello world! How are you? I'm doing great."
sentences = nlu.segmenter.segment_sentences(text)
print(sentences)  # ['Hello world!', 'How are you?', "I'm doing great."]

# Tokenize with metadata
tokens = nlu.segmenter.tokenize("Hello, world!")
for token in tokens:
    print(f"{token['text']} - Punctuation: {token['is_punctuation']}")

nlu.close()
```

### Morphological Analysis

```python
from nlu_system import NLUSystem

nlu = NLUSystem()

# Analyze a single word
analysis = nlu.analyze_word("unhappiness")
print(f"Lemma: {analysis['lemma']}")
print(f"Prefix: {analysis['prefix']}")
print(f"Root: {analysis['root']}")
print(f"Suffix: {analysis['suffix']}")
print(f"Morphemes: {[m['form'] for m in analysis['morphemes']]}")

# Lemmatize text
lemmatized = nlu.lemmatize_text("The children were running")
print(lemmatized)  # "the child be run"

nlu.close()
```

### Batch Processing

```python
from nlu_system import NLUSystem

nlu = NLUSystem()

# Analyze multiple words
words = ['running', 'unhappiness', 'preprocessing']
analyses = nlu.morphology.analyze_batch(words, store_in_db=True)

for analysis in analyses:
    print(f"{analysis['original']} -> {analysis['lemma']}")

nlu.close()
```

### Context Manager (Recommended)

```python
from nlu_system import NLUSystem

with NLUSystem() as nlu:
    results = nlu.process_text("Your text here")
    # Automatic cleanup when done
```

## Database Schema

### Tables

1. **morphemes**: Stores morpheme dictionary (roots, prefixes, suffixes)
2. **word_analysis**: Stores morphological analyses of words
3. **text_segments**: Stores processed texts
4. **sentences**: Individual sentences from texts
5. **tokens**: Tokens from segmentation
6. **morphology_rules**: Custom morphological rules

## API Reference

### NLUSystem Class

Main orchestrator for the NLU pipeline.

#### Methods

- `__init__(db_config)`: Initialize the system
- `initialize_database(schema_file)`: Setup database schema
- `process_text(text, analyze_morphology, store_results)`: Complete text processing
- `analyze_sentence(sentence)`: Analyze a single sentence
- `analyze_word(word)`: Detailed word analysis
- `lemmatize_text(text)`: Lemmatize all words in text
- `get_text_statistics(text)`: Get comprehensive statistics
- `add_morpheme(morpheme, type, meaning, language)`: Add custom morpheme
- `search_word_analyses(word)`: Search previous analyses
- `get_recent_texts(limit)`: Get recently processed texts
- `close()`: Close database connection

### Segmenter Class

Handles text segmentation.

#### Methods

- `segment_sentences(text)`: Split text into sentences
- `segment_words(text)`: Extract words from text
- `tokenize(text, preserve_punctuation)`: Detailed tokenization
- `process_text(text, store_in_db)`: Complete segmentation pipeline
- `get_statistics(results)`: Calculate statistics

### MorphologyAnalyzer Class

Handles morphological analysis.

#### Methods

- `analyze_word(word)`: Complete morphological analysis
- `lemmatize(word)`: Convert to base form
- `segment_morphemes(word)`: Extract morphemes
- `analyze_batch(words, store_in_db)`: Batch analysis

## Extending the System

### Adding Custom Morphemes

```python
with NLUSystem() as nlu:
    # Add a custom prefix
    nlu.add_morpheme('bio', 'prefix', 'relating to life or living things')
    
    # Add a custom suffix
    nlu.add_morpheme('ology', 'suffix', 'study of')
```

### Creating New Modules

The system is designed to be modular. To add a new module:

1. Create a new file in `modules/` directory
2. Implement your module class with database integration
3. Register it in the main `NLUSystem` class
4. Update the database schema if needed

Example structure:

```python
# modules/your_module.py
class YourModule:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
    
    def process(self, input_data):
        # Your processing logic
        pass
```

## Examples

Run the provided examples:

```bash
python examples.py
```

This demonstrates:
1. Basic text analysis
2. Segmentation analysis
3. Morphological analysis
4. Sentence analysis
5. Lemmatization
6. Adding custom morphemes
7. Comprehensive statistics

## Scalability Features

- **Modular Design**: Each component is independent and can be scaled separately
- **Database-Backed**: Persistent storage for analyses and reusability
- **Batch Processing**: Efficient handling of multiple items
- **Flexible Configuration**: Easy customization through config files
- **Context Managers**: Proper resource management
- **Logging**: Comprehensive logging for debugging and monitoring

## Future Extensions

The modular architecture supports easy addition of:
- Syntax parsing
- Semantic analysis
- Named Entity Recognition (NER)
- Part-of-Speech (POS) tagging
- Dependency parsing
- Sentiment analysis
- Word embeddings
- Language models

## Performance Considerations

- Use batch processing for multiple words/sentences
- Set `store_results=False` for analysis-only operations
- Implement caching for frequently analyzed words
- Index database tables appropriately for your queries
- Consider connection pooling for high-load scenarios

## Troubleshooting

### Database Connection Issues

```python
# Test your connection
from core.database import DatabaseManager
db = DatabaseManager(**DB_CONFIG)
if db.connect():
    print("Connection successful!")
db.disconnect()
```

### Import Errors

Ensure all files have proper `__init__.py` files and you're running from the correct directory.

## License

This project is open source and available for educational purposes.

## Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## Contact

For questions or suggestions, please open an issue in the repository.
