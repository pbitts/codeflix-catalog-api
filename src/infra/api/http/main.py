from fastapi import FastAPI, Depends, Query

from src.application.list_category import (
    ListCategory,
    ListCategoryInput,
    CategorySortableFields,
)
from src.application.listing import ListOutput, DEFAULT_PAGINATION_SIZE, SortDirection
from src.domain.category import Category
from src.domain.category_repository import CategoryRepository
from src.infra.elasticsearch.elasticsearch_category_repository import (
    ElasticsearchCategoryRepository,
)

from src.application.list_cast_member import (
    CastMemberSortableFields, 
    ListCastMember, 
    ListCastMemberInput
)
from src.domain.cast_member_repository import CastMemberRepository
from src.domain.cast_member import CastMember
from src.infra.elasticsearch.elasticsearch_cast_member_repository import ElasticsearchCastMemberRepository

app = FastAPI()


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "ok"}


def get_category_repository() -> CategoryRepository:
    # Vamos deixar aqui por simplicidade, mas isso poderia ser um arquivo separado de configuração, dependências, etc.
    return ElasticsearchCategoryRepository()

def get_cast_member_repository() -> CastMemberRepository:
    # Vamos deixar aqui por simplicidade, mas isso poderia ser um arquivo separado de configuração, dependências, etc.
    return ElasticsearchCastMemberRepository()


@app.get("/categories", response_model=ListOutput[Category])
def list_categories(
    repository: ElasticsearchCategoryRepository = Depends(get_category_repository),
    search: str | None = Query(None, description="Search term for name or description"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        DEFAULT_PAGINATION_SIZE,
        ge=1,
        le=100,
        description="Number of items per page",
    ),
    sort: CategorySortableFields = Query(
        CategorySortableFields.NAME, description="Field to sort by"
    ),
    direction: SortDirection = Query(
        SortDirection.ASC, description="Sort direction (asc or desc)"
    ),
) -> ListOutput[Category]:
    return ListCategory(repository=repository).execute(ListCategoryInput(
        search=search,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
    ))
    

@app.get("/cast_members", response_model=ListOutput[CastMember])
def list_cast_members(
    repository: ElasticsearchCastMemberRepository = Depends(get_cast_member_repository),
    search: str | None = Query(None, description="Search term for name or description"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(
        DEFAULT_PAGINATION_SIZE,
        ge=1,
        le=100,
        description="Number of items per page",
    ),
    sort: CastMemberSortableFields = Query(
        CastMemberSortableFields.NAME, description="Field to sort by"
    ),
    direction: SortDirection = Query(
        SortDirection.ASC, description="Sort direction (asc or desc)"
    ),
) -> ListOutput[CastMember]:
    return ListCastMember(repository=repository).execute(ListCastMemberInput(
        search=search,
        page=page,
        per_page=per_page,
        sort=sort,
        direction=direction,
    ))