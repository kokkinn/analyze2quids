import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.sqlalchemy.models import Base

host: str = 'localhost'
db_name: str = 'analyze2quids'
port = 3306
username: str = 'root'
password: str = ''

engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()
