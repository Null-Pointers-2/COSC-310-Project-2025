from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_resources
from app.core.resources import SingletonResources
from app.services import ranking_service

router = APIRouter()


@router.get("/ranking/popular")
def get_popular_movies(
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    return ranking_service.get_popular_movies(resources)
