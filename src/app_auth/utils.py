def is_read_only_user(user, perm):
    if not(user.is_authenticated) or not(user.is_admin or user.is_staff or user.has_perm(perm)):
            return True
    else:
        return False