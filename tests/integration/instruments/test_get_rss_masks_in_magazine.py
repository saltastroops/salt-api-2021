from fastapi.testclient import TestClient
from starlette import status

RSS_MASKS_IN_MAGAZINE_URL = "/rss/masks-in-magazine"


def test_should_return_list_of_rss_masks_in_magazine(
    client: TestClient,
) -> None:
    response_all_masks = client.get(
        RSS_MASKS_IN_MAGAZINE_URL + "/",
    )
    assert response_all_masks.status_code == status.HTTP_200_OK

    response_longslit_masks = client.get(
        RSS_MASKS_IN_MAGAZINE_URL + "/", params={"mask_types": ["Longslit"]}
    )
    assert response_longslit_masks.status_code == status.HTTP_200_OK

    response_mos_masks = client.get(
        RSS_MASKS_IN_MAGAZINE_URL + "/",
        params={"mask_types": ["MOS"]},
    )
    assert response_mos_masks.status_code == status.HTTP_200_OK

    response_imaging_masks = client.get(
        RSS_MASKS_IN_MAGAZINE_URL + "/",
        params={"mask_types": ["Imaging"]},
    )
    assert response_imaging_masks.status_code == status.HTTP_200_OK

    response_engineering_masks = client.get(
        RSS_MASKS_IN_MAGAZINE_URL + "/",
        params={"mask_types": ["Engineering"]},
    )
    assert response_engineering_masks.status_code == status.HTTP_200_OK
    assert len(response_all_masks.json()) == sum(
        [
            len(response_longslit_masks.json()),
            len(response_mos_masks.json()),
            len(response_imaging_masks.json()),
            len(response_engineering_masks.json()),
        ]
    )
