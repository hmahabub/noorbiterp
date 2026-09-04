from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from .models import ApprovalRequest


class MyApprovalsView(LoginRequiredMixin, ListView):
    model = ApprovalRequest
    template_name = 'approvals/my_approvals.html'
    context_object_name = 'approvals'

    def get_queryset(self):
        return ApprovalRequest.objects.filter(approver=self.request.user, status='pending')


@login_required
def decide_approval(request, pk, decision):
    approval = get_object_or_404(ApprovalRequest, pk=pk, approver=request.user)
    if decision not in ('approved', 'rejected'):
        messages.error(request, 'Invalid decision.')
        return redirect('approvals:my_approvals')
    approval.status = decision
    approval.decided_at = timezone.now()
    approval.remarks = request.POST.get('remarks', approval.remarks)
    approval.save()

    # Reflect the decision back onto the linked object where applicable
    linked = approval.linked_object
    if linked is not None and hasattr(linked, 'md_approved') and decision == 'approved':
        linked.md_approved = True
        linked.save(update_fields=['md_approved'])

    messages.success(request, f'Request #{approval.pk} marked as {decision}.')
    return redirect('approvals:my_approvals')
