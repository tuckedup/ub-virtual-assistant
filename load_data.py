# load_data.py
import csv
from sqlalchemy.orm import Session
from models import Course, CourseOffering, init_db, get_engine

DB_URL = "sqlite:///ub_courses.db"

def load_courses(csv_path: str):
    engine = get_engine(DB_URL)
    init_db(DB_URL)

    with Session(engine) as session:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                course = session.query(Course).filter_by(course_id=row["course_id"]).one_or_none()
                if course is None:
                    course = Course(
                        course_id=row["course_id"].strip(),
                        title=row["title"].strip(),
                        description=row.get("description", "").strip(),
                        credits=float(row.get("credits", 0) or 0),
                        department=row.get("department", "").strip(),
                        level=row.get("level", "").strip(),
                    )
                    session.add(course)
            session.commit()
    print("Loaded courses from", csv_path)

def load_offerings(csv_path: str):
    engine = get_engine(DB_URL)
    init_db(DB_URL)

    with Session(engine) as session:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                offering = CourseOffering(
                    term=row["term"].strip(),
                    course_id=row["course_id"].strip(),
                    section=row.get("section", "").strip(),
                    instructor=row.get("instructor", "").strip(),
                    days=row.get("days", "").strip(),
                    start_time=row.get("start_time", "").strip(),
                    end_time=row.get("end_time", "").strip(),
                    room=row.get("room", "").strip(),
                    campus=row.get("campus", "").strip(),
                    modality=row.get("modality", "").strip(),
                )
                session.add(offering)
            session.commit()
    print("Loaded offerings from", csv_path)

if __name__ == "__main__":
    load_courses("courses.csv")
    load_offerings("offerings.csv")
