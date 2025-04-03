from cryptomesh.repositories.functions import FunctionsRepository
from cryptomesh.models import FunctionModel


class FunctionsService:
    def __init__(self, repository: FunctionsRepository):
        self.repository = repository

    async def get_all_functions(self) -> list[FunctionModel]:
        return await self.repository.find_all()
