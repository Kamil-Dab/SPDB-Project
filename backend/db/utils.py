from typing import Dict


def get_postgres_uri(db: Dict[str, str]) -> str:
    host = db["db_host"]
    port = db["db_port"]
    db_name = db["db_name"]
    user = db["db_user"]
    password = db["db_password"]
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
