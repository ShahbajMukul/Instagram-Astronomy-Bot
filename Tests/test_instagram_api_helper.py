import unittest
from unittest.mock import patch, MagicMock
from instagram_api_helper import InstagramApiHelper

class TestInstagramApiHelper(unittest.TestCase):

    def setUp(self):
        self.insta = InstagramApiHelper()
        self.insta.instagram_id = "test_id"
        self.insta.access_token = "test_token"

    def test_write_caption(self):
        title = "Test Title"
        image_by = "Test Author"
        date = "07/06/2023"
        explanation = "This is a test explanation."
        
        expected_caption = "Test Title\n\nThis is a test explanation.\n\nImage Credit: Test Author\n07/06/2023"
        actual_caption = self.insta.write_caption(title, image_by, date, explanation)
        self.assertEqual(actual_caption, expected_caption)

    def test_write_caption_truncation(self):
        title = "Short Title"
        image_by = "Credit"
        date = "01/01/2026"
        explanation = "A" * 3000
        actual_caption = self.insta.write_caption(title, image_by, date, explanation)
        self.assertLessEqual(len(actual_caption), 2200)
        self.assertTrue(actual_caption.endswith("..."))

    @patch('instagram_api_helper.requests.post')
    def test_create_media_id_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "12345"}
        mock_post.return_value = mock_response

        media_id = self.insta.create_media_id("hd_url", "url", "caption")
        self.assertEqual(media_id, "12345")

    @patch('instagram_api_helper.requests.post')
    @patch('instagram_api_helper.InstagramApiHelper.check_container_status')
    def test_publish_media(self, mock_status, mock_post):
        mock_status.return_value = "FINISHED"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.insta.publish_media("12345", "caption")
        self.assertEqual(result, "Image posted successfully!")

    @patch('instagram_api_helper.InstagramApiHelper.publish_media')
    @patch('instagram_api_helper.InstagramApiHelper.create_media_id')
    def test_post_default_image(self, mock_create, mock_publish):
        mock_create.return_value = "12345"
        mock_publish.return_value = "Image posted successfully!"

        result = self.insta.post_default_image("caption")
        self.assertEqual(result, "Image posted successfully!")

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b'data')
    @patch('instagram_api_helper.os.path.exists', return_value=True)
    @patch('instagram_api_helper.os.path.getsize', return_value=4)
    @patch('instagram_api_helper.requests.post')
    def test_create_reel_container(self, mock_post, mock_getsize, mock_exists, mock_open):
        init_response = MagicMock()
        init_response.json.return_value = {"id": "67890", "uri": "upload-url"}
        upload_response = MagicMock()
        upload_response.status_code = 200
        upload_response.json.return_value = {"success": True}
        mock_post.side_effect = [init_response, upload_response]
        
        container_id = self.insta.create_reel_container("dummy.mp4", "caption")
        self.assertEqual(container_id, "67890")
        upload_call_kwargs = mock_post.call_args_list[1].kwargs
        self.assertEqual(upload_call_kwargs["data"], b"data")
        self.assertEqual(
            upload_call_kwargs["headers"]["Content-Type"],
            "application/octet-stream",
        )

    @patch('instagram_api_helper.requests.post')
    @patch('instagram_api_helper.requests.get')
    @patch('instagram_api_helper.os.path.exists', return_value=True)
    @patch('instagram_api_helper.os.path.getsize', return_value=5)
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b'video')
    def test_create_reel_container_reports_upload_failure(
        self, mock_open, mock_getsize, mock_exists, mock_get, mock_post
    ):
        init_response = MagicMock()
        init_response.json.return_value = {"id": "67890", "uri": "upload-url"}
        upload_response = MagicMock()
        upload_response.status_code = 400
        upload_response.text = '{"error":"processing failed"}'
        upload_response.json.return_value = {"error": "processing failed"}
        mock_post.side_effect = [init_response, upload_response]
        mock_get.return_value.text = '{"status_code":"ERROR","status":"Error: processing failed"}'

        container_id = self.insta.create_reel_container("dummy.mp4", "caption")

        self.assertIsNone(container_id)
        upload_headers = mock_post.call_args_list[1].kwargs["headers"]
        self.assertEqual(upload_headers["file_size"], "5")
        self.assertEqual(upload_headers["offset"], "0")
        self.assertEqual(upload_headers["Content-Length"], "5")

    @patch('instagram_api_helper.requests.post')
    @patch('instagram_api_helper.requests.get')
    @patch('instagram_api_helper.os.path.exists', return_value=True)
    @patch('instagram_api_helper.os.path.getsize', return_value=5)
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b'video')
    def test_create_reel_container_rejects_processing_failed_upload(
        self, mock_open, mock_getsize, mock_exists, mock_get, mock_post
    ):
        init_response = MagicMock()
        init_response.json.return_value = {"id": "67890", "uri": "upload-url"}
        upload_response = MagicMock()
        upload_response.status_code = 400
        upload_response.json.return_value = {
            "debug_info": {
                "retriable": False,
                "type": "ProcessingFailedError",
                "message": "Request processing failed",
            }
        }
        mock_post.side_effect = [init_response, upload_response]
        container_id = self.insta.create_reel_container("dummy.mp4", "caption")

        self.assertIsNone(container_id)
        mock_get.assert_not_called()

    @patch('instagram_api_helper.requests.post')
    @patch('instagram_api_helper.requests.get')
    @patch('instagram_api_helper.os.path.exists', return_value=True)
    @patch('instagram_api_helper.os.path.getsize', return_value=5)
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b'video')
    def test_create_reel_container_rejects_processing_failed_upload_without_status_poll(
        self, mock_open, mock_getsize, mock_exists, mock_get, mock_post
    ):
        init_response = MagicMock()
        init_response.json.return_value = {"id": "67890", "uri": "upload-url"}
        upload_response = MagicMock()
        upload_response.status_code = 400
        upload_response.json.return_value = {
            "debug_info": {
                "retriable": False,
                "type": "ProcessingFailedError",
                "message": "Request processing failed",
            }
        }
        mock_post.side_effect = [init_response, upload_response]
        container_id = self.insta.create_reel_container("dummy.mp4", "caption")

        self.assertIsNone(container_id)
        mock_get.assert_not_called()

    @patch('instagram_api_helper.InstagramApiHelper.publish_reel')
    @patch('instagram_api_helper.InstagramApiHelper.check_container_status')
    @patch('instagram_api_helper.InstagramApiHelper.create_reel_container')
    def test_post_reel(self, mock_create, mock_status, mock_publish):
        mock_create.return_value = "67890"
        mock_status.return_value = "FINISHED"
        mock_publish.return_value = "Reel published successfully!"
        
        result = self.insta.post_reel("dummy.mp4", "caption")
        self.assertEqual(result, "Reel published successfully!")

    @patch('time.sleep')
    @patch('instagram_api_helper.InstagramApiHelper.publish_reel')
    @patch('instagram_api_helper.InstagramApiHelper.check_container_status')
    @patch('instagram_api_helper.InstagramApiHelper.create_reel_container')
    def test_post_reel_waits_for_delayed_processing(
        self, mock_create, mock_status, mock_publish, mock_sleep
    ):
        mock_create.return_value = "67890"
        mock_status.side_effect = ["IN_PROGRESS"] * 6 + ["FINISHED"]
        mock_publish.return_value = "Reel published successfully!"

        result = self.insta.post_reel("dummy.mp4", "caption", max_attempts=7)

        self.assertEqual(result, "Reel published successfully!")
        self.assertEqual(mock_status.call_count, 7)
        mock_publish.assert_called_once_with("67890")

    @patch('time.sleep')
    @patch('instagram_api_helper.InstagramApiHelper.publish_reel')
    @patch('instagram_api_helper.InstagramApiHelper.check_container_status')
    @patch('instagram_api_helper.InstagramApiHelper.create_reel_container')
    def test_post_reel_allows_slow_processing(
        self, mock_create, mock_status, mock_publish, mock_sleep
    ):
        mock_create.return_value = "67890"
        mock_status.side_effect = ["IN_PROGRESS"] * 18 + ["FINISHED"]
        mock_publish.return_value = "Reel published successfully!"

        result = self.insta.post_reel("dummy.mp4", "caption", max_attempts=19)

        self.assertEqual(result, "Reel published successfully!")
        self.assertEqual(mock_status.call_count, 19)
        mock_publish.assert_called_once_with("67890")

if __name__ == '__main__':
    unittest.main()