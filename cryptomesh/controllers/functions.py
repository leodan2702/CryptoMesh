from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import FunctionModel
from cryptomesh.services.functions import FunctionsService
from cryptomesh.repositories.functions import FunctionsRepository
from cryptomesh.db import get_collection

router = APIRouter()

def get_functions_service() -> FunctionsService:
    service = FunctionsService(
        repository=FunctionsRepository(
            collection=get_collection("functions")
        )
    )
    return service

@router.get("/functions", response_model=List[FunctionModel])
async def get_functions(
    functions_service: FunctionsService = Depends(get_functions_service)
):
    """
    Retrieve a list of all functions.
    """
    return await functions_service.get_all_functions()
