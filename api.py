# api.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict
import openai
import os
from dotenv import load_dotenv
from rag import query_rag
from datetime import datetime
import json

# Import your database queries
from queries import get_course_offerings
from models import SessionLocal, Course, CourseOffering

# Load environment variables
load_dotenv()

app = FastAPI(title="UB Chatbot API", version="1.0.0")

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI (optional - for enhanced responses)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    data: Optional[Dict] = None

class CourseQuery(BaseModel):
    term: Optional[str] = None
    subject: Optional[str] = None
    level: Optional[str] = None
    course_id: Optional[str] = None
    instructor: Optional[str] = None

# Store conversation history (in production, use Redis or database)
conversations = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a simple HTML interface"""
    index_path = Path(__file__).parent / "templates" / "index.html"
    html = index_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html)

@app.get("/api/courses")
async def get_courses(
    subject: Optional[str] = Query(None, description="Department code (e.g., CSE)"),
    level: Optional[str] = Query(None, description="Course level (UG or GR)"),
    search: Optional[str] = Query(None, description="Search term for course title/description")
):
    """Get list of courses with optional filters"""
    db = SessionLocal()
    try:
        query = db.query(Course)
        
        if subject:
            query = query.filter(Course.department == subject.upper())
        if level:
            query = query.filter(Course.level == level.upper())
        if search:
            query = query.filter(
                (Course.title.contains(search)) | 
                (Course.description.contains(search))
            )
        
        courses = query.all()
        
        return [{
            "course_id": c.course_id,
            "title": c.title,
            "description": c.description,
            "credits": c.credits,
            "department": c.department,
            "level": c.level
        } for c in courses]
        
    finally:
        db.close()

@app.get("/api/offerings")
async def get_offerings(
    term: str = Query(..., description="Term (e.g., 2025-01 for Spring 2025)"),
    subject: Optional[str] = Query(None, description="Department code"),
    level: Optional[str] = Query(None, description="Course level"),
    instructor: Optional[str] = Query(None, description="Instructor name"),
    days: Optional[str] = Query(None, description="Days (e.g., MWF, TR)")
):
    """Get course offerings for a specific term"""
    offerings = get_course_offerings(term, subject, level)
    
    # Additional filtering
    if instructor:
        offerings = [o for o in offerings if instructor.lower() in o['instructor'].lower()]
    if days:
        offerings = [o for o in offerings if days in o['days']]
    
    return offerings

@app.post("/api/chat")
async def chat(message: ChatMessage) -> ChatResponse:
    """Process chat messages and return responses"""
    
    # Generate session ID if not provided
    if not message.session_id:
        message.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Store conversation
    if message.session_id not in conversations:
        conversations[message.session_id] = []
    
    conversations[message.session_id].append({
        "role": "user",
        "content": message.message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Process the message
    response_text, data = process_message(message.message)
    
    # Store bot response
    conversations[message.session_id].append({
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.now().isoformat()
    })
    
    return ChatResponse(
        response=response_text,
        session_id=message.session_id,
        data=data
    )

def process_message(user_message: str) -> tuple[str, Optional[Dict]]:
    """
    Process user message and generate response.
    Returns (response_text, optional_data)
    """
    user_message_lower = user_message.lower()
    
    # Intent detection
    if any(word in user_message_lower for word in ['course', 'class', 'offering', 'schedule']):
        return handle_course_query(user_message)
    elif any(word in user_message_lower for word in ['register', 'enrollment', 'add', 'drop']):
        return handle_registration_query(user_message)
    elif any(word in user_message_lower for word in ['grade', 'gpa', 'transcript']):
        return handle_grades_query(user_message)
    elif any(word in user_message_lower for word in ['tuition', 'fee', 'cost', 'financial']):
        return handle_financial_query(user_message)
    elif any(word in user_message_lower for word in ['building', 'campus', 'library', 'dining']):
        return handle_campus_query(user_message)
    else:
        # Use LLM for general queries if API key is available
        if openai.api_key:
            return handle_general_query_with_llm(user_message)
        else:
            return handle_general_query(user_message)

def handle_course_query(message: str) -> tuple[str, Optional[Dict]]:
    """Handle course-related queries"""
    
    # Extract entities from message
    import re
    
    # Try to find course codes (e.g., CSE 115)
    course_pattern = r'\b([A-Z]{2,4})\s+(\d{3})\b'
    course_matches = re.findall(course_pattern, message.upper())
    
    # Extract term
    term = None
    if 'spring' in message.lower():
        if '2025' in message:
            term = '2025-01'
        elif '2024' in message:
            term = '2024-01'
    elif 'fall' in message.lower():
        if '2025' in message:
            term = '2025-09'
        elif '2024' in message:
            term = '2024-09'
    
    # If specific course mentioned
    if course_matches:
        dept, num = course_matches[0]
        course_id = f"{dept} {num}"
        
        # Get course info from database
        db = SessionLocal()
        try:
            course = db.query(Course).filter(Course.course_id == course_id).first()
            if course:
                response = f"**{course.course_id} - {course.title}**\n\n"
                response += f"Credits: {course.credits}\n"
                response += f"Level: {'Graduate' if course.level == 'GR' else 'Undergraduate'}\n"
                response += f"Description: {course.description}\n"
                
                # Check for offerings
                if term:
                    offerings = db.query(CourseOffering).filter(
                        CourseOffering.course_id == course_id,
                        CourseOffering.term == term
                    ).all()
                    
                    if offerings:
                        response += f"\n**Offerings for {term}:**\n"
                        for off in offerings:
                            response += f"- Section {off.section}: {off.days} {off.start_time}-{off.end_time}"
                            response += f" with {off.instructor} in {off.room}\n"
                
                return response, {"course": course_id, "found": True}
            else:
                return f"I couldn't find information about {course_id}. Please check the course code.", None
        finally:
            db.close()
    
    # General course search
    if 'computer science' in message.lower() or 'cse' in message.lower():
        db = SessionLocal()
        try:
            courses = db.query(Course).filter(Course.department == 'CSE').limit(5).all()
            if courses:
                response = "Here are some Computer Science courses:\n\n"
                for c in courses:
                    response += f"• **{c.course_id}**: {c.title} ({c.credits} credits)\n"
                return response, {"department": "CSE"}
        finally:
            db.close()
    
    return "Could you please specify which course or department you're interested in?", None

def handle_registration_query(message: str) -> tuple[str, str]:
    """Handle registration-related queries"""
    response = """**Registration Information:**

**Important Dates:**
- Registration for Spring 2025 opens: November 1, 2024
- Add/Drop deadline: First week of classes
- Course withdrawal deadline: Week 11 of semester

**How to Register:**
1. Log into HUB Student Center
2. Click on "Enroll" under Academics
3. Select the term
4. Search for classes and add to shopping cart
5. Proceed to enrollment

**Need help?** Contact the Registrar's Office at (716) 645-5698 or visit 1Capen."""
    
    return response, None

def handle_grades_query(message: str) -> tuple[str, str]:
    """Handle grades/GPA queries"""
    response = """**Academic Records & Grades:**

**Accessing Your Grades:**
- Log into HUB Student Center
- Click "Grades" under Academics
- Select the term to view

**GPA Information:**
- UB uses a 4.0 scale
- A=4.0, A-=3.67, B+=3.33, B=3.0, B-=2.67
- C+=2.33, C=2.0, C-=1.67, D=1.0, F=0.0

**Transcripts:**
- Official transcripts: Order through HUB ($10 fee)
- Unofficial transcripts: Available free in HUB

For specific grade inquiries, please log into HUB or contact your academic advisor."""
    
    return response, None

def handle_financial_query(message: str) -> tuple[str, str]:
    """Handle financial aid/tuition queries"""
    response = """**Financial Information:**

**2024-2025 Tuition Rates:**
- NY Resident Undergraduate: $7,070/semester
- Non-Resident Undergraduate: $12,730/semester
- Graduate rates vary by program

**Financial Aid:**
- FAFSA Priority Deadline: February 1
- Visit Student Accounts at 1Capen
- Call: (716) 645-8000
- Email: studentaccounts@buffalo.edu

**Scholarships:**
- Check ScholarshipUniverse on HUB
- Department-specific scholarships available
- Merit-based aid automatically considered

For personalized financial aid info, please log into HUB."""
    
    return response, None

def handle_campus_query(message: str) -> tuple[str, str]:
    """Handle campus services queries"""
    response = """**Campus Services & Locations:**

**Libraries:**
- Lockwood Memorial Library (North Campus)
- Health Sciences Library (South Campus)
- Law Library (North Campus)

**Dining:**
- Student Union (North) - Multiple options
- Ellicott Complex - C3, Hubies
- Governors Complex - Dining center

**Parking:**
- Permits required Mon-Fri, 7am-5pm
- Student permits: $250/year
- Daily permits available at kiosks

**Student Services:**
- One Stop (1Capen) - All student services
- Career Services (259 Capen)
- Health Services (Michael Hall)

What specific campus service are you looking for?"""
    
    return response, None

def handle_general_query(message: str) -> tuple[str, str]:
    """Handle general queries without LLM"""
    response = """I'm the UB Virtual Assistant. I can help you with:

• **Course Information** - Search courses, check prerequisites
• **Registration** - Enrollment dates, how to register
• **Academic Calendar** - Important dates, deadlines
• **Campus Services** - Dining, libraries, parking
• **Financial Aid** - Tuition, scholarships, payment

What would you like to know about?

For urgent matters, contact:
- Student Response Center: (716) 645-2450
- Email: ub-help@buffalo.edu"""
    
    return response, None

def handle_general_query_with_llm(message: str) -> tuple[str, Optional[Dict]]:
    """Use LLM for enhanced responses"""
    try:
        # Get context from database if relevant
        context = get_relevant_context(message)
        
        # Create prompt
        system_prompt = """You are a helpful University at Buffalo (UB) virtual assistant. 
        You help students, faculty, and staff with academic and campus-related questions.
        Be friendly, concise, and accurate. If you don't know something specific to UB,
        suggest contacting the Student Response Center at (716) 645-2450."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        if context:
            messages[0]["content"] += f"\n\nContext:\n{context}"
        
        # Call OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content, None
        
    except Exception as e:
        print(f"LLM Error: {e}")
        return handle_general_query(message)

def get_relevant_context(message: str) -> str:
    """Get relevant context from DB + RAG for LLM."""
    context_parts = []

    # ---- 1) DB context (existing course search) ----
    db = SessionLocal()
    try:
        keywords = message.lower().split()

        for keyword in keywords:
            if len(keyword) <= 3:
                continue

            courses = db.query(Course).filter(
                (Course.title.ilike(f"%{keyword}%")) |
                (Course.description.ilike(f"%{keyword}%"))
            ).limit(3).all()

            for course in courses:
                context_parts.append(
                    f"{course.course_id}: {course.title} "
                    f"({course.credits} credits) - {course.description[:200]}"
                )
    finally:
        db.close()

    # ---- 2) RAG context from JSON knowledge base ----
    rag_context = query_rag(message)
    if rag_context:
        context_parts.append("UB Knowledge Base:\n" + rag_context)

    return "\n\n".join(context_parts)


@app.get("/api/stats")
async def get_stats():
    """Get chatbot usage statistics"""
    db = SessionLocal()
    try:
        total_courses = db.query(Course).count()
        total_offerings = db.query(CourseOffering).count()
        departments = db.query(Course.department).distinct().count()
        
        return {
            "total_courses": total_courses,
            "total_offerings": total_offerings,
            "departments": departments,
            "active_sessions": len(conversations)
        }
    finally:
        db.close()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
