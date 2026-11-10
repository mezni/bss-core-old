"""REST endpoints for customer management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from fastapi import status as http_status

from ..application.commands import (
    AddAddressCommand,
    AddContactCommand,
    CreateCustomerCommand,
    DeactivateCustomerCommand,
    ReactivateCustomerCommand,
    RemoveAddressCommand,
    RemoveContactCommand,
    UpdateAddressCommand,
    UpdateContactCommand,
    UpdateCustomerCommand,
)
from ..application.dto import CustomerDetailsDTO, CustomerListDTO
from ..application.queries import CustomerSearchQuery
from ..application.use_cases import CustomerService
from ..domain.value_objects import CustomerStatus, CustomerType
from .dependencies import (
    get_customer_service,
    require_customer_manage,
    require_customer_view,
)
from .schemas import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
    EligibilityResponse,
    VersionRequest,
)

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


def _details(dto: CustomerDetailsDTO) -> CustomerResponse:
    return CustomerResponse.model_validate(dto)


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Depends(require_customer_manage)],
)
def create_customer(
    payload: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    command = CreateCustomerCommand(
        customer_type=payload.customer_type,
        display_name=payload.display_name,
        first_name=payload.first_name,
        last_name=payload.last_name,
        legal_name=payload.legal_name,
        email=payload.email,
        registration_number=payload.registration_number,
    )
    return _details(service.create(command))


@router.get(
    "",
    response_model=CustomerListResponse,
    dependencies=[Depends(require_customer_view)],
)
def list_customers(
    q: str | None = Query(default=None),
    customer_type: CustomerType | None = Query(default=None),
    status: CustomerStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerListResponse:
    result: CustomerListDTO = service.search(
        CustomerSearchQuery(
            q=q,
            customer_type=customer_type,
            status=status,
            page=page,
            page_size=page_size,
        )
    )
    return CustomerListResponse.model_validate(result)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    dependencies=[Depends(require_customer_view)],
)
def get_customer(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return _details(service.get(customer_id))


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    dependencies=[Depends(require_customer_manage)],
)
def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    changes = payload.model_dump(exclude_unset=True)
    version = int(changes.pop("version"))
    command = UpdateCustomerCommand(customer_id=customer_id, version=version, changes=changes)
    return _details(service.update(command))


@router.post(
    "/{customer_id}/deactivate",
    response_model=CustomerResponse,
    dependencies=[Depends(require_customer_manage)],
)
def deactivate_customer(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return _details(service.deactivate(DeactivateCustomerCommand(customer_id)))


@router.post(
    "/{customer_id}/reactivate",
    response_model=CustomerResponse,
    dependencies=[Depends(require_customer_manage)],
)
def reactivate_customer(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return _details(service.reactivate(ReactivateCustomerCommand(customer_id)))


@router.get(
    "/{customer_id}/eligibility",
    response_model=EligibilityResponse,
    dependencies=[Depends(require_customer_view)],
)
def get_eligibility(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
) -> EligibilityResponse:
    return EligibilityResponse.model_validate(service.check_eligibility(customer_id))


@router.post(
    "/{customer_id}/contacts",
    response_model=ContactResponse,
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Depends(require_customer_manage)],
)
def add_contact(
    customer_id: str,
    payload: ContactCreate,
    service: CustomerService = Depends(get_customer_service),
) -> ContactResponse:
    command = AddContactCommand(
        customer_id=customer_id,
        name=payload.name,
        contact_type=payload.contact_type,
        value=payload.value,
        is_primary=payload.is_primary,
    )
    return ContactResponse.model_validate(service.add_contact(command))


@router.patch(
    "/{customer_id}/contacts/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(require_customer_manage)],
)
def update_contact(
    customer_id: str,
    contact_id: str,
    payload: ContactUpdate,
    service: CustomerService = Depends(get_customer_service),
) -> ContactResponse:
    changes = payload.model_dump(exclude_unset=True)
    version = int(changes.pop("version"))
    command = UpdateContactCommand(
        customer_id=customer_id,
        contact_id=contact_id,
        version=version,
        changes=changes,
    )
    return ContactResponse.model_validate(service.update_contact(command))


@router.delete(
    "/{customer_id}/contacts/{contact_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_customer_manage)],
)
def remove_contact(
    customer_id: str,
    contact_id: str,
    payload: VersionRequest,
    service: CustomerService = Depends(get_customer_service),
) -> Response:
    service.remove_contact(
        RemoveContactCommand(
            customer_id=customer_id,
            contact_id=contact_id,
            version=payload.version,
        )
    )
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)


@router.post(
    "/{customer_id}/addresses",
    response_model=AddressResponse,
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Depends(require_customer_manage)],
)
def add_address(
    customer_id: str,
    payload: AddressCreate,
    service: CustomerService = Depends(get_customer_service),
) -> AddressResponse:
    command = AddAddressCommand(
        customer_id=customer_id,
        label=payload.label,
        line1=payload.line1,
        line2=payload.line2,
        city=payload.city,
        region=payload.region,
        postal_code=payload.postal_code,
        country=payload.country,
        is_primary=payload.is_primary,
    )
    return AddressResponse.model_validate(service.add_address(command))


@router.patch(
    "/{customer_id}/addresses/{address_id}",
    response_model=AddressResponse,
    dependencies=[Depends(require_customer_manage)],
)
def update_address(
    customer_id: str,
    address_id: str,
    payload: AddressUpdate,
    service: CustomerService = Depends(get_customer_service),
) -> AddressResponse:
    changes = payload.model_dump(exclude_unset=True)
    version = int(changes.pop("version"))
    command = UpdateAddressCommand(
        customer_id=customer_id,
        address_id=address_id,
        version=version,
        changes=changes,
    )
    return AddressResponse.model_validate(service.update_address(command))


@router.delete(
    "/{customer_id}/addresses/{address_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_customer_manage)],
)
def remove_address(
    customer_id: str,
    address_id: str,
    payload: VersionRequest,
    service: CustomerService = Depends(get_customer_service),
) -> Response:
    service.remove_address(
        RemoveAddressCommand(
            customer_id=customer_id,
            address_id=address_id,
            version=payload.version,
        )
    )
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)


__all__ = ["router"]
