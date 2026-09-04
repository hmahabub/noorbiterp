def pending_approvals(request):
    if not request.user.is_authenticated:
        return {}
    from apps.approvals.models import ApprovalRequest
    count = ApprovalRequest.objects.filter(approver=request.user, status='pending').count()
    return {'pending_approvals_count': count}
