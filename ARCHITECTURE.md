# NLU System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                      (Your Application)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      NLUSystem (Main)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Process Text Pipeline                     │ │
│  │  1. Segmentation → 2. Morphology → 3. Results         │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────┬───────────────────────────────┬─────────────────┘
            │                               │
            ▼                               ▼
┌───────────────────────┐       ┌──────────────────────────┐
│  Segmentation Module  │       │   Morphology Module      │
│  ┌─────────────────┐  │       │  ┌────────────────────┐ │
│  │ - Sentences     │  │       │  │ - Prefix detect    │ │
│  │ - Words         │  │       │  │ - Suffix detect    │ │
│  │ - Tokens        │  │       │  │ - Root extraction  │ │
│  │ - Statistics    │  │       │  │ - Lemmatization    │ │
│  └─────────────────┘  │       │  │ - POS inference    │ │
└───────────┬───────────┘       │  └────────────────────┘ │
            │                   └───────────┬──────────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
                ┌───────────────────────┐
                │   Database Manager    │
                │  ┌──────────────────┐ │
                │  │ - Connections    │ │
                │  │ - CRUD Ops       │ │
                │  │ - Transactions   │ │
                │  └──────────────────┘ │
                └───────────┬───────────┘
                            ▼
                ┌───────────────────────┐
                │    MySQL Database     │
                │  ┌──────────────────┐ │
                │  │ - morphemes      │ │
                │  │ - word_analysis  │ │
                │  │ - text_segments  │ │
                │  │ - sentences      │ │
                │  │ - tokens         │ │
                │  └──────────────────┘ │
                └───────────────────────┘
```

## Module Interaction Flow

### 1. Text Processing Flow

```
User Text Input
      │
      ▼
[Segmentation Module]
      │
      ├─> Sentence Segmentation
      │   └─> ["Sentence 1", "Sentence 2", ...]
      │
      ├─> Word Segmentation
      │   └─> ["word1", "word2", ...]
      │
      └─> Tokenization
          └─> [{"text": "word1", "pos": 0, ...}, ...]
      │
      ▼
[Morphology Module]
      │
      ├─> Prefix Detection
      ├─> Root Extraction
      ├─> Suffix Detection
      ├─> Lemmatization
      └─> POS Inference
      │
      ▼
[Results + Statistics]
      │
      └─> Stored in Database / Returned to User
```

### 2. Database Interaction

```
Module Request
      │
      ▼
[Database Manager]
      │
      ├─> Connection Pool
      ├─> Query Execution
      ├─> Transaction Management
      └─> Error Handling
      │
      ▼
[MySQL Database]
      │
      └─> Persistent Storage
```

## Component Details

### NLUSystem (Main Orchestrator)

**Responsibilities:**
- Initialize all modules
- Coordinate pipeline execution
- Manage database connections
- Provide unified API
- Handle errors and logging

**Key Methods:**
- `process_text()` - Full pipeline
- `analyze_sentence()` - Single sentence
- `analyze_word()` - Single word
- `lemmatize_text()` - Text lemmatization
- `get_text_statistics()` - Statistics

### Segmentation Module

**Input:** Raw text string

**Processes:**
1. **Sentence Segmentation**
   - Identifies sentence boundaries
   - Handles abbreviations (Dr., Mrs., etc.)
   - Manages edge cases

2. **Word Segmentation**
   - Extracts words using regex
   - Handles contractions
   - Lowercase normalization

3. **Tokenization**
   - Detailed token analysis
   - Position tracking
   - Punctuation detection
   - Stopword identification

**Output:** Structured segmentation data

### Morphology Module

**Input:** Word(s)

**Processes:**
1. **Affix Analysis**
   - Prefix identification
   - Suffix identification
   - Root extraction

2. **Lemmatization**
   - Base form conversion
   - Irregular form handling
   - Rule-based processing

3. **POS Inference**
   - Part-of-speech inference from morphology
   - Multiple possibilities

**Output:** Morphological analysis data

### Database Manager

**Responsibilities:**
- Connection management
- Query execution
- Transaction handling
- Error recovery
- Connection pooling

**Database Schema:**

```
morphemes
├── id (PK)
├── morpheme
├── type (prefix/suffix/root)
├── meaning
└── language

word_analysis
├── id (PK)
├── word
├── root
├── prefix
├── suffix
├── pos_tag
└── lemma

text_segments
├── id (PK)
├── original_text
├── sentence_count
└── word_count

sentences
├── id (PK)
├── text_segment_id (FK)
├── sentence_text
├── sentence_position
└── word_count

tokens
├── id (PK)
├── sentence_id (FK)
├── token
├── token_position
├── is_punctuation
└── is_stopword
```

## Data Flow Example

```
Input: "The children were running quickly."

Step 1: Segmentation
  ├─> Sentences: ["The children were running quickly."]
  ├─> Words: ["the", "children", "were", "running", "quickly"]
  └─> Tokens: [
        {"text": "The", "pos": 0, "is_stopword": true},
        {"text": "children", "pos": 1, "is_stopword": false},
        ...
      ]

Step 2: Morphology
  ├─> "children"
  │   ├─> Lemma: "child"
  │   ├─> Type: irregular plural
  │   └─> Root: "child"
  │
  ├─> "running"
  │   ├─> Lemma: "run"
  │   ├─> Root: "run"
  │   ├─> Suffix: "ing"
  │   └─> POS: ["verb", "noun"]
  │
  └─> "quickly"
      ├─> Lemma: "quickly"
      ├─> Root: "quick"
      ├─> Suffix: "ly"
      └─> POS: ["adverb"]

Step 3: Storage (Optional)
  └─> Database: Insert into respective tables

Step 4: Return Results
  └─> User: Complete analysis object
```

## Scalability Features

### 1. Modular Design
- Each component is independent
- Easy to extend or replace
- Clear interfaces

### 2. Database-Backed
- Persistent storage
- Efficient querying
- Historical analysis

### 3. Batch Processing
- Process multiple items efficiently
- Reduced database calls
- Optimized queries

### 4. Configuration-Based
- Easy environment switching
- Flexible settings
- Environment-specific configs

## Extension Points

### Adding New Modules

```python
# modules/your_module.py
class YourModule:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
    
    def process(self, data):
        # Your logic here
        pass
```

### Registering in Main System

```python
# nlu_system.py
class NLUSystem:
    def __init__(self, db_config):
        # ... existing code ...
        self.your_module = YourModule(db_manager=self.db_manager)
```

## Performance Considerations

1. **Database Indexing**
   - Index frequently queried columns
   - Composite indexes for complex queries

2. **Connection Pooling**
   - Reuse connections
   - Minimize connection overhead

3. **Caching**
   - Cache frequent analyses
   - Reduce redundant processing

4. **Batch Operations**
   - Group database operations
   - Use bulk inserts

## Future Expansion Roadmap

```
Current: Segmentation + Morphology
    │
    ├─> Phase 2: Syntax Analysis
    │   ├─> POS Tagging
    │   ├─> Dependency Parsing
    │   └─> Constituency Parsing
    │
    ├─> Phase 3: Semantic Analysis
    │   ├─> Named Entity Recognition
    │   ├─> Word Sense Disambiguation
    │   └─> Semantic Role Labeling
    │
    └─> Phase 4: Pragmatic Analysis
        ├─> Sentiment Analysis
        ├─> Intent Detection
        └─> Context Understanding
```

## Error Handling Strategy

```
User Request
    │
    ▼
Try:
    Process Request
    │
    └─> Success: Return Results
    
Except Database Error:
    │
    ├─> Log Error
    ├─> Rollback Transaction
    └─> Return Error Message

Except Processing Error:
    │
    ├─> Log Error
    ├─> Return Partial Results (if any)
    └─> Inform User

Finally:
    │
    └─> Cleanup Resources
```

## Logging Structure

```
INFO  - System initialization
INFO  - Module loading
DEBUG - Processing steps
WARN  - Unusual patterns
ERROR - Processing failures
```
