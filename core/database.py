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
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
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
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Fetch single result
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            Single result as dictionary or None
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Fetch one failed: {e}")
            return None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
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
                return cursor.fetchall()
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
