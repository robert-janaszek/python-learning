class UserService:
    def __init__(self):
        self._users: dict[str, dict[str, str]] = dict()
    def register(self, email: str) -> dict[str, str]:
        self.validate_email(email)
        if email in self._users:
            return self._users[email]
        self._users[email] = { "email": email }
        return self._users[email]
    def get_user(self, email: str) -> dict[str, str]:
        return self._users[email]
    def validate_email(self, email: str) -> None:
        if email.count('@') == 0:
            raise ValueError("Incorrect email, @ not found")
        if email.count('@') > 1:
            raise ValueError("Incorrect email, more than 1 @ found")
        if len(email.split("@")[0]) == 0:
            raise ValueError("Incorrect email, empty username")
        if len(email.split("@")[1]) == 0:
            raise ValueError("Incorrect email, empty domain")
