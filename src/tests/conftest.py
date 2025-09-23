from datetime import datetime
from typing import Generator
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.domain.genre import Genre
from src.domain.cast_member import CastMember
from src.domain.category import Category
from src.infra.elasticsearch import ELASTICSEARCH_HOST_TEST
from src.infra.elasticsearch.elasticsearch_genre_repository import ElasticsearchGenreRepository
from src.infra.elasticsearch.elasticsearch_cast_member_repository import ElasticsearchCastMemberRepository
from src.infra.elasticsearch.elasticsearch_category_repository import ElasticsearchCategoryRepository


@pytest.fixture
def es() -> Generator[Elasticsearch, None, None]:
    client = Elasticsearch(hosts=[ELASTICSEARCH_HOST_TEST])

    if not client.indices.exists(index=ElasticsearchCategoryRepository.INDEX):
        client.indices.create(index=ElasticsearchCategoryRepository.INDEX)
    if not client.indices.exists(index=ElasticsearchCastMemberRepository.INDEX):
        client.indices.create(index=ElasticsearchCastMemberRepository.INDEX)
    if not client.indices.exists(index=ElasticsearchGenreRepository.INDEX):
        client.indices.create(index=ElasticsearchGenreRepository.INDEX)

    yield client

    client.indices.delete(index=ElasticsearchGenreRepository.INDEX)
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
def drama(movie: Category, documentary: Category) -> Genre:
    return Genre(
        id=uuid4(),
        name="Drama",
        categories={movie.id, documentary.id},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def romance() -> Genre:
    return Genre(
        id=uuid4(),
        name="Romance",
        categories=set(),
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
    drama: Genre,
    romance: Genre,
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
    
     # Genre
    es.index(
        index=ElasticsearchGenreRepository.INDEX,
        id=str(drama.id),
        body=drama.model_dump(mode="json"),
        refresh=True,
    )
    es.index(
        index=ElasticsearchGenreRepository.INDEX,
        id=str(romance.id),
        body=romance.model_dump(mode="json"),
        refresh=True,
    )

    # Drama categories
    es.index(
        index=ElasticsearchGenreRepository._GENRE_CATEGORIES_INDEX,
        id=str(uuid4()),
        body={
            "genre_id": str(drama.id),
            "category_id": str(movie.id),
        },
        refresh=True,
    )
    es.index(
        index=ElasticsearchGenreRepository._GENRE_CATEGORIES_INDEX,
        id=str(uuid4()),
        body={
            "genre_id": str(drama.id),
            "category_id": str(documentary.id),
        },
        refresh=True,
    )

    return es