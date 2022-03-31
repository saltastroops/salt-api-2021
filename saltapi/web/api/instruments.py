from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body, Path

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web import services
from saltapi.web.schema.common import Semester
from saltapi.web.schema.rss import MosBlock, UpdateMosMaskMatadata, MosMaskMatadata

router = APIRouter(tags=["Instrument"])


@router.get(
    "/rss/masks-in-magazine",
    summary="Get current MOS masks in the magazine",
    response_model=List[str]
)
def get_masks_in_magazine(
    mask_type: Optional[str] = Query(
        None, title="Mask type", description="The mask type."),
) -> List[str]:
    """
    Returns the list of masks in the magazine, optionally filtered by mask type.
    """
    with UnitOfWork() as unit_of_work:
        instrument_service = services.instrument_service(unit_of_work.connection)
        return instrument_service.get_masks_in_magazine(mask_type)


@router.get(
    "/rss/mos-mask-metadata",
    summary="Get MOS data",
    response_model=List[MosBlock],
    status_code=200,
)
def get_mos_mask_matadata(
    user: User = Depends(get_current_user),
    semesters: List[Semester] = Query(
        ..., alias='semester', title="Semester", description="Semester"),
) -> List[MosBlock]:
    """
    Get the list of blocks using MOS.
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_mos_matadata(user)

        instrument_service = services.instrument_service(unit_of_work.connection)
        mos_blocks = instrument_service.get_mos_mask_matadata([str(s) for s in semesters])
        return [MosBlock(**md) for md in mos_blocks]


@router.put(
    "/rss/mos-mask-metadata/{barcode}",
    summary="Update MOS mask matadata",
    response_model=MosMaskMatadata,
    status_code=201,
)
def update_mos_mask_matadata(
    mos_mask_matadata: UpdateMosMaskMatadata = Body(..., title="The Slit mask", description="Semester"),
    barcode: str = Path(..., title="Barcode", description="The barcode of slit mask"),
    user: User = Depends(get_current_user),
) -> MosMaskMatadata:
    """
    Update MOS mask matadata.
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_update_mos_mask_matadata(user)

        instrument_service = services.instrument_service(unit_of_work.connection)
        args = dict(mos_mask_matadata)
        args["barcode"] = barcode
        response = instrument_service.update_mos_mask_matadata(args)
        unit_of_work.connection.commit()
        return MosMaskMatadata(**response)
