from datetime import datetime
from typing import Generator
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.domain.category import Category
from src.infra.elasticsearch import ELASTICSEARCH_HOST_TEST
from src.infra.elasticsearch.elasticsearch_category_repository import ElasticsearchCategoryRepository

from src.domain.cast_member import CastMember
from src.infra.elasticsearch.elasticsearch_cast_member_repository import ElasticsearchCastMemberRepository


@pytest.fixture
def es() -> Generator[Elasticsearch, None, None]:
    client = Elasticsearch(hosts=[ELASTICSEARCH_HOST_TEST])

    if not client.indices.exists(index=ElasticsearchCategoryRepository.INDEX):
        client.indices.create(index=ElasticsearchCategoryRepository.INDEX)
    if not client.indices.exists(index=ElasticsearchCastMemberRepository.INDEX):
        client.indices.create(index=ElasticsearchCastMemberRepository.INDEX)

    yield client

    client.indices.delete(index=ElasticsearchCategoryRepository.INDEX)
    client.indices.delete(index=ElasticsearchCastMemberRepository.INDEX)


@pytest.fixture
def movie() -> Category:
    return Category(
        id=uuid4(),
        name="Filme",
        description="Categoria de filmes",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def series() -> Category:
    return Category(
        id=uuid4(),
        name="Séries",
        description="Categoria de séries",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def documentary() -> Category:
    return Category(
        id=uuid4(),
        name="Documentários",
        description="Categoria de documentários",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )
    

@pytest.fixture
def actor() -> CastMember:
    return CastMember(
        id=uuid4(),
        name="Alf",
        type='ACTOR',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def director() -> CastMember:
    return CastMember(
        id=uuid4(),
        name="Benny",
        type='DIRECTOR',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def director2() -> CastMember:
    return CastMember(
        id=uuid4(),
        name="Doug",
        type='DIRECTOR',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def populated_es(
    es: Elasticsearch,
    movie: Category,
    series: Category,
    documentary: Category,
    actor: CastMember,
    director: CastMember,
    director2: CastMember,
) -> Elasticsearch:
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(movie.id),
        body=movie.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(series.id),
        body=series.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCategoryRepository.INDEX,
        id=str(documentary.id),
        body=documentary.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCastMemberRepository.INDEX,
        id=str(actor.id),
        body=actor.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCastMemberRepository.INDEX,
        id=str(director.id),
        body=director.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchCastMemberRepository.INDEX,
        id=str(director2.id),
        body=director2.model_dump(mode="json"),
        refresh=True,
    )

    return es