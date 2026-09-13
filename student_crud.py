"""Command-line student record manager backed by SQLite."""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Student:
    id: int
    name: str
    age: int
    major: str

class StudentRepository:
    """Persistence layer for validated student records."""
    def __init__(self, database: str | Path = "students.db") -> None:
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("""CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(trim(name)) > 0),
            age INTEGER NOT NULL CHECK(age BETWEEN 16 AND 120),
            major TEXT NOT NULL CHECK(length(trim(major)) > 0))""")
        self.connection.commit()

    def __enter__(self) -> "StudentRepository": return self
    def __exit__(self, *_: object) -> None: self.close()

    def add(self, name: str, age: int, major: str) -> Student:
        name, major = self._validate(name, age, major)
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO students (name, age, major) VALUES (?, ?, ?)",
                (name, age, major))
        return self.get(cursor.lastrowid)

    def all(self) -> list[Student]:
        rows = self.connection.execute(
            "SELECT id, name, age, major FROM students ORDER BY id").fetchall()
        return [Student(**dict(row)) for row in rows]

    def get(self, student_id: int) -> Student:
        row = self.connection.execute(
            "SELECT id, name, age, major FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        if row is None: raise LookupError(f"Student {student_id} was not found")
        return Student(**dict(row))

    def update(self, student_id: int, *, name: str | None = None,
               age: int | None = None, major: str | None = None) -> Student:
        current = self.get(student_id)
        name, age, major = (current.name if name is None else name,
                            current.age if age is None else age,
                            current.major if major is None else major)
        name, major = self._validate(name, age, major)
        with self.connection:
            self.connection.execute(
                "UPDATE students SET name = ?, age = ?, major = ? WHERE id = ?",
                (name, age, major, student_id))
        return self.get(student_id)

    def delete(self, student_id: int) -> None:
        with self.connection:
            cursor = self.connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
        if cursor.rowcount == 0: raise LookupError(f"Student {student_id} was not found")

    def close(self) -> None: self.connection.close()

    @staticmethod
    def _validate(name: str, age: int, major: str) -> tuple[str, str]:
        name, major = name.strip(), major.strip()
        if not name or not major: raise ValueError("Name and major are required")
        if not 16 <= age <= 120: raise ValueError("Age must be between 16 and 120")
        return name, major

def read_integer(prompt: str) -> int:
    while True:
        try: return int(input(prompt))
        except ValueError: print("Please enter a whole number.")

def menu(repository: StudentRepository) -> None:
    while True:
        print("\n1. Add student  2. View students  3. Update  4. Delete  5. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "5": return
        try:
            if choice == "1":
                student = repository.add(input("Name: "), read_integer("Age: "), input("Major: "))
                print(f"Added student {student.id}: {student.name}")
            elif choice == "2":
                for student in repository.all():
                    print(f"{student.id}: {student.name}, {student.age}, {student.major}")
            elif choice == "3":
                student_id = read_integer("Student ID: ")
                name = input("New name (blank to keep): ").strip() or None
                age_text = input("New age (blank to keep): ").strip()
                major = input("New major (blank to keep): ").strip() or None
                repository.update(student_id, name=name,
                    age=int(age_text) if age_text else None, major=major)
                print("Student updated.")
            elif choice == "4":
                repository.delete(read_integer("Student ID: "))
                print("Student deleted.")
            else: print("Choose a number from 1 to 5.")
        except (LookupError, ValueError) as error: print(f"Error: {error}")

if __name__ == "__main__":
    print("Student Record Manager")
    with StudentRepository() as repository: menu(repository)
