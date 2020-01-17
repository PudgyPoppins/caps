import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Network


class NetworkModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Network(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_no_networks(self):
        """
        If no networks exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('network:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WTF, who deleted all the networks?")