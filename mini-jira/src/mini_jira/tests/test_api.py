import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_project(async_client: AsyncClient):
    response = await async_client.post("/projects/", json={ "name": "project name", "description": "description" })
    assert response.status_code == 201
    assert response.json()["name"] == "project name"

@pytest.mark.asyncio
async def test_create_task(async_client: AsyncClient):
    response = await async_client.post("/projects/-1/tasks/", json={ "title": "title", "priority": "high" })
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_projects(async_client: AsyncClient):
    response = await async_client.get("/projects/")
    assert response.status_code == 200

    assert len(response.json()) == 0

    response = await async_client.post("/projects/", json={ "name": "project name", "description": "description" })
    assert response.status_code == 201
    project_without_tasks_id = response.json()["id"]

    response = await async_client.get("/projects/")
    assert response.status_code == 200

    assert len(response.json()) == 1

    response = await async_client.post("/projects/", json={ "name": "project 2", "description": "desc" })
    assert response.status_code == 201
    project_with_task_id = response.json()["id"]

    response = await async_client.post(f"/projects/{project_with_task_id}/tasks/", json={ "title": "title", "priority": "high" })
    assert response.status_code == 201

    response = await async_client.get("/projects/")
    assert response.status_code == 200

    projects = { project["id"]: project for project in response.json()}

    assert projects[project_with_task_id]["task_count"] == 1
    assert projects[project_without_tasks_id]["task_count"] == 0
    assert len(response.json()) == 2
