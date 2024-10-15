from sqlalchemy import create_engine


def get_engine(host, user, password, database, port):
    engine = create_engine(
        f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')
    return engine
