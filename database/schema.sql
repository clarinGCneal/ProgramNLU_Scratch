-- NLU System Database Schema

-- Table for storing morpheme dictionary (roots, prefixes, suffixes)
CREATE TABLE IF NOT EXISTS morphemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    morpheme VARCHAR(100) NOT NULL,
    type ENUM('root', 'prefix', 'suffix', 'infix') NOT NULL,
    meaning TEXT,
    language VARCHAR(10) DEFAULT 'en',
    frequency INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_morpheme (morpheme),
    INDEX idx_type (type)
);

-- Table for word forms and their morphological analysis
CREATE TABLE IF NOT EXISTS word_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(200) NOT NULL,
    root VARCHAR(100),
    prefix VARCHAR(100),
    suffix VARCHAR(100),
    pos_tag VARCHAR(20),
    lemma VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_word (word),
    INDEX idx_root (root)
);

-- Table for storing processed texts and their segmentation
CREATE TABLE IF NOT EXISTS text_segments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_text TEXT NOT NULL,
    sentence_count INT,
    word_count INT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_processed_at (processed_at)
);

-- Table for individual sentences
CREATE TABLE IF NOT EXISTS sentences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text_segment_id INT,
    sentence_text TEXT NOT NULL,
    sentence_position INT,
    word_count INT,
    FOREIGN KEY (text_segment_id) REFERENCES text_segments(id) ON DELETE CASCADE,
    INDEX idx_text_segment (text_segment_id)
);

-- Table for tokens from segmentation
CREATE TABLE IF NOT EXISTS tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sentence_id INT,
    token VARCHAR(200) NOT NULL,
    token_position INT,
    is_punctuation BOOLEAN DEFAULT FALSE,
    is_stopword BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (sentence_id) REFERENCES sentences(id) ON DELETE CASCADE,
    INDEX idx_sentence (sentence_id),
    INDEX idx_token (token)
);

-- Table for morphological rules
CREATE TABLE IF NOT EXISTS morphology_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    pattern VARCHAR(255) NOT NULL,
    transformation VARCHAR(255),
    rule_type ENUM('inflection', 'derivation', 'compound') NOT NULL,
    priority INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_rule_type (rule_type),
    INDEX idx_priority (priority)
);

-- Insert some common English morphemes
INSERT INTO morphemes (morpheme, type, meaning) VALUES
('un', 'prefix', 'not, opposite of'),
('re', 'prefix', 'again, back'),
('pre', 'prefix', 'before'),
('post', 'prefix', 'after'),
('anti', 'prefix', 'against'),
('dis', 'prefix', 'not, opposite'),
('ed', 'suffix', 'past tense'),
('ing', 'suffix', 'present participle'),
('ly', 'suffix', 'adverb marker'),
('ness', 'suffix', 'state or quality'),
('tion', 'suffix', 'action or process'),
('able', 'suffix', 'capable of'),
('less', 'suffix', 'without'),
('ful', 'suffix', 'full of');

-- Additional schema for Lexicon support

-- Table for lexical entries
CREATE TABLE IF NOT EXISTS lexicon (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    pos VARCHAR(20) NOT NULL,
    lemma VARCHAR(100) NOT NULL,
    frequency INT DEFAULT 0,
    features TEXT,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_word (word),
    INDEX idx_pos (pos),
    INDEX idx_lemma (lemma),
    INDEX idx_frequency (frequency),
    UNIQUE KEY unique_word_pos (word, pos)
);

-- Table for grammar rules (CFG)
CREATE TABLE IF NOT EXISTS grammar_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lhs VARCHAR(50) NOT NULL,
    rhs TEXT NOT NULL,
    probability FLOAT DEFAULT 1.0,
    grammar_name VARCHAR(100) DEFAULT 'default',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_lhs (lhs),
    INDEX idx_grammar (grammar_name)
);

-- Table for parse trees (store parsing results)
CREATE TABLE IF NOT EXISTS parse_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sentence TEXT NOT NULL,
    parse_tree TEXT NOT NULL,
    parser_type VARCHAR(50),
    parse_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
);