from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Cat(Base):
    __tablename__ = 'cats'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    experience = Column(Integer, nullable=False)
    breed = Column(String, nullable=False)
    salary = Column(Float, nullable=False)

    mission = relationship("Mission", back_populates="cat", uselist=False)


class Mission(Base):
    __tablename__ = 'missions'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_complete = Column(Boolean, default=False)

    cat_id = Column(Integer, ForeignKey('cats.id'), unique=True, nullable=True)
    cat = relationship("Cat", back_populates="mission")

    targets = relationship("Target", back_populates="mission", cascade="all, delete-orphan")


class Target(Base):
    __tablename__ = 'targets'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    notes = Column(String, default="")
    is_complete = Column(Boolean, default=False)

    mission_id = Column(Integer, ForeignKey('missions.id'))
    mission = relationship("Mission", back_populates="targets")
