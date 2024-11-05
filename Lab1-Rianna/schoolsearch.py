# Function to load students from list.txt
def load_students(file_path):
    students = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                fields = line.strip().split(',')
                student = {
                    'last_name': fields[0].strip(),
                    'first_name': fields[1].strip(),
                    'grade': int(fields[2].strip()),
                    'classroom': int(fields[3].strip()),
                    'bus': int(fields[4].strip()),
                    'gpa': float(fields[5].strip())
                }
                students.append(student)
    except FileNotFoundError:
        print("The file list.txt could not be found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return students

# Function to load teachers from teachers.txt
def load_teachers(file_path):
    teachers = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                fields = line.strip().split(',')
                classroom = int(fields[2].strip())
                teacher = {
                    'last_name': fields[0].strip(),
                    'first_name': fields[1].strip(),
                }
                if classroom in teachers:
                    teachers[classroom].append(teacher)
                else:
                    teachers[classroom] = [teacher]
    except FileNotFoundError:
        print("The file teachers.txt could not be found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return teachers

# Combine the students and teachers data
def combine_students_teachers(students, teachers):
    for student in students:
        classroom = student['classroom']
        if classroom in teachers:
            student['teachers'] = teachers[classroom]
        else:
            student['teachers'] = []

    return students

# Search for students by last name
def search_student_by_last_name(students, last_name):
    results = [student for student in students if student['last_name'].lower() == last_name.lower()]
    if results:
        for student in results:
            teacher_names = ", ".join([f"{teacher['last_name']}, {teacher['first_name']}" for teacher in student['teachers']])
            print(f"{student['last_name']}, {student['first_name']}, Grade: {student['grade']}, "
                  f"Classroom: {student['classroom']}, GPA: {student['gpa']}, Teachers: {teacher_names}")
    else:
        print("No student found with that last name.")

# Search for students by classroom number (NR1)
def search_students_by_classroom(students, classroom):
    results = [student for student in students if student['classroom'] == classroom]
    if results:
        for student in results:
            print(f"{student['last_name']}, {student['first_name']}, Grade: {student['grade']}, GPA: {student['gpa']}")
    else:
        print(f"No students found in classroom {classroom}.")

# Search for teachers by classroom number (NR2)
def search_teachers_by_classroom(teachers, classroom):
    if classroom in teachers:
        for teacher in teachers[classroom]:
            print(f"Teacher: {teacher['last_name']}, {teacher['first_name']}")
    else:
        print(f"No teachers found in classroom {classroom}.")

# Search for teachers by grade (NR3)
def search_teachers_by_grade(students, grade):
    classrooms = set([student['classroom'] for student in students if student['grade'] == grade])
    teachers_found = set()

    for classroom in classrooms:
        for student in students:
            if student['classroom'] == classroom:
                for teacher in student['teachers']:
                    teachers_found.add(f"{teacher['last_name']}, {teacher['first_name']}")

    if teachers_found:
        for teacher in teachers_found:
            print(f"Teacher: {teacher}")
    else:
        print(f"No teachers found for grade {grade}.")

# Report enrollments broken down by classroom (NR4)
def report_enrollments_by_classroom(students):
    classroom_enrollment = {}
    for student in students:
        classroom = student['classroom']
        if classroom in classroom_enrollment:
            classroom_enrollment[classroom] += 1
        else:
            classroom_enrollment[classroom] = 1

    for classroom in sorted(classroom_enrollment.keys()):
        print(f"Classroom {classroom}: {classroom_enrollment[classroom]} students")

# Calculate average GPA by grade, teacher, or bus route (NR5 example for analytics)
def calculate_gpa_by_grade(students):
    grade_gpa = {}
    for student in students:
        grade = student['grade']
        if grade in grade_gpa:
            grade_gpa[grade].append(student['gpa'])
        else:
            grade_gpa[grade] = [student['gpa']]

    for grade, gpas in grade_gpa.items():
        average_gpa = sum(gpas) / len(gpas)
        print(f"Grade {grade}: Average GPA = {round(average_gpa, 2)}")

def calculate_gpa_by_teacher(students, teacher_last_name):
    students_with_teacher = [student for student in students if any(teacher['last_name'].lower() == teacher_last_name.lower() for teacher in student['teachers'])]
    
    if not students_with_teacher:
        print(f"No students found for teacher {teacher_last_name}.")
        return
    
    average_gpa = sum(student['gpa'] for student in students_with_teacher) / len(students_with_teacher)
    print(f"Teacher {teacher_last_name}: Average GPA = {round(average_gpa, 2)}")

def calculate_gpa_by_bus(students, bus_number):
    students_on_bus = [student for student in students if student['bus'] == bus_number]

    if not students_on_bus:
        print(f"No students found on bus {bus_number}.")
        return

    average_gpa = sum(student['gpa'] for student in students_on_bus) / len(students_on_bus)
    print(f"Bus {bus_number}: Average GPA = {round(average_gpa, 2)}")

# Command-line interface to handle user inputs
def start_school_search(students, teachers):
    while True:
        command = input("Enter command (S: <lastname>, C: <classroom>, T: <teacher>, G: <grade>, R: report, GPA: <type>, Q: quit): ").strip()

        if command.startswith('S:'):
            # Searching for a student by last name
            last_name = command.split(":")[1].strip()
            search_student_by_last_name(students, last_name)

        elif command.startswith('C:'):
            # Searching for students by classroom number
            classroom = int(command.split(":")[1].strip())
            search_students_by_classroom(students, classroom)

        elif command.startswith('T:'):
            # Searching for teachers by classroom number
            classroom = int(command.split(":")[1].strip())
            search_teachers_by_classroom(teachers, classroom)

        elif command.startswith('G:'):
            # Searching for teachers by grade
            grade = int(command.split(":")[1].strip())
            search_teachers_by_grade(students, grade)

        elif command == 'R':
            # Report enrollments by classroom
            report_enrollments_by_classroom(students)

        elif command.startswith('GPA:'):
            # GPA analytics
            parts = command.split(":")[1].strip().split()
            if parts[0] == "GRADE":
                calculate_gpa_by_grade(students)
            elif parts[0] == "TEACHER":
                teacher_last_name = parts[1]
                calculate_gpa_by_teacher(students, teacher_last_name)
            elif parts[0] == "BUS":
                bus_number = int(parts[1])
                calculate_gpa_by_bus(students, bus_number)

        elif command == 'Q':
            print("Quitting the program.")
            break
        else:
            print("Invalid command. Please try again.")

# Main program
if __name__ == '__main__':
    # Load students and teachers data from the files
    students_file = 'list.txt'
    teachers_file = 'teachers.txt'
    
    students = load_students(students_file)
    teachers = load_teachers(teachers_file)
    
    if students and teachers:
        # Combine student and teacher data
        students = combine_students_teachers(students, teachers)
        # Start the interactive search
        start_school_search(students, teachers)
