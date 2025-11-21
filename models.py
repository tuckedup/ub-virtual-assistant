# models.py
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String, unique=True, index=True)  # e.g., "CSE 574"
    title = Column(String, nullable=False)
    description = Column(String)
    credits = Column(Float)
    department = Column(String)       # e.g., "CSE"
    level = Column(String)            # e.g., "UG", "GR"

    offerings = relationship("CourseOffering", back_populates="course")

class CourseOffering(Base):
    __tablename__ = "course_offerings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # ex: "2025-09" or UB term code "2259" – your choice, just be consistent
    term = Column(String, index=True)  

    course_id = Column(String, ForeignKey("courses.course_id"), index=True)
    section = Column(String)          # e.g., "A", "LEC 1", "SEM 1"
    instructor = Column(String)
    days = Column(String)             # e.g., "MWF", "TR"
    start_time = Column(String)       # e.g., "10:00"
    end_time = Column(String)         # e.g., "10:50"
    room = Column(String)             # e.g., "Knox 109"
    campus = Column(String)           # e.g., "North Campus"
    modality = Column(String)         # e.g., "In Person", "Online"

    course = relationship("Course", back_populates="offerings")

    __table_args__ = (
        # Avoid duplicate offerings for the same term/course/section
        UniqueConstraint("term", "course_id", "section", name="uq_offering"),
    )


def get_engine(db_url: str = "sqlite:///ub_courses.db"):
    return create_engine(db_url, echo=False, future=True)


def init_db(db_url: str = "sqlite:///ub_courses.db"):
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    return engine


SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)

if __name__ == "__main__":
    init_db()
    print("DB initialized")
