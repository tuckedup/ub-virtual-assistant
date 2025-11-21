# queries.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Course, CourseOffering, get_engine

DB_URL = "sqlite:///ub_courses.db"
engine = get_engine(DB_URL)

def get_course_offerings(
    term: str,
    subject: Optional[str] = None,    # e.g., "CSE"
    level: Optional[str] = None,      # "UG" or "GR"
) -> List[dict]:
    """
    Returns list of offerings for a given term, optionally filtered by subject/level.
    """
    with Session(engine) as session:
        q = session.query(CourseOffering, Course).join(Course, CourseOffering.course_id == Course.course_id)
        q = q.filter(CourseOffering.term == term)

        if subject:
            q = q.filter(Course.department == subject)

        if level:
            q = q.filter(Course.level == level)

        results = []
        for off, course in q.all():
            results.append(
                {
                    "course_id": course.course_id,
                    "title": course.title,
                    "description": course.description,
                    "credits": course.credits,
                    "department": course.department,
                    "level": course.level,
                    "term": off.term,
                    "section": off.section,
                    "instructor": off.instructor,
                    "days": off.days,
                    "start_time": off.start_time,
                    "end_time": off.end_time,
                    "room": off.room,
                    "campus": off.campus,
                    "modality": off.modality,
                }
            )
        return results

if __name__ == "__main__":
    # Example: "What CSE grad courses are offered in Fall 2025?"
    offerings = get_course_offerings(term="2025-09", subject="CSE", level="GR")
    for o in offerings:
        print(
            f'{o["course_id"]} - {o["title"]} ({o["section"]}) {o["days"]} {o["start_time"]}-{o["end_time"]} '
            f'with {o["instructor"]} in {o["room"]}'
        )