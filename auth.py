import getpass

AUTHORIZED_USERS = ["ganesh", "admin"]

def check_user():
    user = getpass.getuser()
    return user, user in AUTHORIZED_USERS