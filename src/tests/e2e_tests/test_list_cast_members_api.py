from typing import Iterator

import pytest
from elasticsearch import Elasticsearch
from fastapi.testclient import TestClient

from src.domain.cast_member import CastMember
from src.domain.cast_member_repository import CastMemberRepository
from src.infra.api.http.auth import authenticate
from src.infra.api.http.main import app
from src.infra.api.http.dependencies import get_cast_member_repository
from src.infra.elasticsearch.elasticsearch_cast_member_repository import (
    ElasticsearchCastMemberRepository,
)


@pytest.fixture
def populated_cast_member_repository(
    populated_es: Elasticsearch,
) -> Iterator[CastMemberRepository]:
    yield ElasticsearchCastMemberRepository(client=populated_es)


@pytest.fixture
def test_client_with_populated_repo(
    populated_cast_member_repository: CastMemberRepository,
) -> Iterator[TestClient]:
    app.dependency_overrides[get_cast_member_repository] = lambda: populated_cast_member_repository
    app.dependency_overrides[authenticate] = lambda: None
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_cast_members(
    test_client_with_populated_repo: TestClient,
    actor: CastMember,
    director: CastMember,
    director2: CastMember,
) -> None:
    response = test_client_with_populated_repo.get("/cast_members")
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "id": str(actor.id),
                "name": actor.name,
                "type": actor.type,
                "created_at": actor.created_at.isoformat(),
                "updated_at": actor.updated_at.isoformat(),
                "is_active": actor.is_active,
            },
            {
                "id": str(director.id),
                "name": director.name,
                "type": director.type,
                "created_at": director.created_at.isoformat(),
                "updated_at": director.updated_at.isoformat(),
                "is_active": director.is_active,
            },
            {
                "id": str(director2.id),
                "name": director2.name,
                "type": director2.type,
                "created_at": director2.created_at.isoformat(),
                "updated_at": director2.updated_at.isoformat(),
                "is_active": director2.is_active,
            },
        ],
        "meta": {
            "page": 1,
            "per_page": 5,
            "sort": "name",
            "direction": "asc",
        },
    }