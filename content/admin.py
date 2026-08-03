from django.contrib import admin

from .models import (Album, Announcement, ContactMessage, Faq, Leader, MediaItem,
                     MessageLog, Milestone, News, NewsCategory, Notification,
                     Pillar, Service, SiteSetting, Verse)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ("reference", "swahili", "is_active", "order")


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_on", "is_featured", "is_published")
    list_filter = ("category", "is_featured", "is_published")
    search_fields = ("title", "summary")
    date_hierarchy = "published_on"


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "published_on", "is_active")
    list_filter = ("audience", "is_active")


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("name", "item_count", "is_public")


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "category", "album", "size_mb", "views", "uploaded_on")
    list_filter = ("kind", "category", "album")
    search_fields = ("title",)
    date_hierarchy = "uploaded_on"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("question", "page", "order", "is_active")
    list_filter = ("page",)
    list_editable = ("order", "is_active")


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("year", "title", "order")


@admin.register(Pillar)
class PillarAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "full_name", "subject", "phone", "is_read", "replied")
    list_filter = ("is_read", "replied", "subject")
    search_fields = ("full_name", "email", "phone", "body")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "title", "user", "member", "is_read")
    list_filter = ("is_read",)


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "channel", "subject", "recipients", "status")
    list_filter = ("channel", "status")
