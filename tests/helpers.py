class AuthedUser:
    def __init__(self, username, password, access_token, refresh_token):
        self.username = username
        self.password = password
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
