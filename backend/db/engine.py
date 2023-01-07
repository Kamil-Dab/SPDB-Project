import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .utils import get_postgres_uri

LOCAL_DB = {
    "db_host": os.environ["DB_HOST"],
    "db_port": os.environ["DB_PORT"],
    "db_name": os.environ["DB_NAME"],
    "db_user": os.environ["DB_USER"],
    "db_password": os.environ["DB_PASSWORD"],
}

engine = create_engine(get_postgres_uri(LOCAL_DB))
get_session = sessionmaker(bind=engine)
