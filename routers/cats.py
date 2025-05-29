from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Cat
from database import get_session
from schemas import CreateCat, CatOut, UpdateCatSalary

router = APIRouter(prefix="/api/cats", tags=["Cats"])


@router.post("/", response_model=CatOut)
async def create_cat(cat: CreateCat, db: AsyncSession = Depends(get_session)):
    db_cat = Cat(**cat.dict())
    db.add(db_cat)
    await db.commit()
    await db.refresh(db_cat)
    return db_cat


@router.get("/", response_model=list[CatOut])
async def list_cats(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Cat))
    cats = result.scalars().all()
    return cats


@router.get("/{cat_id}", response_model=CatOut)
async def get_cat(cat_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Cat).where(Cat.id == cat_id))
    cat = result.scalar_one_or_none()
    if cat is None:
        raise HTTPException(status_code=404, detail="Cat not found")
    return cat


@router.put("/{cat_id}/salary", response_model=CatOut)
async def update_salary(cat_id: int, salary_update: UpdateCatSalary, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Cat).where(Cat.id == cat_id))
    cat = result.scalar_one_or_none()
    if cat is None:
        raise HTTPException(status_code=404, detail="Cat not found")

    cat.salary = salary_update.salary
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/{cat_id}")
async def delete_cat(cat_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Cat).where(Cat.id == cat_id))
    cat = result.scalar_one_or_none()
    if cat is None:
        raise HTTPException(status_code=404, detail="Cat not found")

    await db.delete(cat)
    await db.commit()
    return {"detail": "Cat deleted"}
