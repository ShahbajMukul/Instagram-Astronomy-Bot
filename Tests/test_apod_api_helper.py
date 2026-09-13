import pytest
from unittest.mock import patch
from apod_api_helper import ApodApiHelper

@patch('apod_api_helper.requests.get')
def test_get_apod_data(mock_get):
    mock_get.return_value.json.return_value = {
        "date": "2023-07-07",
        "explanation": "This pretty starfield spans...",
        "hdurl": "https://example.com/hd.jpg",
        "copyright": "Mårten Frosth",
        "title": "The Double Cluster in Perseus"
    }
    mock_get.return_value.raise_for_status.return_value = None
    
    helper = ApodApiHelper()
    data = helper.get_apod_data()
    assert data["date"] == "2023-07-07"
    assert data["copyright"] == "Mårten Frosth"
    assert data["title"] == "The Double Cluster in Perseus"

@patch('apod_api_helper.requests.get')
def test_get_apod_data_wrong_cr_format(mock_get):
    mock_get.return_value.json.return_value = {
        "date": "2023-07-07",
        "explanation": "A good explanation",
        "hdurl": "https://example.com/hd.jpg",
        "copyright": "Brian Cox \n Stephen Hawking \n Albert Einstein",
        "title": "The Double Cluster in Perseus"
    }
    mock_get.return_value.raise_for_status.return_value = None

    helper = ApodApiHelper()
    data = helper.get_apod_data()
    
    assert "Brian Cox" in data["copyright"]
    assert "\n" not in data["copyright"]

@patch('apod_api_helper.requests.get')
def test_get_random_apod_data_uses_single_random_date(mock_get):
    mock_get.return_value.json.return_value = {
        "date": "2026-01-01",
        "explanation": "A random explanation",
        "title": "A random APOD",
        "copyright": "NASA\nESA",
        "media_type": "image",
    }
    mock_get.return_value.raise_for_status.return_value = None

    helper = ApodApiHelper()
    data = helper.get_random_apod_data()

    requested_url = mock_get.call_args.args[0]
    assert "start_date=" in requested_url
    assert "end_date=" in requested_url
    assert data["copyright"] == "NASA,ESA"


@patch('apod_api_helper.random.randint', side_effect=[1, 2])
@patch('apod_api_helper.requests.get')
def test_get_random_apod_data_skips_video(mock_get, mock_randint):
    video_response = {
        "date": "2026-01-01",
        "media_type": "video",
    }
    image_response = {
        "date": "2026-01-02",
        "explanation": "An image explanation",
        "title": "An image APOD",
        "copyright": "NASA",
        "media_type": "image",
    }
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.side_effect = [video_response, image_response]

    helper = ApodApiHelper()
    data = helper.get_random_apod_data()

    assert data["media_type"] == "image"
    assert mock_get.call_count == 2