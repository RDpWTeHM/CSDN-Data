from django.contrib import admin

# Register your models here.
from .models import UserID, VisualData, Article
from .models import Follows


class VisualDataInline(admin.TabularInline):
    model = VisualData
    # ordering = ('-crawlerDate',)
    # list_per_page = 5
    extra = 1


@admin.register(VisualData)
class VisualDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'crawlerDate')
    list_per_page = 100


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'articleid', 'title',
                    'pub_date', 'read_num', 'comments_num')
    list_per_page = 100


@admin.register(Follows)
class FollowsAdmin(admin.ModelAdmin):
    list_display = ('id', 'followed_by', 'follow_id', 'follow_name',
                    # 'current_total_follows_num',
                    'crawledDate')
    list_per_page = 50

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
    list_display = ('id', 'user_id', 'visit', 'rank', 'register_date')
    fieldsets = [
        (None,            {'fields': ['user_id']}),
        ('Register Date', {'fields': ['register_date'],
                           # 'classes': ['collapse'],
                           }),
        ('last visit number', {'fields': ['visit']}),
        ('last rank', {'fields': ['rank']}),
    ]
    inlines = [VisualDataInline]

    list_per_page = 50

    search_fields = ['user_id']
    list_filter=[UsefulUserIDFilter, 'register_date']


admin.site.register(UserID, UserIDAdmin)
