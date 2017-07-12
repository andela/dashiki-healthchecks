# Create your tests here.
import os
from hc.help_videos.models import Video
from django.test import TestCase
from django.urls import reverse
from hc.settings import BASE_DIR
from django.contrib.auth.models import User

# Create your tests here.


class HelpVideosTestCase(TestCase):

    def setUp(self):
        self.superuser = User(username="admin", email="collins@andela.com")
        self.superuser.set_password("pass")
        self.superuser.is_superuser = True
        self.superuser.save()

        self.client.login(username="collins@andela.com", password="pass")
        # create dummy file
        with open("dummy.mp4", 'wb') as f:
            f.write(os.urandom(124))

    def test_upload_video_successfully(self):
        form = {"title": "Dummy video",
                "description": "loremipsum",
                "video-file": open("dummy.mp4", "rb")
                }
        response = self.client.post(reverse('hc-help-videos-upload'), form)
        self.assertEqual(response.status_code, 200)

    def test_save_uploaded_video_to_db_successfully(self):
        initial_video_count = Video.objects.count()
        form = {"title": "Dummy video",
                "description": "loremipsum",
                "video-file": open("dummy.mp4", "rb")
                }

        response = self.client.post(reverse('hc-help-videos-upload'), form)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(Video.objects.count() - initial_video_count, 1)

    def tearDown(self):
        self.client.logout()
        os.system("rm -r {}".format("{}{}".format(BASE_DIR,
                                                  "/dummy.mp4").replace("%20", "\ ")))
