"""Viewsets for the tracking app."""

import django_excel
from django.http import HttpResponseBadRequest
from rest_condition import C
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from timed.tracking import filters, models, serializers
from timed.tracking.permissions import (IsAdminUser, IsAuthenticated, IsOwner,
                                        IsReadOnly, IsUnverified)


class ActivityViewSet(ModelViewSet):
    """Activity view set."""

    serializer_class = serializers.ActivitySerializer
    filter_class     = filters.ActivityFilterSet

    def get_queryset(self):
        """Filter the queryset by the user of the request.

        :return: The filtered activities
        :rtype:  QuerySet
        """
        return models.Activity.objects.prefetch_related(
            'blocks'
        ).select_related(
            'task',
            'user',
            'task__project',
            'task__project__customer'
        ).filter(
            user=self.request.user
        )


class ActivityBlockViewSet(ModelViewSet):
    """Activity view set."""

    serializer_class = serializers.ActivityBlockSerializer
    filter_class     = filters.ActivityBlockFilterSet

    def get_queryset(self):
        """Filter the queryset by the user of the request.

        :return: The filtered activity blocks
        :rtype:  QuerySet
        """
        return models.ActivityBlock.objects.select_related(
            'activity'
        ).filter(
            activity__user=self.request.user
        )


class AttendanceViewSet(ModelViewSet):
    """Attendance view set."""

    serializer_class = serializers.AttendanceSerializer
    filter_class     = filters.AttendanceFilterSet

    def get_queryset(self):
        """Filter the queryset by the user of the request.

        :return: The filtered attendances
        :rtype:  QuerySet
        """
        return models.Attendance.objects.select_related(
            'user'
        ).filter(
            user=self.request.user
        )


class ReportViewSet(ModelViewSet):
    """Report view set."""

    serializer_class = serializers.ReportSerializer
    filter_class     = filters.ReportFilterSet
    permission_classes = [
        # admin user can change all
        C(IsAuthenticated) & C(IsAdminUser) |
        # owner may only change its own unverified reports
        C(IsAuthenticated) & C(IsOwner) & C(IsUnverified) |
        # all authenticated users may read all reports
        C(IsAuthenticated) & C(IsReadOnly)
    ]
    ordering = ('date', )
    ordering_fields = (
        'date',
        'duration',
        'task__project__customer__name',
        'task__project__name',
        'task__name',
        'user__username',
        'comment',
    )

    @list_route()
    def export(self, request):
        """Export filtered reports to given file format."""
        queryset = self.filter_queryset(self.get_queryset())
        colnames = [
            'Date', 'Duration', 'Customer',
            'Project', 'Task', 'User', 'Comment'
        ]
        content = [
            [
                report.date,
                report.duration,
                report.task.project.customer.name,
                report.task.project.name,
                report.task.name,
                report.user.username,
                report.comment,
            ]
            for report in queryset
        ]

        file_type = request.query_params.get('file_type')
        if file_type not in ['csv', 'xlsx', 'ods']:
            return HttpResponseBadRequest()

        sheet = django_excel.pe.Sheet(
            content, name='Report', colnames=colnames
        )
        return django_excel.make_response(
            sheet, file_type=file_type, file_name='report.%s' % file_type
        )

    @list_route(methods=['post'], url_path='verify',
                permission_classes=[IsAuthenticated, IsAdminUser])
    def verify_list(self, request):
        """
        Bulk verify all reports by given filter.

        Authenticated user will be set as verified_by on given
        reports.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            # page is a list so need to convert it to queryset
            ids = [report.id for report in page]
            queryset = models.Report.objects.filter(id__in=ids)
        queryset.update(verified_by=request.user)

        return Response(data={})

    def get_queryset(self):
        """Select related to reduce queries.

        :return: The filtered reports
        :rtype:  QuerySet
        """
        return models.Report.objects.select_related(
            'task',
            'user',
            'activity'
        ).prefetch_related('task__project', 'task__project__customer')


class AbsenceViewSet(ModelViewSet):
    """Absence view set."""

    serializer_class = serializers.AbsenceSerializer
    filter_class     = filters.AbsenceFilterSet

    def get_queryset(self):
        """Filter the queryset by the user of the request.

        :return: The filtered absences
        :rtype:  QuerySet
        """
        return models.Absence.objects.select_related(
            'type',
            'user'
        ).filter(
            user=self.request.user
        )
