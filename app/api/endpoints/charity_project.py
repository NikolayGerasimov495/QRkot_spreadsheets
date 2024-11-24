from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_project_exists,
                                check_name_duplicate,
                                check_project_can_be_deleted,
                                validate_charity_project_update)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import Donation
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investing import investing_process

router = APIRouter()


@router.get('/',
            response_model=list[CharityProjectDB],
            response_model_exclude_none=True,
            )
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """Возвращает список всех проектов."""
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.

    Создает благотворительный проект.
    """
    await check_name_duplicate(charity_project.name, session)
    await charity_project_crud.get_project_id_by_name(
        charity_project.name, session
    )
    new_project = await charity_project_crud.create(charity_project, session)

    await investing_process(new_project, Donation, session)

    return new_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.

    Удаляет проект. Нельзя удалить проект,
    в который уже были инвестированы средства,
    его можно только закрыть.
    """
    project = await check_charity_project_exists(
        project_id, session
    )
    await check_project_can_be_deleted(project, session)
    charity_project = await charity_project_crud.remove(
        project, session
    )
    return charity_project


@router.patch(
    '/{charity_project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
        charity_project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.

    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    charity_project = await check_charity_project_exists(
        charity_project_id, session
    )
    await validate_charity_project_update(charity_project, obj_in)

    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    return charity_project
