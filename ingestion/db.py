"""
Ingestion - Chargement des données CSV vers PostgreSQL
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import StaticPool

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

def get_engine():
    """Crée une connexion SQLAlchemy"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            engine = create_engine(database_url, echo=False)
        else:
            engine = create_engine(
                URL.create(
                    "postgresql+psycopg2",
                    username=os.getenv("DB_USER", os.getenv("POSTGRES_USER")),
                    password=os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD")),
                    host=os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "localhost")),
                    port=int(os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))),
                    database=os.getenv("DB_NAME", os.getenv("POSTGRES_DB")),
                ),
                echo=False,
            )
        return engine
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None


def test_connection():
    """Teste la connexion à la base de données"""
    engine = get_engine()
    if engine:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✓ Connexion PostgreSQL établie")
                return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    return False


if __name__ == "__main__":
    test_connection()
