from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
vacancy_technologies = Table('vacancy_technologies',
                             Base.metadata,
                             Column("framework_id", Integer, ForeignKey('framework.id')),
                             Column("vacancy_id", Integer, ForeignKey('vacancy.id')))


class Framework(Base):
	__tablename__ = "framework"
	id = Column(Integer, primary_key=True)
	framework_name = Column(String, unique=True, nullable=True)


class Vacancy(Base):
	__tablename__ = "vacancy"
	id = Column(Integer, primary_key=True)
	vacancy_name = Column(String)
	experience = Column(Integer)
	lvl = Column(String, default="junior")
	views = Column(Integer)
	applications = Column(Integer)
	part_of_url = Column(String)
	frameworks = relationship("Framework", secondary=vacancy_technologies, backref="vac_frame")


engine = create_engine('sqlite:///djinni.db', echo=True)
Base.metadata.drop_all(engine)  # drop all you can turn off and cleanup the database
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
