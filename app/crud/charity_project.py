from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_open_projects(self, session: AsyncSession):
        result = await session.execute(
            select(self.model).where(
                self.model.fully_invested.is_(False)
            )
        )
        return result.scalars().all()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ) -> list[dict]:
        closed_projects = await session.execute(
            select(
                CharityProject.name,
                CharityProject.description,
                func.julianday(CharityProject.close_date) -
                func.julianday(CharityProject.create_date).label('delta')
            ).where(
                CharityProject.fully_invested
            )
        )

        closed_projects_list = []

        for project in closed_projects:
            closed_projects_list.append({
                'name': project.name,
                'description': project.description,
                'delta': project.delta
            })

        return sorted(closed_projects_list, key=lambda x: x['delta'])


charity_project_crud = CRUDCharityProject(CharityProject)
