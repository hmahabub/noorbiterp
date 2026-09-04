from django.contrib import admin

from .models import Commission, Expense, Payment, ProfitabilityRecord


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('order', 'buyer', 'amount', 'currency', 'status', 'due_date')
    list_filter = ('status', 'currency')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'order', 'buyer', 'amount', 'currency', 'approval_status', 'date')
    list_filter = ('approval_status', 'category')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'order', 'buyer', 'vendor', 'amount', 'currency', 'status', 'date')
    list_filter = ('transaction_type', 'status')


@admin.register(ProfitabilityRecord)
class ProfitabilityRecordAdmin(admin.ModelAdmin):
    list_display = ('order', 'revenue', 'contribution', 'contribution_percentage', 'updated_at')
    readonly_fields = ('updated_at',)
