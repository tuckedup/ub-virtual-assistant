# run_chatbot.py
"""
Easy setup and run script for UB Chatbot
Run this file to start the chatbot with all components
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['fastapi', 'uvicorn', 'sqlalchemy', 'requests', 'beautifulsoup4']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("📦 Installing missing packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed!")
    else:
        print("✅ All dependencies are installed!")

def setup_database():
    """Initialize database if not exists"""
    db_file = Path("ub_courses.db")
    
    if not db_file.exists():
        print("🗄️ Setting up database...")
        
        # Run models.py to create tables
        subprocess.run([sys.executable, "models.py"])
        
        # Check if CSV files exist
        if Path("courses.csv").exists() and Path("offerings.csv").exists():
            print("📊 Loading data from CSV files...")
            subprocess.run([sys.executable, "load_data.py"])
        else:
            print("⚠️ CSV files not found. Creating sample data...")
            create_sample_data()
            subprocess.run([sys.executable, "load_data.py"])
    else:
        print("✅ Database already exists!")

def create_sample_data():
    """Create sample CSV files if they don't exist"""
    
    # Sample courses
    courses_data = """course_id,title,description,credits,department,level
CSE 115,Introduction to Computer Science I,Introduction to algorithm design and implementation in a modern programming language.,4,CSE,UG
CSE 116,Introduction to Computer Science II,Continuation of CSE 115. Data structures and algorithms.,4,CSE,UG
CSE 191,Introduction to Discrete Structures,Discrete mathematics for computer science.,4,CSE,UG
CSE 220,Systems Programming,Introduction to systems programming in C and assembly.,3,CSE,UG
CSE 250,Data Structures,Advanced data structures and their analysis.,3,CSE,UG
CSE 341,Computer Organization,Computer architecture and organization.,4,CSE,UG
CSE 442,Software Engineering,Principles and practices of software engineering.,3,CSE,UG
CSE 468,Robotics Algorithms,Algorithms for robotics applications.,3,CSE,UG
CSE 474,Machine Learning,Introduction to machine learning algorithms and applications.,3,CSE,UG
CSE 486,Distributed Systems,Principles of distributed computing systems.,3,CSE,UG
CSE 521,Operating Systems,Design and implementation of operating systems.,3,CSE,GR
CSE 531,Algorithm Analysis and Design,Advanced algorithm design and complexity analysis.,3,CSE,GR
CSE 535,Information Retrieval,Text processing and search engine design.,3,CSE,GR
CSE 540,Machine Learning,Graduate-level machine learning.,3,CSE,GR
CSE 573,Computer Vision,Image processing and computer vision algorithms.,3,CSE,GR
MTH 141,College Calculus I,Limits derivatives and integrals of functions of one variable.,4,MTH,UG
MTH 142,College Calculus II,Techniques of integration and infinite series.,4,MTH,UG
MTH 241,College Calculus III,Multivariable calculus.,4,MTH,UG
MTH 309,Linear Algebra,Vector spaces and linear transformations.,4,MTH,UG
PHY 107,General Physics I,Mechanics heat and sound.,4,PHY,UG"""
    
    # Sample offerings
    offerings_data = """term,course_id,section,instructor,days,start_time,end_time,room,campus,modality
2025-01,CSE 115,LEC A,Carl Alphonce,MWF,09:00,09:50,Norton 112,North Campus,In Person
2025-01,CSE 115,LEC B,Carl Alphonce,MWF,10:00,10:50,Norton 112,North Campus,In Person
2025-01,CSE 116,LEC A,Matthew Hertz,TR,14:00,15:20,NSC 201,North Campus,In Person
2025-01,CSE 191,LEC A,Jaric Zola,MWF,11:00,11:50,Knox 109,North Campus,In Person
2025-01,CSE 220,LEC A,Ethan Blanton,TR,09:30,10:50,Davis 101,North Campus,In Person
2025-01,CSE 250,LEC A,Andrew Hughes,MWF,13:00,13:50,Cooke 121,North Campus,In Person
2025-01,CSE 474,LEC A,Sargur Srihari,TR,17:00,18:20,Knox 110,North Campus,In Person
2025-01,CSE 486,LEC A,Steven Ko,MWF,15:00,15:50,Bell 138,North Campus,In Person
2025-01,CSE 531,LEC A,Shi Li,TR,12:30,13:50,Capen 260,North Campus,In Person
2025-01,CSE 540,LEC A,Varun Chandola,MW,17:00,18:20,Knox 20,North Campus,In Person
2025-01,MTH 141,LEC A,John Doe,MTWRF,08:00,08:50,Math 250,North Campus,In Person
2025-01,MTH 142,LEC A,Jane Smith,MTWRF,09:00,09:50,Math 250,North Campus,In Person
2025-01,PHY 107,LEC A,Physics Staff,MWF,10:00,10:50,Fronczak 422,North Campus,In Person"""
    
    with open("courses.csv", "w") as f:
        f.write(courses_data)
    
    with open("offerings.csv", "w") as f:
        f.write(offerings_data)
    
    print("✅ Sample CSV files created!")

def scrape_real_data():
    """Optionally scrape real UB data"""
    response = input("\n🌐 Do you want to try scraping real UB course data? (y/n): ").lower()
    
    if response == 'y':
        print("🕷️ Starting web scraper...")
        print("Note: This will take a few minutes and may not get all data.")
        
        try:
            subprocess.run([sys.executable, "scrape_ub.py"])
            
            # Reload data if scraping was successful
            if Path("ub_courses_real.csv").exists():
                print("📊 Loading scraped data...")
                # You'd need to modify load_data.py to use the new files
                subprocess.run([sys.executable, "load_data.py"])
        except Exception as e:
            print(f"⚠️ Scraping failed: {e}")
            print("Continuing with sample data...")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting UB Chatbot server...")
    print("=" * 50)
    print("📌 Server will run at: http://localhost:8000")
    print("📌 API docs available at: http://localhost:8000/docs")
    print("📌 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Wait a bit then open browser
    time.sleep(2)
    webbrowser.open("http://localhost:8000")
    
    # Start uvicorn
    subprocess.run(["uvicorn", "api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

def main():
    """Main setup and run function"""
    print("""
    ╔══════════════════════════════════════════╗
    ║      🎓 UB Chatbot Setup & Launch 🎓      ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required!")
        sys.exit(1)
    
    # Setup steps
    check_dependencies()
    setup_database()
    
    # Optional: scrape real data
    scrape_real_data()
    
    # Create templates directory if it doesn't exist
    Path("templates").mkdir(exist_ok=True)
    
    # Check if API key is set (optional)
    if not os.getenv("OPENAI_API_KEY"):
        print("\n💡 Tip: Set OPENAI_API_KEY in .env file for AI-enhanced responses")
        print("   The chatbot will work without it using rule-based responses.")
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()