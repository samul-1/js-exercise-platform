from django.db.models import Q
from rest_framework import filters


class TeacherOrOwnedOnly(filters.BaseFilterBackend):
    """
    If the requesting user isn't a teacher, filter queryset to their own
    objects only
    """

    def filter_queryset(self, request, queryset, view):
        if not request.user.is_teacher:
            return queryset.filter(user=request.user)
        return queryset


class TeacherOrAssignedOnly(filters.BaseFilterBackend):
    """
    If the requesting user isn't a teacher, filter queryset to their own
    objects only

    Works similar to TeacherOrOwnedOnly, but in this case the filtering is done on a
    many to many relationship
    """

    pass

    # def filter_queryset(self, request, queryset, view):
    #     if not request.user.is_teacher:
    #         # filter for exercises that have been assigned to the user
    #         return queryset.filter(id__in=request.user.assigned_exercises.all())
    #     return queryset


class ExamCreatorAndAllowed(filters.BaseFilterBackend):
    """
    Limits the exam queryset to the exams the user has either created
    or has been granted access to
    """

    def filter_queryset(self, request, queryset, view):
        if request.user.is_teacher:
            return queryset.filter(
                Q(created_by=request.user) | Q(allowed_teachers__in=[request.user])
            ).distinct()
        return queryset
