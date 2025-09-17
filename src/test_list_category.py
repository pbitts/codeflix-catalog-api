from datetime import datetime
from unittest.mock import create_autospec
from uuid import uuid4

import pytest

from src.category import Category
from src.category_repository import CategoryRepository
from src.list_category import ListCategory, ListCategoryInput, ListCategoryOutputMeta, SortableFields


class TestListCategory:
    @pytest.fixture
    def movie_category(self) -> Category:
        return Category(
            id=uuid4(),
            name="Filme",
            description="Categoria de filmes",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

    @pytest.fixture
    def series_category(self) -> Category:
        return Category(
            id=uuid4(),
            name="Séries",
            description="Categoria de séries",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

    def test_list_categories_with_default_values(
        self,
        movie_category: Category,
        series_category: Category,
    ) -> None:
        repository = create_autospec(CategoryRepository)
        repository.search.return_value = [movie_category, series_category]

        list_category = ListCategory(repository)
        output = list_category.execute(input=ListCategoryInput())

        assert output.data == [movie_category, series_category]
        assert output.meta == ListCategoryOutputMeta(
            page=1,
            per_page=5,
            sort="name",
            direction="asc",
        )
        repository.search.assert_called_once_with(
            page=1,
            per_page=5,
            search=None,
            sort="name",
            direction="asc",
        )
    
    def test_list_categories_with_custom_input(
        self,
        movie_category: Category,
        series_category: Category,
    ) -> None:
        repository = create_autospec(CategoryRepository)
        repository.search.return_value = [series_category, movie_category]

        list_category = ListCategory(repository)
        input_data = ListCategoryInput(
            page=2,
            per_page=10,
            sort=SortableFields.DESCRIPTION,
            direction="desc",
        )
        output = list_category.execute(input=input_data)

        assert output.data == [series_category, movie_category]
        assert output.meta == ListCategoryOutputMeta(
            page=2,
            per_page=10,
            sort=SortableFields.DESCRIPTION,
            direction="desc",
        )
        repository.search.assert_called_once_with(
            page=2,
            per_page=10,
            search=None,
            sort=SortableFields.DESCRIPTION,
            direction="desc",
        )

    def test_list_categories_with_invalid_sort_value(self) -> None:
        repository = create_autospec(CategoryRepository)
        list_category = ListCategory(repository)

        # SortableFields só aceita valores válidos, então passar um inválido
        # deve gerar ValidationError do Pydantic.
        with pytest.raises(ValueError):
            ListCategoryInput(sort="invalid_field")  # type: ignore
