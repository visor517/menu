from fastapi import APIRouter

from api import menu, sub_menu, dish


router = APIRouter(prefix="/api/v1")

router.include_router(menu.router, prefix="/menus", tags=["menus"])
router.include_router(sub_menu.router, prefix="/menus", tags=["submenus"])
router.include_router(dish.router, prefix="/menus", tags=["dishes"])
