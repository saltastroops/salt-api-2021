from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query

from saltapi.repository.unit_of_work import UnitOfWork
from saltapi.service.authentication_service import get_current_user
from saltapi.service.user import User
from saltapi.web import services
from saltapi.web.schema.common import Semester
from saltapi.web.schema.rss import (
    MosBlock,
    MosMaskMetadata,
    UpdateMosMaskMetadata,
)

router = APIRouter(tags=["Instrument"])


@router.get(
    "/rss/masks-in-magazine",
    summary="Get current MOS masks in the magazine",
    response_model=List[str],
)
def get_masks_in_magazine(
    mask_type: Optional[str] = Query(
        None, title="Mask type", description="The mask type."
    ),
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
def get_mos_mask_metadata(
    user: User = Depends(get_current_user),
    from_semester: Semester = Query(
        "2000-1",
        alias="from",
        description="Only include MOS masks for this semester and later.",
        title="From semester",
    ),
    to_semester: Semester = Query(
        "2099-2",
        alias="to",
        description="Only include MOS masks for this semester and earlier.",
        title="To semester",
    ),
) -> List[MosBlock]:
    """
    Get the list of blocks using MOS.
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_view_mos_metadata(user)

        instrument_service = services.instrument_service(unit_of_work.connection)
        mos_blocks = instrument_service.get_mos_mask_metadata(
            from_semester, to_semester
        )
        return [MosBlock(**md) for md in mos_blocks]


@router.put(
    "/rss/mos-mask-metadata/{barcode}",
    summary="Update MOS mask metadata",
    response_model=MosMaskMetadata,
    status_code=200,
)
def update_mos_mask_metadata(
    mos_mask_metadata: UpdateMosMaskMetadata = Body(
        ..., title="The Slit mask", description="Semester"
    ),
    barcode: str = Path(..., title="Barcode", description="The barcode of slit mask"),
    user: User = Depends(get_current_user),
) -> MosMaskMetadata:
    """
    Update MOS mask metadata.
    """
    with UnitOfWork() as unit_of_work:
        permission_service = services.permission_service(unit_of_work.connection)
        permission_service.check_permission_to_update_mos_mask_metadata(user)

        instrument_service = services.instrument_service(unit_of_work.connection)
        args = dict(mos_mask_metadata)
        args["barcode"] = barcode
        response = instrument_service.update_mos_mask_metadata(args)
        unit_of_work.connection.commit()
        return MosMaskMetadata(**response)


@router.get(
    "/rss/mos-obsolete-masks-in-magazine",
    summary="Get the masks that are no longer needed",
    response_model=List[str],
)
def get_obsolete_mos_masks_in_magazine() -> List[str]:
    """
    Returns the list of MOS obsolete masks, optionally filtered by mask type.
    """
    with UnitOfWork() as unit_of_work:
        instrument_service = services.instrument_service(unit_of_work.connection)
        return instrument_service.get_obsolete_mos_masks_in_magazine()