"""
Database Setup Script
Initializes the NLU System database with schema
"""

from nlu_system import NLUSystem
from config import DB_CONFIG
import sys


def setup_database():
    """Setup and initialize the database"""
    print("=" * 60)
    print("NLU SYSTEM - DATABASE SETUP")
    print("=" * 60)
    
    print("\nDatabase Configuration:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Port: {DB_CONFIG['port']}")
    
    # Confirm
    response = input("\nProceed with database initialization? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Setup cancelled.")
        return
    
    try:
        print("\nConnecting to database...")
        nlu = NLUSystem(DB_CONFIG)
        
        print("Initializing database schema...")
        nlu.initialize_database('database/schema.sql')
        
        print("\n✓ Database initialized successfully!")
        
        # Verify setup
        print("\nVerifying setup...")
        
        # Check morphemes
        morphemes = nlu.db_manager.fetch_all("SELECT COUNT(*) as count FROM morphemes")
        print(f"  Morphemes loaded: {morphemes[0]['count']}")
        
        # Test insertion
        print("\nTesting database operations...")
        test_id = nlu.db_manager.insert_one('text_segments', {
            'original_text': 'Test sentence.',
            'sentence_count': 1,
            'word_count': 2
        })
        
        if test_id:
            print(f"  ✓ Insert test passed (ID: {test_id})")
            
            # Clean up test
            nlu.db_manager.execute_query(f"DELETE FROM text_segments WHERE id = {test_id}")
            print(f"  ✓ Delete test passed")
        
        print("\n" + "=" * 60)
        print("DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print("\nYou can now run:")
        print("  python examples.py        # Run example analyses")
        print("  python test_modules.py    # Run module tests")
        
        nlu.close()
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nPlease check:")
        print("  1. MySQL server is running")
        print("  2. Database credentials in config.py are correct")
        print("  3. User has proper privileges")
        print("  4. Database exists (or create it first)")
        sys.exit(1)


if __name__ == "__main__":
    setup_database()
