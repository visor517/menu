from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
import models as m
import schemas as s

router = APIRouter()


@router.get(
    "/{menu_id}/submenus/{sub_id}/dishes",
    response_model=List[s.DishResponse],
    status_code=status.HTTP_200_OK,
)
async def read_dishes(
    menu_id: str, sub_id: str, session: AsyncSession = Depends(get_session)
):
    # Проверяем, существует ли подменю
    result = await session.execute(
        select(m.SubMenu).where(
            m.SubMenu.id == sub_id, m.SubMenu.menu_id == menu_id
        )
    )
    submenu = result.scalar_one_or_none()

    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="submenu not found"
        )

    # Получаем все блюда подменю
    result = await session.execute(select(m.Dish).where(m.Dish.sub_menu_id == sub_id))
    dishes = result.scalars().all()

    return [
        s.DishResponse(
            id=dish.id, title=dish.title, description=dish.description, price=dish.price
        )
        for dish in dishes
    ]


@router.get(
    "/{menu_id}/submenus/{sub_id}/dishes/{dish_id}",
    response_model=s.DishResponse,
    status_code=status.HTTP_200_OK,
)
async def read_dish_by_id(
    menu_id: str,
    sub_id: str,
    dish_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(m.Dish).where(
            m.Dish.id == dish_id, m.Dish.sub_menu_id == sub_id
        )
    )
    dish = result.scalar_one_or_none()

    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dish not found"
        )

    return s.DishResponse(
        id=dish.id, title=dish.title, description=dish.description, price=dish.price
    )


@router.post(
    "/{menu_id}/submenus/{sub_id}/dishes",
    response_model=s.DishResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dish(
    menu_id: str,
    sub_id: str,
    request: s.DishRequest,
    session: AsyncSession = Depends(get_session),
):
    # Проверяем, существует ли подменю
    result = await session.execute(
        select(m.SubMenu).where(
            m.SubMenu.id == sub_id, m.SubMenu.menu_id == menu_id
        )
    )
    submenu = result.scalar_one_or_none()

    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="submenu not found"
        )

    uid = str(uuid.uuid1())
    new_dish = m.Dish(
        id=uid,
        sub_menu_id=sub_id,
        title=request.title,
        description=request.description,
        price=request.price,
    )
    session.add(new_dish)
    await session.commit()

    return s.DishResponse(
        id=uid,
        title=request.title,
        description=request.description,
        price=request.price,
    )


@router.patch(
    "/{menu_id}/submenus/{sub_id}/dishes/{dish_id}",
    response_model=s.DishResponse,
    status_code=status.HTTP_200_OK,
)
async def update_dish(
    menu_id: str,
    sub_id: str,
    dish_id: str,
    request: s.DishRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(m.Dish).where(
            m.Dish.id == dish_id, m.Dish.sub_menu_id == sub_id
        )
    )
    dish = result.scalar_one_or_none()

    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dish not found"
        )

    dish.title = request.title
    dish.description = request.description
    dish.price = request.price
    await session.commit()

    return s.DishResponse(
        id=dish.id, title=dish.title, description=dish.description, price=dish.price
    )


@router.delete(
    "/{menu_id}/submenus/{sub_id}/dishes/{dish_id}", status_code=status.HTTP_200_OK
)
async def delete_dish(
    menu_id: str,
    sub_id: str,
    dish_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(m.Dish).where(
            m.Dish.id == dish_id, m.Dish.sub_menu_id == sub_id
        )
    )
    dish = result.scalar_one_or_none()

    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dish not found"
        )

    await session.delete(dish)
    await session.commit()

    return {"status": True, "message": "The dish has been deleted"}
