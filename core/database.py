"""
Database Manager for NLU System
Handles all database connections and operations
"""

import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MySQL database connections and operations"""
    
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        """
        Initialize database manager
        
        Args:
            host: Database host
            user: Database user
            password: Database password
            database: Database name
            port: Database port (default 3306)
        """
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port
        }
        self._connection = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self._connection = mysql.connector.connect(**self.config)
            if self._connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return True
            return False
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            logger.info("MySQL connection closed")
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """
        Context manager for database cursor
        
        Args:
            dictionary: Return results as dictionaries (default True)
        """
        if not self._connection or not self._connection.is_connected():
            raise Error("Database connection not established. Call connect() first.")
        
        cursor = self._connection.cursor(dictionary=dictionary)
        try:
            yield cursor
            self._connection.commit()
        except Error as e:
            self._connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> bool:
        """
        Execute a query without returning results
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            Success status
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return True
        except Error as e:
            logger.error(f"Query execution failed: {e}")
            return False
    
    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch single result
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            Single result as dictionary or None
        """
        try:
            with self.get_cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                return result  # type: ignore[return-value]
        except Error as e:
            logger.error(f"Fetch one failed: {e}")
            return None
    
    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Fetch all results
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            List of results as dictionaries
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()  # type: ignore[return-value]
        except Error as e:
            logger.error(f"Fetch all failed: {e}")
            return []
    
    def insert_one(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert single record
        
        Args:
            table: Table name
            data: Dictionary of column:value pairs
        
        Returns:
            Last insert ID or None
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, tuple(data.values()))
                return cursor.lastrowid
        except Error as e:
            logger.error(f"Insert failed: {e}")
            return None
    
    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> bool:
        """
        Insert multiple records
        
        Args:
            table: Table name
            data_list: List of dictionaries with column:value pairs
        
        Returns:
            Success status
        """
        if not data_list:
            return False
        
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['%s'] * len(data_list[0]))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            with self.get_cursor() as cursor:
                values = [tuple(data.values()) for data in data_list]
                cursor.executemany(query, values)
                return True
        except Error as e:
            logger.error(f"Bulk insert failed: {e}")
            return False
    
    def initialize_database(self, schema_file: str):
        """
        Initialize database with schema file
        
        Args:
            schema_file: Path to SQL schema file
        """
        try:
            with open(schema_file, 'r') as f:
                schema = f.read()
            
            # Split and execute statements
            statements = schema.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    self.execute_query(statement)
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    # ====================
    # Statistics Methods
    # ====================
    
    def get_table_counts(self) -> Dict[str, int]:
        """
        Get record counts for all main tables
        
        Returns:
            Dictionary with table names and their counts
        """
        counts = {}
        tables = ['text_segments', 'sentences', 'tokens', 'morphemes', 'word_analysis']
        
        for table in tables:
            result = self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
            counts[table] = result['count'] if result else 0
        
        return counts
    
    def get_recent_text_segments(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent text segments
        
        Args:
            limit: Number of records to retrieve
        
        Returns:
            List of text segment records
        """
        query = """
            SELECT id, LEFT(original_text, 50) as text_preview, 
                   sentence_count, word_count, processed_at
            FROM text_segments 
            ORDER BY processed_at DESC 
            LIMIT %s
        """
        return self.fetch_all(query, (limit,))
    
    def get_recent_sentences(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent sentences
        
        Args:
            limit: Number of records to retrieve
        
        Returns:
            List of sentence records
        """
        query = """
            SELECT id, LEFT(sentence_text, 50) as text, 
                   sentence_position, word_count
            FROM sentences 
            ORDER BY id DESC 
            LIMIT %s
        """
        return self.fetch_all(query, (limit,))
    
    def get_tokens_by_sentence(self, sentence_id: Optional[int] = None, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Get tokens from a specific sentence or the most recent one
        
        Args:
            sentence_id: Specific sentence ID (None for most recent)
            limit: Number of tokens to retrieve
        
        Returns:
            List of token records
        """
        if sentence_id is None:
            # Get most recent sentence
            query = """
                SELECT token, token_position, is_punctuation, is_stopword
                FROM tokens
                WHERE sentence_id = (SELECT MAX(id) FROM sentences)
                ORDER BY token_position
                LIMIT %s
            """
        else:
            query = """
                SELECT token, token_position, is_punctuation, is_stopword
                FROM tokens
                WHERE sentence_id = %s
                ORDER BY token_position
                LIMIT %s
            """
            return self.fetch_all(query, (sentence_id, limit))
        
        return self.fetch_all(query, (limit,))
    
    def get_recent_word_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent word analyses
        
        Args:
            limit: Number of records to retrieve
        
        Returns:
            List of word analysis records
        """
        query = """
            SELECT word, root, prefix, suffix, pos_tag, lemma
            FROM word_analysis
            ORDER BY id DESC
            LIMIT %s
        """
        return self.fetch_all(query, (limit,))
    
    # ====================
    # Clear/Delete Methods
    # ====================
    
    def clear_analysis_data(self) -> Dict[str, Any]:
        """
        Clear all analysis data (keeps morpheme dictionary)
        
        Returns:
            Dictionary with operation results
        """
        result = {
            'success': False,
            'deleted_counts': {},
            'error': None
        }
        
        try:
            with self.get_cursor(dictionary=True) as cursor:
                # Get counts before deletion
                tables = ['text_segments', 'sentences', 'tokens', 'word_analysis']
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    row = cursor.fetchone()
                    result['deleted_counts'][table] = row['count'] if row else 0  # type: ignore[index]
                
                # Delete in correct order (respecting foreign key constraints)
                cursor.execute("DELETE FROM tokens")
                cursor.execute("DELETE FROM word_analysis")
                cursor.execute("DELETE FROM sentences")
                cursor.execute("DELETE FROM text_segments")
                
                # Reset auto-increment counters
                cursor.execute("ALTER TABLE tokens AUTO_INCREMENT = 1")
                cursor.execute("ALTER TABLE word_analysis AUTO_INCREMENT = 1")
                cursor.execute("ALTER TABLE sentences AUTO_INCREMENT = 1")
                cursor.execute("ALTER TABLE text_segments AUTO_INCREMENT = 1")
                
                result['success'] = True
                logger.info("Analysis data cleared successfully")
                
        except Error as e:
            result['error'] = str(e)
            logger.error(f"Error clearing analysis data: {e}")
            if self._connection:
                self._connection.rollback()
        
        return result
    
    def get_morpheme_count(self) -> int:
        """
        Get count of morphemes in dictionary
        
        Returns:
            Number of morphemes
        """
        result = self.fetch_one("SELECT COUNT(*) as count FROM morphemes")
        return result['count'] if result else 0