import logging
from datetime import datetime
from typing import Generator
from unittest.mock import create_autospec
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.domain.cast_member import CastMember
from src.domain.repository import SortDirection
from src.infra.elasticsearch import ELASTICSEARCH_HOST_TEST
from src.infra.elasticsearch.elasticsearch_cast_member_repository import ElasticsearchCastMemberRepository


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
def es() -> Generator[Elasticsearch, None, None]:
    client = Elasticsearch(hosts=[ELASTICSEARCH_HOST_TEST])
    if not client.indices.exists(index=ElasticsearchCastMemberRepository.INDEX):
        client.indices.create(index=ElasticsearchCastMemberRepository.INDEX)

    yield client

    client.indices.delete(index=ElasticsearchCastMemberRepository.INDEX)


@pytest.fixture
def populated_es(
    es: Elasticsearch,
    actor: CastMember,
    director: CastMember,
    director2: CastMember,
) -> Elasticsearch:
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


class TestSearch:
    def test_can_reach_elasticsearch_test_database(self, es: Elasticsearch) -> None:
        assert es.ping()

    def test_when_index_is_empty_then_return_empty_list(
        self,
        es: Elasticsearch,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=es)

        assert repository.search() == []

    def test_when_index_has_cast_members_then_return_mapped_cast_members_with_default_search(
        self,
        populated_es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=populated_es)

        cast_members = repository.search()

        assert cast_members == [actor, director, director2]

    def test_when_index_has_malformed_cast_members_then_return_valid_cast_members_and_log_error(
        self,
        es: Elasticsearch,
        actor: CastMember,
    ) -> None:
        es.index(
            index=ElasticsearchCastMemberRepository.INDEX,
            id=str(actor.id),
            body=actor.model_dump(mode="json"),
            refresh=True,
        )
        es.index(
            index=ElasticsearchCastMemberRepository.INDEX,
            id=str(uuid4()),
            body={"name": "Malformed"},
            refresh=True,
        )
        mock_logger = create_autospec(logging.Logger)
        repository = ElasticsearchCastMemberRepository(client=es, logger=mock_logger)

        cast_members = repository.search()

        assert cast_members == [actor]
        mock_logger.error.assert_called_once()

    def test_when_search_term_matches_cast_member_name_then_return_matching_entities(
        self,
        populated_es: Elasticsearch,
        actor: CastMember,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=populated_es)

        cast_members = repository.search(search="Alf")

        assert cast_members == [actor]

    def test_search_term_matches_name(
        self,
        populated_es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=populated_es)

        cast_members = repository.search(search="Benny")

        assert cast_members == [director]

    def test_search_is_case_insensitive(
        self,
        populated_es: Elasticsearch,
        actor: CastMember,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=populated_es)

        cast_members = repository.search(search="alf")

        assert cast_members == [actor]

    def test_search_by_non_existent_term_then_return_empty_list(
        self,
        populated_es: Elasticsearch,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=populated_es)

        cast_members = repository.search(search="Non-existent")

        assert cast_members == []


class TestOrdering:
    def test_when_no_sorting_is_specified_then_return_cast_members_ordered_by_insertion_order(
        self,
        es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
        es.index(
            index=ElasticsearchCastMemberRepository.INDEX,
            body=director.model_dump(mode="json"),
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
            id=str(director2.id),
            body=director2.model_dump(mode="json"),
            refresh=True,
        )
        repository = ElasticsearchCastMemberRepository(client=es)

        cast_members = repository.search()

        assert cast_members == [director, actor, director2]

    def test_return_cast_members_ordered_by_name_asc(
        self,
        es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
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
        repository = ElasticsearchCastMemberRepository(client=es)

        cast_members = repository.search(sort="name", direction=SortDirection.ASC)

        assert cast_members == [actor, director, director2]

    def test_return_cast_members_ordered_by_name_desc(
        self,
        es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
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
        repository = ElasticsearchCastMemberRepository(client=es)

        cast_members = repository.search(sort="name", direction=SortDirection.DESC)

        assert cast_members == [director2, director, actor]


class TestPagination:
    def test_when_no_page_is_requested_then_return_default_paginated_response(
        self,
        populated_es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=populated_es)

        cast_members = repository.search(sort="name")

        assert cast_members == [actor, director, director2]

    def test_when_page_is_requested_then_return_expected_paginated_response(
        self,
        populated_es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=populated_es)

        # Page 1
        cast_members = repository.search(sort="name", page=1, per_page=2)
        assert cast_members == [actor, director]

        # Page 2
        cast_members = repository.search(sort="name", page=2, per_page=2)
        assert cast_members == [director2]

    def test_when_requested_page_is_out_of_bounds_then_return_empty_list(
        self,
        populated_es: Elasticsearch,
    ) -> None:
        repository = ElasticsearchCastMemberRepository(client=populated_es)

        cast_members = repository.search(sort="name", page=100, per_page=5)

        assert cast_members == []