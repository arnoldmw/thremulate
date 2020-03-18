from aiohttp_security.abc import AbstractAuthorizationPolicy

from db.database import *


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        try:
            user = User.get(User.id == identity)

            if user.disabled:
                return None
            else:
                return identity

        except User.DoesNotExist:
            return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False

        try:
            user = User.get(User.id == identity)

            if user.disabled is False:
                is_superuser = user.is_superuser
                if is_superuser:
                    return True

                permissions = user.userpermissions
                if permissions.count() == 0:
                    return False

                for record in permissions:
                    if record.perm_id.name == permission:
                        return True

            return False

        except User.DoesNotExist:
            # Should be an error at this point. How did a non existent user get here?
            return False


def check_credentials(email, password):
    try:
        user = User.get(User.email == email)

        if check_password_hash(password, user.passwd):
            return True
        else:
            return False

    except User.DoesNotExist:
        return False


def check_password_hash(plain_password, password_hash):
    plain_password_bin = plain_password.encode('utf-8')
    password_hash_bin = password_hash.encode('utf-8')
    is_correct = bcrypt.checkpw(plain_password_bin, password_hash_bin)
    return is_correct


def generate_password_hash(password):
    password_bin = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt())
    return hashed.decode('utf-8')
