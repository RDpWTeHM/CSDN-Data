from django.contrib import admin

from .models import UserID
# from .models import VisualData, Article
# from .models import Follows


from django.utils.translation import gettext_lazy as _


class UsefulUserIDFilter(admin.SimpleListFilter):
    title = _('Useful UserID')

    parameter_name = 'userfuluserid'

    def lookups(self, request, model_admin):
        return(
            ('useful', _('visit more than 0')),
            ('useless', _('visit less than 1')), )

    def queryset(self, request, queryset):
        if self.value() == 'useful':
            return queryset.filter(visit__gte=1,
                                   visit__lte=99999999999, )

        if self.value() == 'useless':
            return queryset.filter(visit__gte=-1,
                                   visit__lte=0, )


class UserIDAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'name', 'visit', 'rank', 'register_date')
    fieldsets = [
        (None, {'fields': ['user_id']}),
        ('Register Date', {'fields': ['register_date'],
                           # 'classes': ['collapse'],
                           }),
        ('Web Name', {'fields': ['name']}),
        ('last visit number', {'fields': ['visit']}),
        ('last rank number', {'fields': ['rank']}),
    ]
    # inlines = [VisualDataInline]

    list_per_page = 50

    search_fields = ['user_id']
    list_filter = [UsefulUserIDFilter, 'register_date']


admin.site.register(UserID, UserIDAdmin)
