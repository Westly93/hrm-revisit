from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http.response import HttpResponse
from .forms import (
    ContractForm, PositionForm, NextOfKinForm,
    BeneficiaryForm, ChildrenForm, SpouseForm, AcademicQualificationForm,
    LeaveForm
)
from .models import Contract, AcademicQualification, Leave, LeaveBalance

# CONTERACT RELATED FUNCTIONALITY


@require_http_methods(["GET"])
def new_next_of_kin(request, id):
    contract = get_object_or_404(Contract, pk=id)

    form = NextOfKinForm()
    context = {
        "contract": contract,
        "form": form
    }
    return render(request, "contracts/partials/new_next_of_kin.html", context)


@require_http_methods(["POST"])
def add_next_of_kin(request, id):
    contract = get_object_or_404(Contract, pk=id)
    form = NextOfKinForm(request.POST, request.FILES)
    if form.is_valid():
        next_of_kin = form.save(commit=False)
        next_of_kin.employee = contract.employee
        next_of_kin.save()
        messages.success(request, "The next of kin is saved successfully")
        return render(request, "contracts/partials/next_of_kin.html", {"nex_of_kin": next_of_kin, "contract": contract})
    return HttpResponse("")


def new_spouse(request, id):
    contract = get_object_or_404(Contract, pk=id)
    if request.method == "POST":
        form = SpouseForm(request.POST, request.FILES)
        if form.is_valid():
            new_spouse = form.save(commit=False)
            new_spouse.employee = contract.employee
            new_spouse.save()
            messages.success(request, "The spouse is added successfully")
            return render(request, "contracts/partials/spouses.html", {"obj": contract})
    form = SpouseForm()
    context = {
        "form": form,
        "obj": contract
    }
    return render(request, 'contracts/partials/new_spouse.html', context)


def spouses(request, id):
    contract = get_object_or_404(Contract, pk=id)
    context = {
        "obj": contract
    }
    return render(request, "contracts/partials/spouses.html", context)


def qualifications(request, id):
    contract = get_object_or_404(Contract, pk=id)
    context = {
        "obj": contract
    }
    return render(request, "contracts/partials/academic_qualifications.html", context)


def beneficiaries(request, id):
    contract = get_object_or_404(Contract, pk=id)
    context = {
        "obj": contract
    }
    return render(request, "contracts/partials/beneficiaries.html", context)


def academic_qualifications(request, id):
    contract = get_object_or_404(Contract, pk=id)
    if request.method == "POST":
        form = AcademicQualificationForm(request.POST, request.FILES)
        if form.is_valid():
            new_qualification = form.save(commit=False)
            new_qualification.employee = contract.employee
            new_qualification.save()
            messages.success(
                request, "accademic qualification is successfully added")
            context = {
                "obj": contract,
            }
            return render(request, "contracts/partials/academic_qualifications.html", context)
    form = AcademicQualificationForm()
    context = {
        "form": form,
        "contract": contract
    }
    return render(request, 'contracts/partials/new_academic_qualifications.html', context)


def new_beneficiary(request, id):
    contract = get_object_or_404(Contract, pk=id)
    if request.method == "POST":
        form = BeneficiaryForm(request.POST, request.FILES)
        if form.is_valid():
            beneficiary = form.save(commit=False)
            beneficiary.employee = contract.employee
            beneficiary.save()
            messages.success(
                request, "You have successfully added the beneficiary")
            return render(request, "contracts/partials/beneficiaries.html", {"obj": contract})
    form = BeneficiaryForm()
    context = {
        "form": form,
        "obj": contract
    }
    return render(request, 'contracts/partials/new_beneficiary.html', context)


def add_children(request, id):
    contract = get_object_or_404(Contract, pk=id)
    if request.method == "POST":
        form = ChildrenForm(request.POST, request.FILES)
        if form.is_valid():
            new_child = form.save(commit=False)
            new_child.employee = contract.employee
            new_child.save()
            messages.success(request, "The child is added successfully")
            context = {
                "obj": contract
            }
            return render(request, "contracts/partials/children_list.html", context)
    form = ChildrenForm()
    context = {
        "form": form,
        "obj": contract
    }
    return render(request, 'contracts/partials/new_children.html', context)


@require_http_methods(["GET"])
def children_list(request, id):
    contract = get_object_or_404(Contract, pk=id)
    context = {
        "obj": contract
    }
    return render(request, "contracts/partials/children_list.html", context)


def new_contract(request):
    if request.method == "POST":
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save()
            messages.success(request, "Contract is created successfully!!")
            return redirect("contracts:contract_detail", contract.id)
    form = ContractForm()
    context = {
        "form": form
    }
    return render(request, "contracts/new_contract.html", context)


def contract_detail(request, id):
    contract = get_object_or_404(Contract, pk=id)
    context = {
        "obj": contract
    }
    return render(request, "contracts/contract_detail.html", context)


def new_position(request):
    if request.method == "POST":
        form = PositionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Position is created successfully!!")
            return redirect("contracts:new_contract")
    form = PositionForm()
    context = {
        "form": form
    }
    return render(request, "contracts/new_position.html", context)


# LEAVE DAYS AND APPLICATION FUNCTIONALITY
def leave_application(request):
    contract = Contract.objects.get(employee=request.user)
    form = LeaveForm()
    context = {
        "form": form
    }
    return render(request, "contracts/leave_application.html", context)
