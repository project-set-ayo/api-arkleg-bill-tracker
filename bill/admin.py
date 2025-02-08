from django.contrib import admin

from .models import Bill, UserBillInteraction, UserKeyword


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'admin_stance', 'admin_note')
    search_fields = ('bill_number',)
    list_filter = ('admin_stance',)

@admin.register(UserBillInteraction)
class UserBillInteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'bill', 'user', 'stance')
    search_fields = ('bill__bill_number', 'user__username')
    list_filter = ('stance',)

@admin.register(UserKeyword)
class UserKeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'keyword')
    search_fields = ('keyword', 'user__username')
