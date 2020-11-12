from django.core.management.base import BaseCommand
from django.db.models import Q, F
from django.utils import timezone
from orgs.models import Invitation

class Command(BaseCommand):
    help = 'Makes any invites that should be invalid, invalid'

    def handle(self, *args, **kwargs):
        for i in Invitation.objects.filter(Q(valid=True), Q(uses__gte=F('max_uses')) | Q(expiration__lte=(timezone.now() - F('created_on')))):
            i.valid = False
            i.save()
'''
Cronjob
*/10 * * * * cd ~/Desktop/caps && source env/bin/activate && python3 manage.py invite_invalidator
'''
