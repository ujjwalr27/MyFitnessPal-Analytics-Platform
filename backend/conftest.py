import pytest
import os
import sys
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.db_client import init_db
from backend.app import app

@pytest.fixture(scope="session")
def test_app():
    app.config['TESTING'] = True
    return app

@pytest.fixture(scope="session")
def test_db():
    """Set up a test database."""
    # Use environment variables or default to test values
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'ujjwal')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'myfitnessdb_test')
    
    # Create connection string
    conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Create engine
    engine = create_engine(conn_string)
    
    # Create tables
    with app.app_context():
        init_db()
    
    yield engine
    
    # Clean up after tests
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS fitness_data"))
        conn.commit() 