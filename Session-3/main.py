
from sqlalchemy import (
    create_engine,
    ForeignKey,
    String,
    select,
    func,
    desc,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


# ==================================================
# 1. DATABASE CONNECTION
# ==================================================

DATABASE_URL = "sqlite:///course_enrollment.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine)


# ==================================================
# 2. CREATE THE BASE CLASS
# ==================================================

class Base(DeclarativeBase):
    pass


# ==================================================
# 3. SQLALCHEMY MODELS
# ==================================================

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150))

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id")
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id")
    )

    student: Mapped["Student"] = relationship(
        back_populates="enrollments"
    )

    course: Mapped["Course"] = relationship(
        back_populates="enrollments"
    )


# Create all three tables if they do not exist.
Base.metadata.create_all(engine)


# ==================================================
# 4. ADD A STUDENT
# ==================================================

def add_student(name, email):
    with SessionLocal() as session:
        student = Student(name=name, email=email)

        session.add(student)
        session.commit()
        session.refresh(student)

        print(f"Student added: {student.name}, ID: {student.id}")
        return student.id


# ==================================================
# 5. ADD A COURSE
# ==================================================

def add_course(name, category):
    with SessionLocal() as session:
        course = Course(name=name, category=category)

        session.add(course)
        session.commit()
        session.refresh(course)

        print(f"Course added: {course.name}, ID: {course.id}")
        return course.id


# ==================================================
# 6. ENROLL A STUDENT IN A COURSE
# ==================================================

def enroll_student(student_id, course_id):
    with SessionLocal() as session:
        student = session.get(Student, student_id)
        course = session.get(Course, course_id)

        if student is None:
            print("Student not found.")
            return

        if course is None:
            print("Course not found.")
            return

        # Prevent duplicate enrollment.
        existing = session.scalar(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
            )
        )

        if existing is not None:
            print("Student is already enrolled in this course.")
            return

        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
        )

        session.add(enrollment)
        session.commit()

        print(f"{student.name} enrolled in {course.name}.")


# ==================================================
# 7. UPDATE A STUDENT'S EMAIL
# ==================================================

def update_student_email(student_id, new_email):
    with SessionLocal() as session:
        student = session.get(Student, student_id)

        if student is None:
            print("Student not found.")
            return

        student.email = new_email
        session.commit()

        print(f"Updated email for {student.name}: {new_email}")


# ==================================================
# 8. DELETE AN ENROLLMENT
# ==================================================

def delete_enrollment(student_id, course_id):
    with SessionLocal() as session:
        enrollment = session.scalar(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
            )
        )

        if enrollment is None:
            print("Enrollment not found.")
            return

        session.delete(enrollment)
        session.commit()

        print("Enrollment deleted successfully.")


# ==================================================
# 9. INNER JOIN: STUDENTS AND THEIR COURSES
# ==================================================

def show_student_courses():
    with SessionLocal() as session:
        statement = (
            select(Student.name, Course.name)
            .join(
                Enrollment,
                Student.id == Enrollment.student_id,
            )
            .join(
                Course,
                Course.id == Enrollment.course_id,
            )
            .order_by(Student.name, Course.name)
        )

        results = session.execute(statement).all()

        print("\nSTUDENT ENROLLMENTS")
        print("-------------------")

        for student_name, course_name in results:
            print(f"{student_name} | {course_name}")


# ==================================================
# 10. LEFT JOIN: STUDENTS WITH NO ENROLLMENTS
# ==================================================

def show_unenrolled_students():
    with SessionLocal() as session:
        statement = (
            select(Student.name)
            .outerjoin(
                Enrollment,
                Student.id == Enrollment.student_id,
            )
            .where(Enrollment.id.is_(None))
            .order_by(Student.name)
        )

        results = session.scalars(statement).all()

        print("\nSTUDENTS NOT ENROLLED")
        print("---------------------")

        for name in results:
            print(name)


# ==================================================
# 11. COURSE-WISE ENROLLMENT COUNT
# ==================================================

def show_course_enrollment_counts():
    with SessionLocal() as session:
        statement = (
            select(
                Course.name,
                func.count(Enrollment.id).label(
                    "student_count"
                ),
            )
            .outerjoin(
                Enrollment,
                Course.id == Enrollment.course_id,
            )
            .group_by(Course.id, Course.name)
            .order_by(Course.name)
        )

        results = session.execute(statement).all()

        print("\nCOURSE-WISE ENROLLMENT COUNTS")
        print("-----------------------------")

        for course_name, count in results:
            print(f"{course_name} | {count}")


# ==================================================
# 12. HAVING: COURSES WITH MORE THAN 10 ENROLLMENTS
# ==================================================

def show_popular_courses():
    with SessionLocal() as session:
        statement = (
            select(
                Course.name,
                func.count(Enrollment.id).label(
                    "student_count"
                ),
            )
            .join(
                Enrollment,
                Course.id == Enrollment.course_id,
            )
            .group_by(Course.id, Course.name)
            .having(func.count(Enrollment.id) > 10)
            .order_by(desc("student_count"))
        )

        results = session.execute(statement).all()

        print("\nCOURSES WITH MORE THAN 10 ENROLLMENTS")
        print("-------------------------------------")

        for course_name, count in results:
            print(f"{course_name} | {count}")


# ==================================================
# 13. BONUS: MOST POPULAR COURSE
# ==================================================

def show_most_popular_course():
    with SessionLocal() as session:
        statement = (
            select(
                Course.name,
                func.count(Enrollment.id).label(
                    "student_count"
                ),
            )
            .join(
                Enrollment,
                Course.id == Enrollment.course_id,
            )
            .group_by(Course.id, Course.name)
            .order_by(desc("student_count"))
            .limit(1)
        )

        result = session.execute(statement).first()

        print("\nMOST POPULAR COURSE")
        print("-------------------")

        if result is None:
            print("No enrollments found.")
        else:
            print(f"{result[0]} | {result[1]}")


# ==================================================
# 14. DISPLAY ALL STUDENTS
# ==================================================

def show_all_students():
    with SessionLocal() as session:
        students = session.scalars(
            select(Student).order_by(Student.id)
        ).all()

        print("\nALL STUDENTS")
        print("------------")

        for student in students:
            print(
                f"ID: {student.id} | "
                f"Name: {student.name} | "
                f"Email: {student.email}"
            )


# ==================================================
# 15. DEMO DATA AND RUN THE APPLICATION
# ==================================================

if __name__ == "__main__":
    with SessionLocal() as session:
        # Insert sample data only when the database
        # has no students. This avoids duplicate demo
        # data on every run.
        if session.scalar(select(Student.id).limit(1)) is None:
            aman = Student(
                name="Aman",
                email="aman@gmail.com",
            )
            rahul = Student(
                name="Rahul",
                email="rahul@example.com",
            )
            priya = Student(
                name="Priya",
                email="priya@example.com",
            )

            python_course = Course(
                name="Python Backend",
                category="Backend",
            )
            sql_course = Course(
                name="SQL",
                category="Database",
            )
            react_course = Course(
                name="React",
                category="Frontend",
            )

            session.add_all([
                aman,
                rahul,
                priya,
                python_course,
                sql_course,
                react_course,
            ])
            session.commit()

            # Create enrollment records.
            session.add_all([
                Enrollment(
                    student_id=aman.id,
                    course_id=python_course.id,
                ),
                Enrollment(
                    student_id=aman.id,
                    course_id=sql_course.id,
                ),
                Enrollment(
                    student_id=rahul.id,
                    course_id=sql_course.id,
                ),
            ])
            session.commit()

    # Look up IDs rather than assuming they start at 1.
    with SessionLocal() as session:
        aman_id = session.scalar(
            select(Student.id).where(Student.name == "Aman")
        )
        python_id = session.scalar(
            select(Course.id).where(
                Course.name == "Python Backend"
            )
        )

    # Demonstrate UPDATE.
    update_student_email(aman_id, "aman@example.com")

    # Show queries before deleting the example enrollment.
    show_all_students()
    show_student_courses()
    show_unenrolled_students()
    show_course_enrollment_counts()
    show_popular_courses()
    show_most_popular_course()

    # Demonstrate DELETE after displaying the reports.
    delete_enrollment(aman_id, python_id)

    # Verify the enrollment has been removed.
    show_student_courses()
