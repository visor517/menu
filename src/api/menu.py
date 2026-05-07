from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
import models as m
import schemas as s

router = APIRouter()


async def count_extra_params(session: AsyncSession, menu_id: str):
    """Подсчет подменю"""
    result = await session.execute(
        select(func.count())
        .select_from(m.SubMenu)
        .where(m.SubMenu.menu_id == menu_id)
    )
    submenus_count = result.scalar_one()

    # Подсчет блюд через подменю
    result = await session.execute(
        select(func.count())
        .select_from(m.Dish)
        .join(m.SubMenu)
        .where(m.SubMenu.menu_id == menu_id)
    )
    dishes_count = result.scalar_one()

    return (submenus_count, dishes_count)


@router.get("/", response_model=List[s.MenuResponse])
async def read_menus(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(m.Menu))
    menus = result.scalars().all()

    response: List[s.MenuResponse] = []
    for menu in menus:
        submenus_count, dishes_count = await count_extra_params(session, menu.id)
        response.append(
            s.MenuResponse(
                id=menu.id,
                title=menu.title,
                description=menu.description,
                submenus_count=submenus_count,
                dishes_count=dishes_count,
            )
        )

    return response


@router.get("/{menu_id}", response_model=s.MenuResponse)
async def read_menu_by_id(menu_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(m.Menu).where(m.Menu.id == menu_id))
    menu = result.scalar_one_or_none()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="menu not found"
        )

    submenus_count, dishes_count = await count_extra_params(session, menu_id)

    return s.MenuResponse(
        id=menu.id,
        title=menu.title,
        description=menu.description,
        submenus_count=submenus_count,
        dishes_count=dishes_count,
    )


@router.post("/", response_model=s.MenuResponse, status_code=status.HTTP_201_CREATED)
async def create_menu(
    request: s.MenuRequest, session: AsyncSession = Depends(get_session)
):
    uid = str(uuid.uuid1())

    new_menu = m.Menu(
        id=uid,
        title=request.title,
        description=request.description,
    )
    session.add(new_menu)
    await session.commit()

    return s.MenuResponse(
        id=uid,
        title=request.title,
        description=request.description,
        submenus_count=0,
        dishes_count=0,
    )


@router.patch(
    "/{menu_id}", response_model=s.MenuResponse, status_code=status.HTTP_200_OK
)
async def update_menu(
    menu_id: str, request: s.MenuRequest, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(m.Menu).where(m.Menu.id == menu_id))
    menu = result.scalar_one_or_none()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="menu not found"
        )

    menu.title = request.title
    menu.description = request.description
    await session.commit()

    submenus_count, dishes_count = await count_extra_params(session, menu_id)

    return s.MenuResponse(
        id=menu.id,
        title=menu.title,
        description=menu.description,
        submenus_count=submenus_count,
        dishes_count=dishes_count,
    )


@router.delete("/{menu_id}", status_code=status.HTTP_200_OK)
async def delete_menu(menu_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(m.Menu).where(m.Menu.id == menu_id))
    menu = result.scalar_one_or_none()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="menu not found"
        )

    await session.delete(menu)
    await session.commit()

    return {"status": True, "message": "The menu has been deleted"}
