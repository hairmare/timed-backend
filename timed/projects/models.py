"""Models for the projects app."""

from django.conf import settings
from django.db import models


class Customer(models.Model):
    """Customer model.

    A customer is a person or company which will pay the work
    reported on their projects.
    """

    name     = models.CharField(max_length=255)
    email    = models.EmailField(blank=True)
    website  = models.URLField(blank=True)
    comment  = models.TextField(blank=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        """Represent the model as a string.

        :return: The string representation
        :rtype:  str
        """
        return self.name

    class Meta:
        """Meta informations for the customer model."""

        indexes = [models.Index(fields=['name', 'archived'])]


class BillingType(models.Model):
    """Billing type defining how a project, resp. reports are being billed."""

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    """Project model.

    A project is an offer in most cases. It has multiple tasks and
    belongs to a customer.
    """

    name            = models.CharField(max_length=255)
    comment         = models.TextField(blank=True)
    archived        = models.BooleanField(default=False)
    estimated_hours = models.PositiveIntegerField(blank=True, null=True)
    customer        = models.ForeignKey('projects.Customer',
                                        related_name='projects')
    billing_type    = models.ForeignKey(BillingType,
                                        blank=True, null=True,
                                        related_name='projects')
    reviewers       = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                             related_name='reviews')

    def __str__(self):
        """Represent the model as a string.

        :return: The string representation
        :rtype:  str
        """
        return '{0} > {1}'.format(self.customer, self.name)

    class Meta:
        """Meta informations for the project model."""

        indexes = [models.Index(fields=['name', 'archived'])]


class Task(models.Model):
    """Task model.

    A task is a certain activity type on a project. Users can
    report their activities and reports on it.
    """

    name            = models.CharField(max_length=255)
    estimated_hours = models.PositiveIntegerField(blank=True, null=True)
    archived        = models.BooleanField(default=False)
    project         = models.ForeignKey('projects.Project',
                                        related_name='tasks')

    def __str__(self):
        """Represent the model as a string.

        :return: The string representation
        :rtype:  str
        """
        return '{0} > {1}'.format(self.project, self.name)

    class Meta:
        """Meta informations for the task model."""

        indexes = [models.Index(fields=['name', 'archived'])]


class TaskTemplate(models.Model):
    """Task template model.

    A task template is a global template of a task which should
    be generated for every project.
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        """Represent the model as a string.

        :return: The string representation
        :rtype:  str
        """
        return self.name
