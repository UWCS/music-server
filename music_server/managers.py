from django.db.models import Manager

class UnplayedItemManager(Manager):
    def get_query_set(self):
        return super(UnplayedItemManager, self).get_query_set().exclude(state='x')
