from apod_api_helper import ApodApiHelper

def test_get_apod_data():
    apod_api_helper = ApodApiHelper()
    data = apod_api_helper.get_apod_data()
    assert data["date"] == "2023-07-07"
    assert data["explanation"] == "This pretty starfield spans about three full moons (1.5 degrees) across the heroic northern constellation of Perseus. It holds the famous pair of open star clusters, h and Chi Persei. Also cataloged as NGC 869 (top) and NGC 884, both clusters are about 7,000 light-years away and contain stars much younger and hotter than the Sun.  Separated by only a few hundred light-years, the clusters are both 13 million years young based on the ages of their individual stars, evidence that they were likely a product of the same star-forming region. Always a rewarding sight in binoculars, the Double Cluster is even visible to the unaided eye from dark locations."
    assert data["hdurl"] == "https://apod.nasa.gov/apod/image/2307/Caldwell_14_2023_HaLRGB_LRGB_stars_wm.jpg"
    assert data["copyright"] == "Mårten Frosth"
    assert data["title"] == "The Double Cluster in Perseus"

#sometimes copyright will return names with \n 
sample_data = {
    "date": "2023-07-07",
    "explanation": "A good explanation",
    "hdurl": "https://apod.nasa.gov/apod/image/2307/Caldwell_14_2023_HaLRGB_LRGB_stars_wm.jpg",
    "copyright": "Brian Cox \n Stephen Hawking \n Albert Einstein",
    "title": "The Double Cluster in Perseus"
    }

def test_get_apod_data_wrong_cr_format(monkeypatch):
    monkeypatch.setattr(ApodApiHelper, "get_apod_data", lambda x: sample_data)
    apod_api_helper = ApodApiHelper()
    data = apod_api_helper.get_apod_data()
    data["copyright"] = data["copyright"].replace(" \n", ",").strip(",")
    expected_copyright = "Brian Cox, Stephen Hawking, Albert Einstein"
    assert data["copyright"] == expected_copyright