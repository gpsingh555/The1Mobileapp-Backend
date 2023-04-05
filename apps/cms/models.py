from django.db import models

TERMS_AND_COND, PRIVACY_POLICIES, FAQ, ABOUT_US, CONTACT_US = "1", "2", "3", "4", "5"

CMS_TYPE_CHOICES = (
    (TERMS_AND_COND, 'TERMS_AND_COND'),
    (PRIVACY_POLICIES, 'PRIVACY_POLICIES'),
    (FAQ, 'FAQ'),
    (ABOUT_US, 'ABOUT_US'),
    (CONTACT_US, 'CONTACT_US')
)


class CMS(models.Model):
    heading = models.TextField(blank=True)
    description = models.TextField()

    cms_type = models.CharField(max_length=28, choices=CMS_TYPE_CHOICES)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
