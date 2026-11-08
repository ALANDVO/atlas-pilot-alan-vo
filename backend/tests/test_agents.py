"""Tests for agents API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Agent
from app.core.security.jwt import create_access_token


@pytest.mark.asyncio
async def test_list_agents_empty(client: AsyncClient):
    """Test listing agents when empty."""
    # Create a test token
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["viewer"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/agents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_create_agent(client: AsyncClient):
    """Test creating an agent."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["operator"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/agents",
        json={
            "name": "Test Agent",
            "slug": "test-agent",
            "description": "A test agent",
            "category": "coding",
            "color": "#FF0000",
            "content": "Agent content here",
            "source_format": "markdown",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["slug"] == "test-agent"
    assert data["description"] == "A test agent"
    assert data["category"] == "coding"
    assert data["color"] == "#FF0000"
    assert data["content"] == "Agent content here"
    assert data["source_format"] == "markdown"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_agent_duplicate_slug(client: AsyncClient):
    """Test creating agent with duplicate slug fails."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["operator"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create first agent
    await client.post(
        "/api/v1/agents",
        json={
            "name": "Agent 1",
            "slug": "test-slug",
            "description": "First",
            "category": "coding",
            "content": "Content",
            "source_format": "markdown",
        },
        headers=auth_headers,
    )

    # Try to create second with same slug
    response = await client.post(
        "/api/v1/agents",
        json={
            "name": "Agent 2",
            "slug": "test-slug",
            "description": "Second",
            "category": "research",
            "content": "Content",
            "source_format": "markdown",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_agent(client: AsyncClient):
    """Test getting an agent by ID."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["viewer"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create agent
    create_resp = await client.post(
        "/api/v1/agents",
        json={
            "name": "Get Test",
            "slug": "get-test",
            "description": "For getting",
            "category": "coding",
            "content": "Content",
            "source_format": "markdown",
        },
        headers=auth_headers,
    )
    agent_id = create_resp.json()["id"]

    # Get agent
    response = await client.get(f"/api/v1/agents/{agent_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == "Get Test"
    assert data["slug"] == "get-test"


@pytest.mark.asyncio
async def test_get_agent_not_found(client: AsyncClient):
    """Test getting non-existent agent returns 404."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["viewer"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/agents/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_agent(client: AsyncClient):
    """Test updating an agent."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["operator"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create agent
    create_resp = await client.post(
        "/api/v1/agents",
        json={
            "name": "Original",
            "slug": "original",
            "description": "Original desc",
            "category": "coding",
            "content": "Original content",
            "source_format": "markdown",
        },
        headers=auth_headers,
    )
    agent_id = create_resp.json()["id"]

    # Update agent
    response = await client.put(
        f"/api/v1/agents/{agent_id}",
        json={
            "name": "Updated",
            "description": "Updated desc",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["description"] == "Updated desc"
    assert data["slug"] == "original"  # unchanged
    assert data["category"] == "coding"  # unchanged


@pytest.mark.asyncio
async def test_update_agent_slug_conflict(client: AsyncClient):
    """Test updating agent slug to existing one fails."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["operator"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create two agents
    await client.post(
        "/api/v1/agents",
        json={"name": "A1", "slug": "a1", "description": "D", "category": "coding", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )
    create_resp = await client.post(
        "/api/v1/agents",
        json={"name": "A2", "slug": "a2", "description": "D", "category": "coding", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )
    agent2_id = create_resp.json()["id"]

    # Try to update A2's slug to A1's slug
    response = await client.put(
        f"/api/v1/agents/{agent2_id}",
        json={"slug": "a1"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_agent(client: AsyncClient):
    """Test deleting an agent."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["operator"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create agent
    create_resp = await client.post(
        "/api/v1/agents",
        json={
            "name": "To Delete",
            "slug": "to-delete",
            "description": "Will be deleted",
            "category": "coding",
            "content": "Content",
            "source_format": "markdown",
        },
        headers=auth_headers,
    )
    agent_id = create_resp.json()["id"]

    # Delete agent
    response = await client.delete(f"/api/v1/agents/{agent_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify deleted
    get_resp = await client.get(f"/api/v1/agents/{agent_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_agents_pagination(client: AsyncClient):
    """Test agent list pagination."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["operator"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Create 5 agents
    for i in range(5):
        await client.post(
            "/api/v1/agents",
            json={
                "name": f"Agent {i}",
                "slug": f"agent-{i}",
                "description": f"Description {i}",
                "category": "coding",
                "content": "Content",
                "source_format": "markdown",
            },
            headers=auth_headers,
        )

    # Page 1 with page_size=2
    response = await client.get("/api/v1/agents?page=1&page_size=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == 5
    assert data["total_pages"] == 3

    # Page 2
    response = await client.get("/api/v1/agents?page=2&page_size=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_list_agents_filter_by_category(client: AsyncClient):
    """Test filtering agents by category."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["operator"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/agents",
        json={"name": "A1", "slug": "a1", "description": "D", "category": "coding", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/agents",
        json={"name": "A2", "slug": "a2", "description": "D", "category": "research", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )

    response = await client.get("/api/v1/agents?category=coding", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "coding"


@pytest.mark.asyncio
async def test_list_agents_search(client: AsyncClient):
    """Test searching agents by name/description."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["operator"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/agents",
        json={"name": "Python Coder", "slug": "py-coder", "description": "Writes Python", "category": "coding", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/agents",
        json={"name": "Researcher", "slug": "researcher", "description": "Does research", "category": "research", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )

    response = await client.get("/api/v1/agents?search=python", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Python" in data["items"][0]["name"]


@pytest.mark.asyncio
async def test_list_categories(client: AsyncClient):
    """Test listing agent categories."""
    token = create_access_token({"sub": "test-user", "preferred_username": "testuser", "realm_access": {"roles": ["viewer"]}})
    auth_headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/agents",
        json={"name": "A1", "slug": "a1", "description": "D", "category": "coding", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/agents",
        json={"name": "A2", "slug": "a2", "description": "D", "category": "research", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/agents",
        json={"name": "A3", "slug": "a3", "description": "D", "category": "coding", "content": "C", "source_format": "markdown"},
        headers=auth_headers,
    )

    response = await client.get("/api/v1/agents/categories", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "coding" in data
    assert "research" in data
    assert len(data) == 2


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test that endpoints require authentication."""
    response = await client.get("/api/v1/agents")
    assert response.status_code == 401

    response = await client.post("/api/v1/agents", json={})
    assert response.status_code == 401


