import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from schemas.item import Item, ItemCreate, ItemUpdate
from repositories.items_repo import load_all, save_all


def list_items() -> List[Item]:
    return [Item(**it) for it in load_all()]

def create_item(payload: ItemCreate) -> Item:
    items = load_all()
    new_id = str(uuid.uuid4())
    if any(it.get("id") == new_id for it in items):  # extremely unlikely, but consistent check
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    new_item = Item(id=new_id, title=payload.title.strip(), category=payload.category.strip(), tags=payload.tags)
    items.append(new_item.dict())
    save_all(items)
    return new_item

def get_item_by_id(item_id: str) -> Item:
    items = load_all()
    for it in items:
        if it.get("id") == item_id:
            return Item(**it)
    raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")

def update_item(item_id: str, payload: ItemUpdate) -> Item:
    items = load_all()
    for idx, it in enumerate(items):
        if it.get("id") == item_id:
            updated = Item(
                id=item_id,
                title=payload.title.strip(),
                category=payload.category.strip(),
                tags=payload.tags,
            )
            items[idx] = updated.dict()
            save_all(items)
            return updated
    raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")

def delete_item(item_id: str) -> None:
    items = load_all()
    new_items = [it for it in items if it.get("id") != item_id]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")
    save_all(new_items)

