import datetime

from django.db import models

from zerver.models import AbstractPushDeviceToken, Realm, UserProfile, \
    RealmAuditLog

def get_remote_server_by_uuid(uuid: str) -> 'RemoteZulipServer':
    return RemoteZulipServer.objects.get(uuid=uuid)

class RemoteZulipServer(models.Model):
    UUID_LENGTH = 36
    API_KEY_LENGTH = 64
    HOSTNAME_MAX_LENGTH = 128

    uuid = models.CharField(max_length=UUID_LENGTH, unique=True)  # type: str
    api_key = models.CharField(max_length=API_KEY_LENGTH)  # type: str

    hostname = models.CharField(max_length=HOSTNAME_MAX_LENGTH)  # type: str
    contact_email = models.EmailField(blank=True, null=False)  # type: str
    last_updated = models.DateTimeField('last updated', auto_now=True)  # type: datetime.datetime

    def __str__(self) -> str:
        return "<RemoteZulipServer %s %s>" % (self.hostname, self.uuid[0:12])

# Variant of PushDeviceToken for a remote server.
class RemotePushDeviceToken(AbstractPushDeviceToken):
    server = models.ForeignKey(RemoteZulipServer, on_delete=models.CASCADE)  # type: RemoteZulipServer
    # The user id on the remote server for this device device this is
    user_id = models.BigIntegerField(db_index=True)  # type: int
    token = models.CharField(max_length=4096, db_index=True)  # type: bytes

    class Meta:
        unique_together = ("server", "token")

    def __str__(self) -> str:
        return "<RemotePushDeviceToken %s %s>" % (self.server, self.user_id)

class Customer(models.Model):
    realm = models.OneToOneField(Realm, on_delete=models.CASCADE)  # type: Realm
    stripe_customer_id = models.CharField(max_length=255, unique=True)  # type: str
    # Becomes True the first time a payment successfully goes through, and never
    # goes back to being False
    has_billing_relationship = models.BooleanField(default=False)  # type: bool

    def __str__(self) -> str:
        return "<Customer %s %s>" % (self.realm, self.stripe_customer_id)

class Plan(models.Model):
    # The two possible values for nickname
    CLOUD_MONTHLY = 'monthly'
    CLOUD_ANNUAL = 'annual'
    nickname = models.CharField(max_length=40, unique=True)  # type: str

    stripe_plan_id = models.CharField(max_length=255, unique=True)  # type: str

class Coupon(models.Model):
    percent_off = models.SmallIntegerField(unique=True)  # type: int
    stripe_coupon_id = models.CharField(max_length=255, unique=True)  # type: str

    def __str__(self) -> str:
        return '<Coupon: %s %s %s>' % (self.percent_off, self.stripe_coupon_id, self.id)

class BillingProcessor(models.Model):
    log_row = models.ForeignKey(RealmAuditLog, on_delete=models.CASCADE)  # RealmAuditLog
    # Exactly one processor, the global processor, has realm=None.
    realm = models.OneToOneField(Realm, null=True, on_delete=models.CASCADE)  # type: Realm

    DONE = 'done'
    STARTED = 'started'
    SKIPPED = 'skipped'  # global processor only
    STALLED = 'stalled'  # realm processors only
    state = models.CharField(max_length=20)  # type: str

    last_modified = models.DateTimeField(auto_now=True)  # type: datetime.datetime

    def __str__(self) -> str:
        return '<BillingProcessor: %s %s %s>' % (self.realm, self.log_row, self.id)
