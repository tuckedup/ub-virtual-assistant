import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from typing import Dict, List
import re

class UBCourseScraper:
    def __init__(self):
        self.base_url = "https://www.buffalo.edu/class-schedule"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def search_courses(self, term: str = "2025 Spring", subject: str = "CSE") -> List[Dict]:
        """
        Search for courses using UB's public class search.
        Note: This is a simplified example - the actual implementation depends on
        how UB's search page is structured.
        """
        courses = []
        
        # UB uses a specific format for terms
        term_codes = {
            "2025 Spring": "1251",
            "2025 Fall": "1259",
            "2024 Fall": "1249"
        }
        
        # For HUB public search, we'll use a different approach
        # The actual public search is at: https://cdcs.ur.buffalo.edu/psc/csprdpub/
        
        # Alternative: Use the course catalog which is more stable
        catalog_url = f"https://catalog.buffalo.edu/courses/{subject.lower()}/"
        
        try:
            response = self.session.get(catalog_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all course blocks
            course_blocks = soup.find_all('div', class_='courseblock')
            
            for block in course_blocks:
                course_data = self.parse_course_block(block, subject)
                if course_data:
                    courses.append(course_data)
                    
        except Exception as e:
            print(f"Error scraping {subject}: {e}")
            
        return courses
    
    def parse_course_block(self, block, subject: str) -> Dict:
        """Parse individual course block from catalog page"""
        try:
            # Extract course number and title
            title_elem = block.find('p', class_='courseblocktitle')
            if not title_elem:
                return None
                
            title_text = title_elem.get_text(strip=True)
            
            # Parse format like "CSE 115LR - Introduction to Computer Science I"
            match = re.match(r'([A-Z]+)\s+(\d+[A-Z]*)\s+-\s+(.+)', title_text)
            if not match:
                return None
                
            dept, number, title = match.groups()
            course_id = f"{dept} {number}"
            
            # Extract credits
            credits = 0
            credits_match = re.search(r'Credits:\s*(\d+)', title_text)
            if credits_match:
                credits = int(credits_match.group(1))
            
            # Extract description
            desc_elem = block.find('p', class_='courseblockdesc')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Determine level
            course_num = int(re.match(r'\d+', number).group())
            level = "GR" if course_num >= 500 else "UG"
            
            return {
                'course_id': course_id,
                'title': title,
                'description': description,
                'credits': credits,
                'department': subject,
                'level': level
            }
            
        except Exception as e:
            print(f"Error parsing course block: {e}")
            return None
    
    def get_class_schedule(self, term: str = "2025 Spring", subject: str = "CSE") -> List[Dict]:
        """
        Get actual class schedule with sections, times, instructors.
        This would need to interact with HUB's public class search.
        """
        offerings = []
        
        # The public class search requires more complex interaction
        # For a real implementation, you'd need to:
        # 1. Navigate to the search page
        # 2. Submit search parameters
        # 3. Parse the results
        
        # For now, here's a template of what the data would look like:
        sample_offerings = [
            {
                'term': '2025-01',  # Spring 2025
                'course_id': 'CSE 115',
                'section': 'LEC A',
                'instructor': 'Carl Alphonce',
                'days': 'MWF',
                'start_time': '09:00',
                'end_time': '09:50',
                'room': 'Norton 112',
                'campus': 'North Campus',
                'modality': 'In Person'
            },
            {
                'term': '2025-01',
                'course_id': 'CSE 116',
                'section': 'LEC A',
                'instructor': 'Matthew Hertz',
                'days': 'TR',
                'start_time': '14:00',
                'end_time': '15:20',
                'room': 'NSC 201',
                'campus': 'North Campus',
                'modality': 'In Person'
            }
        ]
        
        return sample_offerings
    
    def scrape_all_departments(self, departments: List[str]) -> Dict:
        """Scrape courses for multiple departments"""
        all_courses = {}
        
        for dept in departments:
            print(f"Scraping {dept}...")
            courses = self.search_courses(subject=dept)
            all_courses[dept] = courses
            time.sleep(1)  # Be respectful to the server
            
        return all_courses
    
    def save_to_csv(self, courses: List[Dict], filename: str = "courses.csv"):
        """Save courses to CSV format for your database"""
        if not courses:
            print("No courses to save")
            return
            
        fieldnames = ['course_id', 'title', 'description', 'credits', 'department', 'level']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for course in courses:
                writer.writerow(course)
        
        print(f"Saved {len(courses)} courses to {filename}")
    
    def save_offerings_to_csv(self, offerings: List[Dict], filename: str = "offerings.csv"):
        """Save course offerings to CSV"""
        if not offerings:
            print("No offerings to save")
            return
            
        fieldnames = ['term', 'course_id', 'section', 'instructor', 'days', 
                     'start_time', 'end_time', 'room', 'campus', 'modality']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for offering in offerings:
                writer.writerow(offering)
        
        print(f"Saved {len(offerings)} offerings to {filename}")


def scrape_ub_quick():
    """Quick function to scrape some UB data"""
    scraper = UBCourseScraper()
    
    # Scrape a few departments
    departments = ['CSE', 'MTH', 'ENG', 'BIO', 'PSY']
    
    all_courses = []
    for dept in departments:
        print(f"\nScraping {dept} courses...")
        courses = scraper.search_courses(subject=dept)
        all_courses.extend(courses)
        print(f"Found {len(courses)} {dept} courses")
        time.sleep(1)  # Don't overwhelm the server
    
    # Save to CSV
    if all_courses:
        scraper.save_to_csv(all_courses, "ub_courses_real.csv")
    
    # Get some sample offerings (you'd expand this with real schedule data)
    offerings = scraper.get_class_schedule()
    if offerings:
        scraper.save_offerings_to_csv(offerings, "ub_offerings_real.csv")
    
    return all_courses, offerings


if __name__ == "__main__":
    print("Starting UB course scraper...")
    courses, offerings = scrape_ub_quick()
    print(f"\nTotal courses scraped: {len(courses)}")
    print(f"Total offerings: {len(offerings)}")