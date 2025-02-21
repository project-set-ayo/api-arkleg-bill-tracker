from django.contrib import admin

from .models import Bill, UserBillInteraction, UserKeyword, BillAnalysis


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("bill_number", "admin_stance", "admin_note")
    search_fields = ("bill_number",)
    list_filter = ("admin_stance",)


@admin.register(UserBillInteraction)
class UserBillInteractionAdmin(admin.ModelAdmin):
    list_display = ("id", "bill", "user", "stance")
    search_fields = ("bill__bill_number", "user__username")
    list_filter = ("stance",)


@admin.register(UserKeyword)
class UserKeywordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "keyword")
    search_fields = ("keyword", "user__username")


@admin.register(BillAnalysis)
class BillAnalysisAdmin(admin.ModelAdmin):
    list_display = ("bill", "file_name", "description", "uploaded_at")
    list_filter = ("bill", "uploaded_at")
    search_fields = ("bill__bill_number", "description")
    ordering = ("-uploaded_at",)

    def file_name(self, obj):
        return obj.file.name if obj.file else "No file"

    file_name.short_description = "File Name"
