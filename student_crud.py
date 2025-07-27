import sqlite3

# Step 1: Connect to the database (it will create one if it doesn't exist)
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Step 2: Create the table to store student records (if it doesn't already exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    major TEXT
)
''')
conn.commit()

# Function to add a student to the database
def add_student():
    name = input("Enter student name: ")
    age = int(input("Enter student age: "))
    major = input("Enter student major: ")
    cursor.execute('INSERT INTO students (name, age, major) VALUES (?, ?, ?)', (name, age, major))
    conn.commit()
    print(f"✅ Student '{name}' added successfully.\n")

# Function to display all students
def view_students():
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    print("\n📚 All Students:")
    for student in students:
        print(student)
    print()

# Function to update a student's information
def update_student():
    student_id = int(input("Enter the ID of the student to update: "))
    print("Leave a field blank if you don't want to update it.")

    name = input("New name: ")
    age_input = input("New age: ")
    major = input("New major: ")

    fields = []
    values = []

    if name:
        fields.append("name = ?")
        values.append(name)
    if age_input:
        fields.append("age = ?")
        values.append(int(age_input))
    if major:
        fields.append("major = ?")
        values.append(major)

    if fields:
        values.append(student_id)
        sql = f'UPDATE students SET {", ".join(fields)} WHERE id = ?'
        cursor.execute(sql, values)
        conn.commit()
        print(f"🔁 Student ID {student_id} updated.\n")
    else:
        print("⚠️ Nothing to update.\n")

# Function to delete a student
def delete_student():
    student_id = int(input("Enter the ID of the student to delete: "))
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    print(f"❌ Student ID {student_id} deleted.\n")

# Function to show menu and get user input
def menu():
    while True:
        print("📋 MENU")
        print("1. Add Student")
        print("2. View Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Exit")

        choice = input("Choose an option (1-5): ")

        if choice == '1':
            add_student()
        elif choice == '2':
            view_students()
        elif choice == '3':
            update_student()
        elif choice == '4':
            delete_student()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❗Invalid option. Please try again.\n")

# Run the app
if __name__ == "__main__":
    print("🎓 Welcome to the Student Record Manager!")
    menu()

    # Always close the connection when done
    conn.close()
