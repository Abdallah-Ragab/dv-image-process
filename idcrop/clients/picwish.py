import os
import time
from dotenv import load_dotenv
from log_config import logger
import requests



class CutoutApiClient:
    STATES = {
        		"-8": "Processing timeout, maximum processing time 30 seconds",
                "-7": "Invalid image file (e.g., corrupt image, incorrect format, etc.)",
                "-5": "image_url image exceeds size (15MB)",
                "-3": "image_url server failed to download (Please check if the file URL is available)",
                "-2": "The cutout is complete, but the oss upload failed",
                "-1": "Cutout failed",
            	"0": "Queued, the cutout task is in the queue",
            	"1": "Finished, cutout is successful",
            	"2": "Preparing",
            	"3": "Waiting",
            	"4": "In processing, the cutout is in progress.",
    }
    def __init__(self):
        load_dotenv()
        self.api_key = self.get_api_key()
        self.logger = logger
        self.base_url = "https://techhk.aoscdn.com/api/tasks/visual/segmentation"

    def get_api_key(self):
        try:
            api_key = os.getenv('PICWISH_API_KEY')
            if api_key:
                return api_key
            else:
                raise Exception("No API key found.")
        except Exception as e:
            self.logger.error(f"Could not get API key: {e.__traceback__.tb_lineno}:{e}")
            raise

    def upload_image_async(self, image_file=None, image_url=None, image_base64=None, sync=0, return_type=1, output_type=2, format="jpg", bg_color=None):
        try:
            headers = {
                "X-API-KEY": self.api_key
            }

            data = {
                "sync": sync,
                "return_type": return_type,
                "output_type": output_type,
                "format": format,
                "bg_color": bg_color
            }

            if image_file:
                files = {'image_file': image_file}
            elif image_url:
                data['image_url'] = image_url
            elif image_base64:
                data['image_base64'] = image_base64

            response = requests.post(self.base_url, headers=headers, data=data, files=files)
            response.raise_for_status()

            result = response.json()
            if result.get("status") == 200:
                self.logger.info("Image upload request successful.")
                return result.get("data").get("task_id")
            else:
                self.logger.error(f"Image upload request failed: {result.get('message')}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Image upload request failed: {str(e)}")
            return None

    def poll_cutout_result(self, task_id, duration=1):
        try:
            url = f"{self.base_url}/{task_id}"
            headers = {
                "X-API-KEY": self.api_key
            }

            while True:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                result = response.json()
                state = result.get("data").get("state")
                if state == 1:
                    self.logger.success(self.STATES.get(str(state)))
                    return result
                elif state < 0:
                    self.logger.error(f"Image cutout failed (state-code:{state}): " + self.STATES.get(str(state)))
                    return result
                else:
                    progress = result.get("data").get("progress") or "x"
                    self.logger.info(f"Polling: {self.STATES.get(str(state))} progress:{progress}%")
                    time.sleep(duration)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error while polling cutout result: {str(e)}")
            return None

    def download_result_image(self, result_url, save_path):
        try:
            response = requests.get(result_url)
            response.raise_for_status()

            with open(save_path, 'wb') as image_file:
                image_file.write(response.content)
            self.logger.success(f"Result image downloaded and saved to {save_path}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error while downloading the result image: {str(e)}")
