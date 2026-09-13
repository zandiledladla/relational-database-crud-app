"""Command-line student record manager backed by SQLite."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


DEFAULT_DATABASE = Path("students.db")


def connect(database: str | Path = DEFAULT_DATABASE) -> sqlite3.Connection:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


def create_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(trim(name)) > 0),
            age INTEGER NOT NULL CHECK(age BETWEEN 1 AND 120),
            major TEXT NOT NULL CHECK(length(trim(major)) > 0)
        )
        """
    )
    connection.commit()


def add_student(connection: sqlite3.Connection, name: str, age: int, major: str) -> int:
    name = name.strip()
    major = major.strip()
    if not name or not major:
        raise ValueError("name and major are required")
    if not 1 <= age <= 120:
        raise ValueError("age must be between 1 and 120")

    cursor = connection.execute(
        "INSERT INTO students (name, age, major) VALUES (?, ?, ?)",
        (name, age, major),
    )
    connection.commit()
    return int(cursor.lastrowid)


def list_students(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(connection.execute("SELECT id, name, age, major FROM students ORDER BY id"))


def update_student(
    connection: sqlite3.Connection,
    student_id: int,
    *,
    name: str | None = None,
    age: int | None = None,
    major: str | None = None,
) -> bool:
    fields: list[str] = []
    values: list[object] = []

    if name is not None:
        if not name.strip():
            raise ValueError("name cannot be empty")
        fields.append("name = ?")
        values.append(name.strip())
    if age is not None:
        if not 1 <= age <= 120:
            raise ValueError("age must be between 1 and 120")
        fields.append("age = ?")
        values.append(age)
    if major is not None:
        if not major.strip():
            raise ValueError("major cannot be empty")
        fields.append("major = ?")
        values.append(major.strip())

    if not fields:
        return False

    values.append(student_id)
    cursor = connection.execute(
        f"UPDATE students SET {', '.join(fields)} WHERE id = ?",
        values,
    )
    connection.commit()
    return cursor.rowcount > 0


def delete_student(connection: sqlite3.Connection, student_id: int) -> bool:
    cursor = connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
    connection.commit()
    return cursor.rowcount > 0


def read_age(prompt: str) -> int:
    try:
        age = int(input(prompt))
    except ValueError as error:
        raise ValueError("age must be a whole number") from error
    if not 1 <= age <= 120:
        raise ValueError("age must be between 1 and 120")
    return age


def display_students(connection: sqlite3.Connection) -> None:
    students = list_students(connection)
    if not students:
        print("No student records found.\n")
        return
    print("\nAll students")
    for student in students:
        print(f"{student['id']}: {student['name']} | Age {student['age']} | {student['major']}")
    print()


def menu(connection: sqlite3.Connection) -> None:
    while True:
        print("Student Record Manager")
        print("1. Add student")
        print("2. View students")
        print("3. Update student")
        print("4. Delete student")
        print("5. Exit")
        choice = input("Choose an option (1-5): ").strip()

        try:
            if choice == "1":
                student_id = add_student(
                    connection,
                    input("Student name: "),
                    read_age("Student age: "),
                    input("Student major: "),
                )
                print(f"Student {student_id} added successfully.\n")
            elif choice == "2":
                display_students(connection)
            elif choice == "3":
                student_id = int(input("Student ID: "))
                name = input("New name (leave blank to keep): ").strip() or None
                age_text = input("New age (leave blank to keep): ").strip()
                major = input("New major (leave blank to keep): ").strip() or None
                age = int(age_text) if age_text else None
                changed = update_student(connection, student_id, name=name, age=age, major=major)
                print("Student updated.\n" if changed else "No matching record or changes.\n")
            elif choice == "4":
                student_id = int(input("Student ID: "))
                deleted = delete_student(connection, student_id)
                print("Student deleted.\n" if deleted else "Student not found.\n")
            elif choice == "5":
                print("Goodbye!")
                return
            else:
                print("Please choose a number from 1 to 5.\n")
        except ValueError as error:
            print(f"Invalid input: {error}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=str(DEFAULT_DATABASE))
    args = parser.parse_args()
    with connect(args.database) as connection:
        create_table(connection)
        menu(connection)


if __name__ == "__main__":
    main()
