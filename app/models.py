# models.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.database import Base
from sqlalchemy.dialects.postgresql import ARRAY


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    address = Column(String)

    classes = relationship("Class", back_populates="school")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)

    school = relationship("School", back_populates="classes")
    teachers = relationship("User", secondary="teacher_class", back_populates="classes_taught")
    students = relationship("Student", back_populates="class_")
    class_reps = relationship("ClassRepresentative", back_populates="class_")
    announcements = relationship("Announcement", back_populates="class_")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'teacher', 'parent'

    # Relationship to ParentStudent and children (students)
    children = relationship("ParentStudent", back_populates="parent")
    classes_taught = relationship("Class", secondary="teacher_class", back_populates="teachers")
    represented_classes = relationship("ClassRepresentative", back_populates="parent")
    announcements_created = relationship("Announcement", back_populates="creator")
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    announcements_created = relationship("Announcement", back_populates="creator")




class TeacherClass(Base):
    __tablename__ = "teacher_class"

    teacher_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), primary_key=True)

    # Relationships are defined via secondary relationship in User and Class


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    class_ = relationship("Class", back_populates="students")
    parents = relationship("ParentStudent", back_populates="student")



class ParentStudent(Base):
    __tablename__ = "parent_student"

    parent_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    relationship_type = Column(String, nullable=True)  # e.g., 'father', 'mother', 'guardian'

    # Relationship to User (parent) and Student
    parent = relationship("User", back_populates="children")
    student = relationship("Student", back_populates="parents")




class ClassRepresentative(Base):
    __tablename__ = "class_representative"

    parent_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"), primary_key=True)

    parent = relationship("User", back_populates="represented_classes")
    class_ = relationship("Class", back_populates="class_reps")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content_en = Column(Text, nullable=True)  # English content
    content_de = Column(Text, nullable=True)  # German content
    content_fr = Column(Text, nullable=True)  # French content
    original_language = Column(String, default="en")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    target_audience = Column(String, nullable=False)  # 'parents', 'teachers'
    recipients = Column(ARRAY(Integer), nullable=True)  # Recipient user IDs

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    creator = relationship("User", back_populates="announcements_created")
    class_ = relationship("Class", back_populates="announcements")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    address = Column(String)
    hobbies = Column(String)
    preferred_contact_method = Column(String)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    user = relationship("User", back_populates="profile")
    school = relationship("School")
    class_ = relationship("Class")


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User")

from sqlalchemy.orm import configure_mappers

configure_mappers()
