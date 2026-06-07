import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/estudo_on"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_sqlalchemy_session():
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.close()
        raise e


def get_psycopg2_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar via psycopg2: {e}")
        raise e

