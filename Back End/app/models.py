from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

from users.models import Profile


# Create your models here.
class Favourite(models.Model):
    user = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    location = models.PointField(
        # verbose_name=_("last location"),
        editable=False,
        blank=True,
        null=True,
        default=None,
        help_text=(
            "Geographic coordinates (lon/lat) as Point. Can be serialised from WKT (well-known text) representation")
    )

    def __str__(self):
        return f"{self.user}"
