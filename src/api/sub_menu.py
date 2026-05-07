from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
import models as m
import schemas as s

router = APIRouter()


@router.get(
    "/{menu_id}/submenus",
    response_model=List[s.SubMenuResponse],
    status_code=status.HTTP_200_OK,
)
async def read_sub_menus(menu_id: str, session: AsyncSession = Depends(get_session)):
    # Проверяем, существует ли меню
    result = await session.execute(select(m.Menu).where(m.Menu.id == menu_id))
    menu = result.scalar_one_or_none()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="menu not found"
        )

    # Получаем все подменю меню
    result = await session.execute(
        select(m.SubMenu).where(m.SubMenu.menu_id == menu_id)
    )
    sub_menus = result.scalars().all()

    response = []
    for sub_menu in sub_menus:
        dishes_count = await count_dishes(session, sub_menu.id)
        response.append(
            s.SubMenuResponse(
                id=sub_menu.id,
                title=sub_menu.title,
                description=sub_menu.description,
                dishes_count=dishes_count,
            )
        )

    return response


@router.get(
    "/{menu_id}/submenus/{sub_id}",
    response_model=s.SubMenuResponse,
    status_code=status.HTTP_200_OK,
)
async def read_sub_menu_by_id(
    menu_id: str, sub_id: str, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(m.SubMenu).where(
            m.SubMenu.id == sub_id, m.SubMenu.menu_id == menu_id
        )
    )
    sub_menu = result.scalar_one_or_none()

    if not sub_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="submenu not found"
        )

    dishes_count = await count_dishes(session, sub_id)

    return s.SubMenuResponse(
        id=sub_menu.id,
        title=sub_menu.title,
        description=sub_menu.description,
        dishes_count=dishes_count,
    )


@router.post(
    "/{menu_id}/submenus",
    response_model=s.SubMenuResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sub_menu(
    menu_id: str,
    request: s.SubMenuRequest,
    session: AsyncSession = Depends(get_session),
):
    # Проверяем, существует ли меню
    result = await session.execute(select(m.Menu).where(m.Menu.id == menu_id))
    menu = result.scalar_one_or_none()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="menu not found"
        )

    uid = str(uuid.uuid1())
    new_sub_menu = m.SubMenu(
        id=uid,
        menu_id=menu_id,
        title=request.title,
        description=request.description,
    )
    session.add(new_sub_menu)
    await session.commit()

    return s.SubMenuResponse(
        id=uid,
        title=request.title,
        description=request.description,
        dishes_count=0,
    )


@router.patch(
    "/{menu_id}/submenus/{sub_id}",
    response_model=s.SubMenuResponse,
    status_code=status.HTTP_200_OK,
)
async def update_sub_menu(
    menu_id: str,
    sub_id: str,
    request: s.SubMenuRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(m.SubMenu).where(
            m.SubMenu.id == sub_id, m.SubMenu.menu_id == menu_id
        )
    )
    sub_menu = result.scalar_one_or_none()

    if not sub_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="submenu not found"
        )

    sub_menu.title = request.title
    sub_menu.description = request.description
    await session.commit()

    dishes_count = await count_dishes(session, sub_id)

    return s.SubMenuResponse(
        id=sub_menu.id,
        title=sub_menu.title,
        description=sub_menu.description,
        dishes_count=dishes_count,
    )


@router.delete("/{menu_id}/submenus/{sub_id}", status_code=status.HTTP_200_OK)
async def delete_sub_menu(
    menu_id: str, sub_id: str, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(m.SubMenu).where(
            m.SubMenu.id == sub_id, m.SubMenu.menu_id == menu_id
        )
    )
    sub_menu = result.scalar_one_or_none()

    if not sub_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="submenu not found"
        )

    await session.delete(sub_menu)
    await session.commit()

    return {"status": True, "message": "The submenu has been deleted"}


async def count_dishes(session: AsyncSession, sub_id: str):
    result = await session.execute(
        select(func.count())
        .select_from(m.Dish)
        .where(m.Dish.sub_menu_id == sub_id)
    )
    return result.scalar_one()
