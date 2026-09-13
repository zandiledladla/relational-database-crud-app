import sqlite3
import unittest

from student_crud import add_student, create_table, delete_student, list_students, update_student


class StudentCrudTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        create_table(self.connection)

    def tearDown(self):
        self.connection.close()

    def test_add_and_list_student(self):
        student_id = add_student(self.connection, "Zandile", 23, "Computer Science")
        students = list_students(self.connection)
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0]["id"], student_id)
        self.assertEqual(students[0]["name"], "Zandile")

    def test_update_selected_fields(self):
        student_id = add_student(self.connection, "Amanda", 21, "Information Systems")
        changed = update_student(self.connection, student_id, major="Computer Science")
        self.assertTrue(changed)
        self.assertEqual(list_students(self.connection)[0]["major"], "Computer Science")

    def test_delete_existing_student(self):
        student_id = add_student(self.connection, "Student", 20, "Mathematics")
        self.assertTrue(delete_student(self.connection, student_id))
        self.assertEqual(list_students(self.connection), [])

    def test_missing_student_returns_false(self):
        self.assertFalse(update_student(self.connection, 999, name="Nobody"))
        self.assertFalse(delete_student(self.connection, 999))

    def test_invalid_student_data_is_rejected(self):
        invalid_records = [
            ("", 20, "Computer Science"),
            ("Name", 0, "Computer Science"),
            ("Name", 121, "Computer Science"),
            ("Name", 20, "  "),
        ]
        for record in invalid_records:
            with self.subTest(record=record):
                with self.assertRaises(ValueError):
                    add_student(self.connection, *record)


if __name__ == "__main__":
    unittest.main()
