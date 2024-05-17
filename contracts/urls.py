from django.urls import path
from .views import (
    new_contract, new_position, contract_detail, new_next_of_kin,
    new_beneficiary, add_children, new_spouse, academic_qualifications,
    add_next_of_kin, qualifications, beneficiaries, children_list, spouses, leave_application
)

app_name = "contracts"
urlpatterns = [
    # CONTRACT RELATED URLS
    path("new_contract/", new_contract, name="new_contract"),
    path("new_position/", new_position, name="new_position"),
    path("contracts/<int:id>/", contract_detail, name="contract_detail"),
    # LEAVE APPLICATION RELATED URLS
    path("leave-application/", leave_application, name="leave_application"),
]

patial_patterns = [
    path("contracts/<int:id>/new_next_of_kin/",
         new_next_of_kin, name="new_next_of_kin"),
    path("contracts/<int:id>/qualifications/",
         qualifications, name="qualifications"),
    path("contracts/<int:id>/beneficiaries/",
         beneficiaries, name="beneficiaries"),
    path("contracts/<int:id>/children/",
         children_list, name="children_list"),
    path("contracts/<int:id>/spouses/",
         spouses, name="spouses"),
    path("contracts/<int:id>/add_next_of_kin/",
         add_next_of_kin, name="add_next_of_kin"),
    path("contracts/<int:id>/new_beneficiary/",
         new_beneficiary, name="new_beneficiary"),
    path("contracts/<int:id>/add_children/",
         add_children, name="add_children"),
    path("contracts/<int:id>/add_spouse/",
         new_spouse, name="new_spouse"),
    path("contracts/<int:id>/new_academic_qualification/",
         academic_qualifications, name="new_academic_qualification"),

]
urlpatterns += patial_patterns
