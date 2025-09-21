from typing import Iterator

import pytest
from elasticsearch import Elasticsearch
from fastapi.testclient import TestClient

from src.domain.genre import Genre
from src.domain.genre_repository import GenreRepository
from src.infra.api.http.main import app
from src.infra.api.http.dependencies import get_genre_repository
from src.infra.elasticsearch.elasticsearch_genre_repository import (
    ElasticsearchGenreRepository,
)


@pytest.fixture
def populated_genre_repository(
    populated_es: Elasticsearch,
) -> Iterator[GenreRepository]:
    yield ElasticsearchGenreRepository(client=populated_es)


@pytest.fixture
def test_client_with_populated_repo(
    populated_genre_repository: GenreRepository,
) -> Iterator[TestClient]:
    app.dependency_overrides[get_genre_repository] = lambda: populated_genre_repository
    yield TestClient(app)
    app.dependency_overrides.clear()


def normalize_categories(payload: dict) -> dict:
    """Converte a lista de categories em set, já que no domínio é um conjunto."""
    for item in payload["data"]:
        item["categories"] = set(item["categories"])
    return payload


def test_list_genres(
    test_client_with_populated_repo,
    romance,
    drama,
    movie,
    documentary,
):
    response = test_client_with_populated_repo.get("/genres")
    assert response.status_code == 200

    expected = {
        "data": [
            {
                "id": str(drama.id),
                "name": drama.name,
                "categories": {str(movie.id), str(documentary.id)},
                "created_at": drama.created_at.isoformat(),
                "updated_at": drama.updated_at.isoformat(),
                "is_active": drama.is_active,
            },
            {
                "id": str(romance.id),
                "name": romance.name,
                "categories": set(),
                "created_at": romance.created_at.isoformat(),
                "updated_at": romance.updated_at.isoformat(),
                "is_active": romance.is_active,
            },
        ],
        "meta": {
            "page": 1,
            "per_page": 5,
            "sort": "name",
            "direction": "asc",
        },
    }

    assert normalize_categories(response.json()) == expected
