"""
NOTE: on using peewee for non-integer primary_key

```python
# This works because .create() will specify `force_insert=True`.
obj1 = UUIDModel.create(id=uuid.uuid4())

# This will not work, however. Peewee will attempt to do an update:
obj2 = UUIDModel(id=uuid.uuid4())
obj2.save() # WRONG

obj2.save(force_insert=True) # CORRECT

# Once the object has been created, you can call save() normally.
obj2.save()
```

Read more: http://docs.peewee-orm.com/en/latest/peewee/models.html?highlight=force_insert#id4
"""

from .exceptions import TableDoesNotExist
from .models import DbMetadata, Migration, ReadingHistory, db


def initial_migration() -> None:
    db.create_tables([DbMetadata, ReadingHistory])


MIGRATIONS: list[Migration] = [
    Migration(version=0, migrate=initial_migration),
]


def migrate() -> None:
    db.connect()
    try:
        for migration in sorted(MIGRATIONS, key=lambda x: x.version):
            try:
                if not DbMetadata.table_exists():
                    raise TableDoesNotExist
                DbMetadata.get_by_id(migration.version)
            except (DbMetadata.DoesNotExist, TableDoesNotExist):
                migration.migrate()
                DbMetadata.create(version=migration.version)
    finally:
        db.close()
