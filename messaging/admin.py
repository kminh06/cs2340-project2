from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "created_at")
    filter_horizontal = ("participants",)
    search_fields = ("participants__username", "job__title")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "sent_at", "read_at")
    search_fields = ("sender__username", "body")
    list_filter = ("sent_at",)
