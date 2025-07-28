from ..errors import SessionActivityError


def ensure_active_session(func):
    async def wrapper(self, *args, **kwargs):
        if self.session is None or not self.session.is_active:
            raise SessionActivityError
        return await func(self, *args, **kwargs)

    return wrapper
