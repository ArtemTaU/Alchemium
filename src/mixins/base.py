from .create import CreateMixin
from .delete import DeleteMixin
from .read import ReadMixin
from .update import UpdateMixin


class CrudRepository(CreateMixin, ReadMixin, UpdateMixin, DeleteMixin):
    """A full repository based on CRUD operations."""

    pass
