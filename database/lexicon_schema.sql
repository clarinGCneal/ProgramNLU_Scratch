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
