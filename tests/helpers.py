class TestUser:
    def __init__(
        self,
        username: str,
        password: str,
        update_testcase: dict | None = None,
        update_by_admin_testcase: dict | None = None,
        new_password: str = None,
        name: str | None = None,
        b_date: str | None = None,
    ):
        self.username = username
        self.password = password
        self.update_testcase = update_testcase
        self.update_by_admin_testcase = update_by_admin_testcase
        self._new_password = new_password
        self.name = name
        self.b_date = b_date
        self.user_id: int | None = None

    def update_user(self, admin_flg: bool = False):
        if self.update_by_admin_testcase and admin_flg:
            if username := self.update_by_admin_testcase.get("username"):
                self.username = username
            if name := self.update_by_admin_testcase.get("name"):
                self.name = name
            if b_date := self.update_by_admin_testcase.get("b_date"):
                self.b_date = b_date
            return True
        elif self.update_testcase:
            if username := self.update_testcase.get("username"):
                self.username = username
            if name := self.update_testcase.get("name"):
                self.name = name
            if b_date := self.update_testcase.get("b_date"):
                self.b_date = b_date
            return True
        return False

    def update_password(self):
        if self._new_password:
            self.password = self._new_password
            return True
        return False

    def json(self):
        return {
            "username": self.username,
            "name": self.name,
            "b_date": self.b_date,
            "password": self.password,
        }


class AuthedUser:
    def __init__(
        self,
        user: TestUser,
        access_token,
        refresh_token,
    ):
        self.user = user
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
