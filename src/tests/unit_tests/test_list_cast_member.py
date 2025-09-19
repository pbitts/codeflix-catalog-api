from datetime import datetime
from unittest.mock import create_autospec
from uuid import uuid4

import pytest

from src.application.list_cast_member import ListCastMember, ListCastMemberInput
from src.application.listing import ListOutputMeta, SortDirection
from src.domain.cast_member import CastMember
from src.domain.cast_member_repository import CastMemberRepository


class TestListCastMember:
    @pytest.fixture
    def actor(self) -> CastMember:
        return CastMember(
            id=uuid4(),
            name="Ailton",
            type='ACTOR',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

    @pytest.fixture
    def director(self) -> CastMember:
        return CastMember(
            id=uuid4(),
            name="Diana",
            type='DIRECTOR',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

    def test_list_cast_member_with_default_values(
        self,
        actor: CastMember,
        director: CastMember,
    ) -> None:
        repository = create_autospec(CastMemberRepository)
        repository.search.return_value = [actor, director]

        list_cast_member = ListCastMember(repository)
        output = list_cast_member.execute(input=ListCastMemberInput())

        assert output.data == [actor, director]
        assert output.meta == ListOutputMeta(
            page=1,
            per_page=5,
            sort="name",
            direction=SortDirection.ASC,
        )
        repository.search.assert_called_once_with(
            page=1,
            per_page=5,
            search=None,
            sort="name",
            direction="asc",
        )

    def test_list_with_invalid_sort_field_raises_error(self) -> None:
        repository = create_autospec(CastMemberRepository)
        list_cast_member = ListCastMember(repository)

        with pytest.raises(ValueError) as err:
            list_cast_member.execute(
                input=ListCastMemberInput(sort="invalid_field")  # type: ignore
            )

        assert "Input should be 'name'" in str(err.value)