
# Async SQLAlchemy CRUD Library  
  
A modular and extensible library for building high-quality, maintainable CRUD operations using **SQLAlchemy** and the Unit of Work (UoW) pattern.    
Async-first: Perfect for FastAPI, aiohttp, and any modern Python 3.8+ async application.
---  
  
## Key Features  
  
- **[UnitOfWork](src/uow/session.py)**: **Automatic transaction management — commit or rollback on context exit. No session leaks.**
- **Repository pattern:** Write business logic once, keep CRUD in reusable mixins.   
- **Async-native:** Built for async/await, scales with your concurrency needs.  
- **Type Annotations:** Full IDE support and safer code. 

## Feature Highlights

| Feature                | Benefit                                        |
| ---------------------- | ---------------------------------------------- |
| Async-first design     | Non-blocking, perfect for FastAPI & async apps |
| Unit of Work pattern   | No session leaks; automatic commit/rollback    |
| Repository abstraction | Clean separation of business and DB logic      |
| Robust error handling  | Transactions are always all-or-nothing         |
| IDE-friendly           | Type annotations for superb auto-completion    |


---  
## Quick Start: CRUD Operations Example  


### Step 1: Configure SQLAlchemy
```python  
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

# Example config (adjust to your needs)
DATABASE_URL = "postgresql+asyncpg://user:password@host:port/dbname"

Base = declarative_base()

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool  # No connection pool (optional, good for tests/migrations)
)

async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
``` 

### Step 2: Create & Migrate Your Models
  
```python  
from sqlalchemy import Column, Integer, String  
from sqlalchemy.orm import declarative_base


Base = declarative_base()  
  
  
class User(Base):  
    __tablename__ = "users"  
    id = Column(Integer, primary_key=True, autoincrement=True)  
    name = Column(String, unique=True)  
    position = Column(String)  
```  
**Do not forget to migrate your models into the database.**  
Create tables (one-time, before first use)
```python
async with engine.begin() as conn:  
    await conn.run_sync(Base.metadata.create_all)
```


### Step 3: Create a Repository
```python  
from alchemium import CrudRepository  
  
class UserRepository(CrudRepository):  
	model = User  
```  
No need to write boilerplate CRUD logic for each model — just set `model` in your repository.

### Step 4: Use CRUD operations inside UnitOfWork
```python  
import asyncio  
  
from alchemium import UnitOfWork  
from database import async_session, engine  
from models import UserRepository, Base, User  
  
  
async def main():  
    # Step 2.1: CREATE
    async with UnitOfWork(async_session) as uow:  
        user: User = await UserRepository.create(uow.session, {  
            "name": "Alice",  
            "position": "Engineer"  
        })  
        # For better IDE auto-completion, use type annotations, e.g. user: User = ...
        # If you need the assigned ID, use flush:
        await uow.flush()
        print(f"Created user with id: {user.id}")
  
    async with UnitOfWork(async_session) as uow:  
        found_user: User = await UserRepository.get_one(  
            asession=uow.session,  
            filters={"name": "Alice"}  
        )  
        print(f"Found user: {found_user.name}")

        UserRepository.update(  
            obj=found_user,  
            data={"position": "Team Lead"}  
        )  
        # You don't need to commit manually: commit/rollback are handled automatically!
     
    # Step 2.3: DELETE
    # You can work with ORM objects outside the original session where they were loaded or created:
    async with UnitOfWork(async_session) as uow:      
        await UserRepository.delete(uow.session, found_user)
        
if __name__ == "__main__":
    asyncio.run(main())
```  
Transaction will be closed automatically or an exception will be raised if the session fails.
    
### **How It Works: Step-by-step Advantages**
**Repository once, reuse everywhere:**
- Inherit from CrudRepository and set model — all CRUD methods ready-to-use.

**Automatic transaction boundaries:**
- No manual commit or rollback needed. Each block is its own safe transaction.

**Session-safe object usage:**
- ORM objects (like user or found_user) can be used across UnitOfWork blocks (sessions).

**Get DB-generated fields instantly:**
- Call await uow.flush() to access values like id before committing.

**Robust async workflows:**
- Fully async from top to bottom — ideal for modern Python frameworks.




### **Step-by-step Explanation & Advantages**
        
4.  **Get Assigned IDs Instantly**
    
    -   If you need to get the database-generated ID after creating an object, simply call:
		`await uow.flush()`
        This makes database-generated fields (e.g. id, timestamp) available before committing the transaction.
        
5.  **Isolated Transactions for Each Step**
    
    -   **Advantage:**  
        Every CRUD operation is isolated and safe:  
        you always know when and where the session starts and ends.
        
6.  **Safe Exception Handling**
    
    -   **Advantage:**  
        If anything fails inside the UnitOfWork block, changes will not be committed — you'll never have a half-applied transaction.
        
7.  **Async-native**
    
    -   The entire workflow is non-blocking and perfect for use in async frameworks and applications.
---

### **Ready to build safe, maintainable async CRUD with minimal boilerplate? Try Alchemium!**

---
