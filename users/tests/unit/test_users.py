import unittest
import src.users.service as users_service


class UserServiceTestCase(unittest.TestCase):
    def test_find_user_by_name_when_user_doesnt_exist(self):
        self.assertEqual(users_service.find_user_by_name("NonExistingUser"), [])

    # def test_find_user_by_name_when_user_exists(self):
    #     users_service.insert_user("User")
    #     user = users_service.find_user_by_name("User")
    #     self.assertEqual(len(user), 1)
    #     self.assertEqual(user[0].name, "User")


if __name__ == "__main__":
    unittest.main()
