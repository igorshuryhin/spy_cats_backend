from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import Mission, Target, Cat
from database import get_session
from schemas import (
    CreateMission, MissionOut, AssignCatToMission,
    UpdateTargetNotes, MarkTargetComplete, TargetOut
)

router = APIRouter(prefix="/api/missions", tags=["Missions"])


@router.post("/", response_model=MissionOut)
async def create_mission(mission: CreateMission, db: AsyncSession = Depends(get_session)):
    db_mission = Mission(name=mission.name)
    db.add(db_mission)
    await db.flush()

    for t in mission.targets:
        db_target = Target(
            name=t.name,
            country=t.country,
            notes=t.notes,
            mission_id=db_mission.id
        )
        db.add(db_target)

    await db.commit()

    result = await db.execute(
        select(Mission)
        .options(selectinload(Mission.targets))
        .where(Mission.id == db_mission.id)
    )
    full_mission = result.scalar_one()
    return full_mission


@router.get("/", response_model=list[MissionOut])
async def list_missions(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Mission)
        .options(
            selectinload(Mission.targets),
            selectinload(Mission.cat)
        )
    )
    missions = result.scalars().all()
    return missions


@router.get("/{mission_id}", response_model=MissionOut)
async def get_mission(mission_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Mission)
        .options(selectinload(Mission.targets), selectinload(Mission.cat))
        .where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.delete("/{mission_id}")
async def delete_mission(mission_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Mission).where(Mission.id == mission_id))
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if mission.cat_id:
        raise HTTPException(status_code=400, detail="Cannot delete assigned mission")

    await db.delete(mission)
    await db.commit()
    return {"detail": "Mission deleted"}


from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


@router.post("/{mission_id}/assign")
async def assign_cat(
    mission_id: int,
    assign: AssignCatToMission,
    db: AsyncSession = Depends(get_session)
):
    mission = await db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    if mission.cat_id:
        raise HTTPException(status_code=400, detail="Mission already assigned")

    result = await db.execute(
        select(Cat)
        .options(selectinload(Cat.mission))
        .where(Cat.id == assign.cat_id)
    )
    cat = result.scalar_one_or_none()

    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")

    if cat.mission:
        raise HTTPException(status_code=400, detail="Cat already has a mission")

    mission.cat_id = cat.id

    await db.commit()
    await db.refresh(mission)
    return {"detail": "Cat assigned to mission"}



@router.put("/targets/{target_id}/notes", response_model=TargetOut)
async def update_target_notes(target_id: int, payload: UpdateTargetNotes, db: AsyncSession = Depends(get_session)):
    target = await db.get(Target, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    mission = await db.get(Mission, target.mission_id)
    if mission.is_complete or target.is_complete:
        raise HTTPException(status_code=400, detail="Cannot update notes on completed mission/target")

    target.notes = payload.notes
    await db.commit()
    await db.refresh(target)
    return target


@router.put("/targets/{target_id}/complete", response_model=TargetOut)
async def complete_target(target_id: int, payload: MarkTargetComplete, db: AsyncSession = Depends(get_session)):
    target = await db.get(Target, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    mission = await db.get(Mission, target.mission_id)
    if mission.is_complete:
        raise HTTPException(status_code=400, detail="Mission already complete")

    target.is_complete = payload.is_complete
    await db.commit()
    await db.refresh(target)

    # Check if all targets complete → mark mission complete
    result = await db.execute(
        select(Target).where(Target.mission_id == mission.id)
    )
    targets = result.scalars().all()
    if all(t.is_complete for t in targets):
        mission.is_complete = True
        await db.commit()

    return target
