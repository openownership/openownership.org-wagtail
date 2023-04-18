from django.db import models


class Feedback(models.Model):
    """A Django model for storing data submitted through FeedbackForm
    """

    class Meta:
        verbose_name_plural = 'Feedback'
        ordering = ['-created']

    why_downloading = models.CharField(max_length=255, blank=True)
    where_work = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email}'
