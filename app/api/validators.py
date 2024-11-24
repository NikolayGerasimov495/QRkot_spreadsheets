from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import CharityProjectUpdate


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
        project_id: int,
        session: AsyncSession,
):
    project = await charity_project_crud.get(
        project_id, session
    )
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!'
        )
    return project


async def check_project_can_be_deleted(
        project,
        session: AsyncSession):
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )


async def validate_charity_project_update(
        charity_project,
        obj_in: CharityProjectUpdate
):
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать.'
        )
    if (obj_in.full_amount is not None and
            obj_in.full_amount < charity_project.invested_amount):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя установить значение full_amount'
                   'меньше уже вложенной суммы.'
        )
