from typing import Optional, Union, Dict, Any
from sqlmodel import Session, select, func
from backend.models.models import Item, ItemCreate, ItemUpdate
from fastapi import HTTPException, status


class ItemRepository:
    def get(self, db: Session, id: int) -> Optional[Item]:
        """Retrieves a single item from the database by its primary key ID."""
        return db.get(Item, id)

    def get_by_title_and_owner(
        self, db: Session, *, title: str, owner_id: int
    ) -> Optional[Item]:
        """Fetches an item based on its title and the ID of its owner."""
        return db.exec(
            select(Item).where(Item.title == title, Item.owner_id == owner_id)
        ).first()

    def create_with_owner(
        self, db: Session, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        """Creates a new item in the database, assigning it to a specific owner."""
        db_obj = Item(**obj_in.dict(), owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ):
        """Retrieves all items associated with a specific owner, with options for pagination."""
        return db.exec(
            select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        ).all()

    def del_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ):
        """Deletes all items with null owner_id"""
        
        ### process a delete for every entry in db that is null
        #obj = db.get(Item, db.exec(select(Item.id).where(Item.owner_id == None).offset(skip).limit(limit)))
        obj = db.get(Item, db.exec(select(Item.id).where(Item.owner_id.is_(None)).offset(skip).limit(limit)))
        db.delete(obj)
        db.commit() 
        return obj



    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        """Retrieves a list of all items, with options for pagination."""
        return db.exec(select(Item).offset(skip).limit(limit)).all()

    def update(
        self, db: Session, *, db_obj: Item, obj_in: Union[ItemUpdate, Dict[str, Any]]
    ) -> Item:
        """Updates the attributes of an existing item in the database."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Item:
        """Deletes a specific item from the database by its ID."""
        obj = db.get(Item, id)
        db.delete(obj)
        db.commit()
        return obj


item_repo = ItemRepository()
