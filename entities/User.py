class User:
    def __init__(self, student_id, username, password, phone, user_type):
        self.student_id = student_id
        self.username = username
        self.password = password
        self.phone = phone
        self.user_type = user_type

    def get_login_params(self):
        return {
            'redirect': 'NO',
            'username': self.username,
            'password': self.password,
            'x': 0,
            'y': 0
        }
