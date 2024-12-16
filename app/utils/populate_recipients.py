# populate_recipients.py

from sqlalchemy.orm import Session
from app.models import Announcement, User, ParentStudent, Student, announcement_recipients, Base
from app.database import engine
from sqlalchemy import select

# Create a new session
session = Session(bind=engine)

def assign_parents_to_announcements():
    # Fetch all announcements
    announcements = session.query(Announcement).all()
    
    for announcement in announcements:
        # Check if the announcement has specific recipients
        if not announcement.recipients:
            # If no recipients, it's intended for all parents of the class
            # Fetch all parents of the class
            class_id = announcement.class_id
            parent_ids = session.query(ParentStudent.parent_id).join(Student).filter(Student.class_id == class_id).all()
            parent_ids = [pid for (pid,) in parent_ids]
            
            # Assign all parents to the announcement
            for parent_id in parent_ids:
                parent = session.query(User).get(parent_id)
                if parent and parent not in announcement.recipients:
                    announcement.recipients.append(parent)
        else:
            # If there are specific recipients, ensure only those see the announcement
            # No action needed as recipients are already assigned
            pass
    
    # Commit the changes
    session.commit()
    print("Parents have been assigned to announcements based on class associations.")

if __name__ == "__main__":
    assign_parents_to_announcements()
