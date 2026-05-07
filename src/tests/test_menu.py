import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_menu(client: AsyncClient):
    """Создание меню"""
    response = await client.post(
        "/api/v1/menus/",
        json={
            "title": "Тестовое меню",
            "description": "Описание тестового меню"
        }
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert data["title"] == "Тестовое меню", "Title mismatch"
    assert data["description"] == "Описание тестового меню", "Description mismatch"
    assert "id" in data, "Response missing 'id' field"
    assert data["submenus_count"] == 0, "submenus_count should be 0"
    assert data["dishes_count"] == 0, "dishes_count should be 0"


@pytest.mark.asyncio
async def test_get_menus(client: AsyncClient):
    """Получение списка меню"""
    # Создаем два меню
    await client.post("/api/v1/menus/", json={"title": "Меню 1", "description": "Описание 1"})
    await client.post("/api/v1/menus/", json={"title": "Меню 2", "description": "Описание 2"})
    
    response = await client.get("/api/v1/menus/")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert len(data) == 2, f"Expected 2 menus, got {len(data)}"


@pytest.mark.asyncio
async def test_get_menu_by_id(client: AsyncClient):
    """Получение меню по ID"""
    # Создаем меню
    create_response = await client.post(
        "/api/v1/menus/",
        json={"title": "Меню для поиска", "description": "Описание"}
    )
    menu_id = create_response.json()["id"]
    
    # Получаем по ID
    response = await client.get(f"/api/v1/menus/{menu_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["id"] == menu_id, "ID mismatch"
    assert data["title"] == "Меню для поиска", "Title mismatch"


@pytest.mark.asyncio
async def test_get_nonexistent_menu(client: AsyncClient):
    """Получение несуществующего меню"""
    response = await client.get("/api/v1/menus/nonexistent-id")
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    assert response.json()["detail"] == "menu not found"


@pytest.mark.asyncio
async def test_update_menu(client: AsyncClient):
    """Обновление меню"""
    # Создаем меню
    create_response = await client.post(
        "/api/v1/menus/",
        json={"title": "Старое название", "description": "Старое описание"}
    )
    menu_id = create_response.json()["id"]
    
    # Обновляем
    response = await client.patch(
        f"/api/v1/menus/{menu_id}",
        json={"title": "Новое название", "description": "Новое описание"}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["title"] == "Новое название", "Title not updated"
    assert data["description"] == "Новое описание", "Description not updated"


@pytest.mark.asyncio
async def test_delete_menu(client: AsyncClient):
    """Удаление меню"""
    # Создаем меню
    create_response = await client.post(
        "/api/v1/menus/",
        json={"title": "Меню для удаления", "description": "Описание"}
    )
    menu_id = create_response.json()["id"]
    
    # Удаляем
    response = await client.delete(f"/api/v1/menus/{menu_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json()["status"] == True, "Status should be True"
    
    # Проверяем, что удалилось
    get_response = await client.get(f"/api/v1/menus/{menu_id}")
    assert get_response.status_code == 404, "Menu should not exist after deletion"
