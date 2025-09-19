from datetime import datetime
from typing import Generator
from uuid import uuid4

import pytest
from elasticsearch import Elasticsearch

from src.application.list_cast_member import CastMemberSortableFields, ListCastMember, ListCastMemberInput
from src.application.listing import ListOutputMeta
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


class TestListCastMember:
    def test_list_castmember_with_default_values(
        self,
        populated_es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
        list_castmember = ListCastMember(
            repository=ElasticsearchCastMemberRepository(client=populated_es)
        )
        output = list_castmember.execute(input=ListCastMemberInput())

        assert output.data == [actor, director, director2]  # Ordered by name by default
        assert output.meta == ListOutputMeta(
            page=1,
            per_page=5,
            sort=CastMemberSortableFields.NAME,
            direction=SortDirection.ASC,
        )

    def test_list_cast_member_with_pagination_sorting_and_search(
        self,
        populated_es: Elasticsearch,
        actor: CastMember,
        director: CastMember,
        director2: CastMember,
    ) -> None:
        list_castmember = ListCastMember(
            repository=ElasticsearchCastMemberRepository(client=populated_es)
        )

        # Page 1
        output = list_castmember.execute(
            input=ListCastMemberInput(
                search="Alf",
                sort=CastMemberSortableFields.NAME,
                direction=SortDirection.DESC,
                page=1,
                per_page=1,
            )
        )

        assert output.data == [actor]
        assert output.meta == ListOutputMeta(
            page=1,
            per_page=1,
            sort=CastMemberSortableFields.NAME,
            direction=SortDirection.DESC,
        )

        # Page 2
        output = list_castmember.execute(
            input=ListCastMemberInput(
                search="Alf",
                sort=CastMemberSortableFields.NAME,
                direction=SortDirection.DESC,
                page=2,
                per_page=1,
            )
        )

        assert output.data == []
        assert output.meta == ListOutputMeta(
            page=2,
            per_page=1,
            sort=CastMemberSortableFields.NAME,
            direction=SortDirection.DESC,
        )