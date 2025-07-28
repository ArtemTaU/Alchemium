# Async SQLAlchemy CRUD Library

A modular and extensible library for building high-quality, maintainable CRUD operations using **SQLAlchemy** and the Unit of Work (UoW) pattern.  
Supports both **asynchronous** workflows and standardized exception handling for robust production code.

---

## Key Features

- **Async-first**: All operations are built around `AsyncSession` and async/await syntax.
- **Unit of Work**: Centralized transaction management via [UnitOfWork](src/uow/session.py).
- **Reusable CRUD Mixins**: Pluggable mixins for [Create](src/mixins/create.py), [Read](src/mixins/read.py), [Update](src/mixins/update.py), [Delete](src/mixins/delete.py) and general [GRUD](src/mixins/base.py) mixin.
- **Strict Session Control**: Automatic session validation and lifecycle management (commit, flush, rollback).
- **Type Annotations**: All public interfaces are fully type-annotated for IDE support.

---
## Quick Start: CRUD Operations Example

Before starting, suppose you have these SQLAlchemy models:

```python
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    position = Column(String)
```
The only step to use **Alchemium** is to declare a Repository
```python
from alchemium import CrudRepository

class UserRepository(CrudRepository):
    model = User
```
Now you can easily use CRUD methods inside UnitOfWork
```python
from alchemium import UnitOfWork

async with UnitOfWork(session_factory) as uow:
    # CREATE
    user = await UserRepository.create(uow.session, {
        "name": "Alice",
        "position": "Engineer"
    })
    await uow.flush()  # flush to assign IDs if needed

    # READ
    found_user = await UserRepository.get_one(
        asession=uow.session,
        filters={"name": "Alice"}
    )

    # UPDATE
    await UserRepository.update(
        obj=user,
        data={"position": "Team Lead"}
    )

    # DELETE
    await UserRepository.delete(uow.session, user)
```
Transaction will be closed automatically or raise Exception whenever the session is finished.


---

## Architecture Overview

- **UnitOfWork**  
  Manages the session and transaction lifecycle. Designed to be used as an async context manager:
  ```python
  async with UnitOfWork(session_factory) as uow:
      # Use uow.session for DB operations
      ...
  ```