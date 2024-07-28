import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from cash_registers.models import CashRegister


@login_required
def get_cash_registers(request):
    result = CashRegister.get_cash_registers()
    return JsonResponse({"result": result})


@login_required
def open_shift(request):
    data = {"cashRegisterId": 1, "shiftId": 1}
    print('открыли такие смену')
    return JsonResponse({"ok": True, "message": "", "data": data})


@login_required
def close_shift(request):
    print('открыли такие смену')
    return JsonResponse({"ok": True, "message": ""})
