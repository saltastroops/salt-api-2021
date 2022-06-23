from fastapi.testclient import TestClient
from starlette import status

RSS_MASKS_IN_MAGAZINE_URL = "/rss/masks-in-magazine"


def test_should_return_list_of_rss_masks_in_magazine(
    client: TestClient,
) -> None:
    response = client.get(
        RSS_MASKS_IN_MAGAZINE_URL + "/",
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 1


def test_should_return_list_of_longslit_rss_masks_in_magazine(
    client: TestClient,
) -> None:
    response = client.get(
        RSS_MASKS_IN_MAGAZINE_URL + "/", params={"mask_types": ["Longslit"]}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 1


def test_should_return_list_of_rss_masks_in_magazine_filtered_by_mask_types(
    client: TestClient,
) -> None:
    response = client.get(
        RSS_MASKS_IN_MAGAZINE_URL + "/",
        params={"mask_types": ["MOS", "Imaging", "Engineering"]},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 1
