import unittest
from student_crud import StudentRepository

class StudentRepositoryTests(unittest.TestCase):
    def setUp(self): self.repository = StudentRepository(":memory:")
    def tearDown(self): self.repository.close()

    def test_complete_crud_lifecycle(self):
        created = self.repository.add("Zandile Dladla", 24, "Computer Science")
        self.assertEqual(self.repository.get(created.id), created)
        updated = self.repository.update(created.id, major="Software Engineering")
        self.assertEqual(updated.major, "Software Engineering")
        self.repository.delete(created.id)
        self.assertEqual(self.repository.all(), [])

    def test_rejects_invalid_student(self):
        with self.assertRaises(ValueError): self.repository.add("", 15, "")

    def test_missing_record_raises_clear_error(self):
        with self.assertRaises(LookupError): self.repository.get(999)

if __name__ == "__main__": unittest.main()
