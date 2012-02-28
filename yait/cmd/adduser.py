"""Interactive command-line utility to add a new user."""

# FIXME: there must a web interface to add a new user. So there will
# be field validators that we should reuse here. In fact, I am not
# sure that this utility is of any use at all.


import sys

import transaction

from yait.models import DBSession
from yait.models import User


class AddUser(object):
    def __init__(self):
        self.session = DBSession()

    def run(self):
        info = self.interactive()
        self.add_user(**info)

    def add_user(self, login, password, fullname, email, is_admin):
        user = User(login=login, password=password,
                    fullname=fullname, email=email,
                    is_admin=is_admin)
        self.session.add(user)
        transaction.commit()

    def interactive(self, encoding='utf-8'):
        """An interactive program that asks for the new user's
        details: login, password, etc.
        """
        info = {}
        while 1:
            login = raw_input('Login:')
            login = unicode(login, encoding)
            if self.session.query(User).filter_by(login=login).count():
                self.print_err('This login is already used. Please '
                               'choose another one.')
            else:
                break
        return info

def main():
    return sys.exit(AddUser().run())


if __name__ == '__main__':
    main()
