"""DTO основных сущностей API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _str(data: Mapping[str, Any], key: str) -> str | None:
    """Приводит значение к строке или возвращает None."""
    value = data.get(key)
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return None


def _int(data: Mapping[str, Any], key: str) -> int | None:
    """Приводит значение к int или возвращает None."""
    value = data.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lstrip("-").isdigit():
        return int(value)
    return None


def _float(data: Mapping[str, Any], key: str) -> float | None:
    """Приводит значение к float или возвращает None."""
    value = data.get(key)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _bool(data: Mapping[str, Any], key: str, default: bool = False) -> bool:
    """Приводит значение к bool."""
    value = data.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _dict(data: Mapping[str, Any], key: str) -> dict[str, Any]:
    """Возвращает словарь по ключу или пустой словарь."""
    value = data.get(key)
    return dict(value) if isinstance(value, Mapping) else {}


def _list(data: Mapping[str, Any], key: str) -> list[Any]:
    """Возвращает список по ключу или пустой список."""
    value = data.get(key)
    return list(value) if isinstance(value, list) else []


@dataclass(frozen=True, slots=True)
class ClientProfile:
    """Анкета клиента для скоринга. Содержит ПДн."""

    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    gender: str | None = None
    inn: str | None = None
    marital_status: str | None = None
    children: str | None = None
    birth_date: str | None = None
    birth_place: str | None = None
    passport_series: str | None = None
    passport_number: str | None = None
    passport_date: str | None = None
    passport_authority: str | None = None
    passport_code: str | None = None
    reg_address: str | None = None
    reg_address_fias: str | None = None
    res_address: str | None = None
    res_address_fias: str | None = None
    consent_pd_date: str | None = None
    credit_history_date: str | None = None
    credit_history_end_date: str | None = None
    marketing_agreed: bool | None = None
    employment_type: str | None = None
    employment_org: str | None = None
    employment_position: str | None = None
    income_salary: int | None = None
    income_extra: int | None = None
    pdl_relation: str | None = None
    pdl_family_relation: str | None = None
    pdl_fio: str | None = None
    pdl_position: str | None = None
    pdl_org: str | None = None
    antifraud_session: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ClientProfile:
        """Создаёт DTO из ответа API."""
        return cls(
            last_name=_str(data, "last_name"),
            first_name=_str(data, "first_name"),
            middle_name=_str(data, "middle_name"),
            gender=_str(data, "gender"),
            inn=_str(data, "inn"),
            marital_status=_str(data, "marital_status"),
            children=_str(data, "children"),
            birth_date=_str(data, "birth_date"),
            birth_place=_str(data, "birth_place"),
            passport_series=_str(data, "passport_series"),
            passport_number=_str(data, "passport_number"),
            passport_date=_str(data, "passport_date"),
            passport_authority=_str(data, "passport_authority"),
            passport_code=_str(data, "passport_code"),
            reg_address=_str(data, "reg_address"),
            reg_address_fias=_str(data, "reg_address_fias"),
            res_address=_str(data, "res_address"),
            res_address_fias=_str(data, "res_address_fias"),
            consent_pd_date=_str(data, "consent_pd_date"),
            credit_history_date=_str(data, "credit_history_date"),
            credit_history_end_date=_str(data, "credit_history_end_date"),
            marketing_agreed=_bool(data, "marketing_agreed") if data.get("marketing_agreed") is not None else None,
            employment_type=_str(data, "employment_type"),
            employment_org=_str(data, "employment_org"),
            employment_position=_str(data, "employment_position"),
            income_salary=_int(data, "income_salary"),
            income_extra=_int(data, "income_extra"),
            pdl_relation=_str(data, "pdl_relation"),
            pdl_family_relation=_str(data, "pdl_family_relation"),
            pdl_fio=_str(data, "pdl_fio"),
            pdl_position=_str(data, "pdl_position"),
            pdl_org=_str(data, "pdl_org"),
            antifraud_session=_str(data, "antifraud_session"),
            raw=dict(data),
        )

    def to_dict(self) -> dict[str, Any]:
        """Возвращает исходные данные API."""
        return dict(self.raw)


@dataclass(frozen=True, slots=True)
class Auction:
    """DTO карточки аукциона."""

    id: int
    uuid: str | None = None
    title: str | None = None
    status: str | None = None
    is_own: bool = False
    can_bid: bool = False
    can_manage: bool = False
    can_select_winner: bool = False
    creator_id: int | None = None
    comment: str | None = None
    client: dict[str, Any] = field(default_factory=dict)
    client_profile: ClientProfile | None = None
    city: str | None = None
    city_fias: str | None = None
    vin: str | None = None
    make: str | None = None
    model: str | None = None
    car_year: int | None = None
    engine: str | None = None
    fuel_type: str | None = None
    power: int | None = None
    engine_capacity: float | None = None
    required_amount: float | None = None
    pts_series: str | None = None
    pts_number: str | None = None
    pts_date: str | None = None
    pts_issued_by: str | None = None
    sts_series: str | None = None
    sts_number: str | None = None
    sts_date: str | None = None
    photos: dict[str, Any] = field(default_factory=dict)
    bids_count: int = 0
    created_at: str | None = None
    updated_at: str | None = None
    started_at: str | None = None
    ends_at: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Auction:
        """Создаёт DTO аукциона из ответа API."""
        auction_id = _int(data, "id")
        if auction_id is None:
            raise ValueError("Auction payload must contain an integer id")
        profile = data.get("client_profile")
        return cls(
            id=auction_id,
            uuid=_str(data, "uuid"),
            title=_str(data, "title"),
            status=_str(data, "status"),
            is_own=_bool(data, "is_own"),
            can_bid=_bool(data, "can_bid"),
            can_manage=_bool(data, "can_manage"),
            can_select_winner=_bool(data, "can_select_winner"),
            creator_id=_int(data, "creator_id"),
            comment=_str(data, "comment"),
            client=_dict(data, "client"),
            client_profile=ClientProfile.from_dict(profile) if isinstance(profile, Mapping) else None,
            city=_str(data, "city"),
            city_fias=_str(data, "city_fias"),
            vin=_str(data, "vin"),
            make=_str(data, "make"),
            model=_str(data, "model"),
            car_year=_int(data, "car_year"),
            engine=_str(data, "engine"),
            fuel_type=_str(data, "fuel_type"),
            power=_int(data, "power"),
            engine_capacity=_float(data, "engine_capacity"),
            required_amount=_float(data, "required_amount"),
            pts_series=_str(data, "pts_series"),
            pts_number=_str(data, "pts_number"),
            pts_date=_str(data, "pts_date"),
            pts_issued_by=_str(data, "pts_issued_by"),
            sts_series=_str(data, "sts_series"),
            sts_number=_str(data, "sts_number"),
            sts_date=_str(data, "sts_date"),
            photos=_dict(data, "photos"),
            bids_count=_int(data, "bids_count") or 0,
            created_at=_str(data, "created_at"),
            updated_at=_str(data, "updated_at"),
            started_at=_str(data, "started_at"),
            ends_at=_str(data, "ends_at"),
            raw=dict(data),
        )

    def to_dict(self) -> dict[str, Any]:
        """Возвращает исходные данные API."""
        return dict(self.raw)


@dataclass(frozen=True, slots=True)
class Bid:
    """DTO ставки партнёра."""

    id: int
    auction_id: int | None = None
    amount: float | None = None
    interest_rate: float | None = None
    rate_period: str | None = None
    is_final: bool = False
    term: int | None = None
    comment: str | None = None
    bid_number: int | None = None
    partner_name: str | None = None
    partner_id: int | None = None
    created_at: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], auction_id: int | None = None) -> Bid:
        """Создаёт DTO ставки из ответа API."""
        bid_id = _int(data, "id")
        if bid_id is None:
            raise ValueError("Bid payload must contain an integer id")
        return cls(
            id=bid_id,
            auction_id=auction_id,
            amount=_float(data, "amount"),
            interest_rate=_float(data, "interest_rate"),
            rate_period=_str(data, "rate_period"),
            is_final=_bool(data, "is_final"),
            term=_int(data, "term"),
            comment=_str(data, "comment"),
            bid_number=_int(data, "bid_number"),
            partner_name=_str(data, "partner_name"),
            partner_id=_int(data, "partner_id"),
            created_at=_str(data, "created_at"),
            raw=dict(data),
        )

    def to_dict(self) -> dict[str, Any]:
        """Возвращает исходные данные API."""
        return dict(self.raw)


@dataclass(frozen=True, slots=True)
class DealDocument:
    """DTO документа сделки."""

    id: str
    original_name: str | None = None
    path: str | None = None
    mime: str | None = None
    size: int | None = None
    uploaded_by: str | None = None
    uploaded_at: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> DealDocument:
        """Создаёт DTO документа из ответа API."""
        document_id = _str(data, "id")
        if not document_id:
            raise ValueError("Deal document payload must contain an id")
        return cls(
            id=document_id,
            original_name=_str(data, "original_name"),
            path=_str(data, "path"),
            mime=_str(data, "mime"),
            size=_int(data, "size"),
            uploaded_by=_str(data, "uploaded_by"),
            uploaded_at=_str(data, "uploaded_at"),
            raw=dict(data),
        )

    def to_dict(self) -> dict[str, Any]:
        """Возвращает исходные данные API."""
        return dict(self.raw)


@dataclass(frozen=True, slots=True)
class Deal:
    """DTO сделки."""

    id: int
    uuid: str | None = None
    auction_id: int | None = None
    partner_id: int | None = None
    manager_id: int | None = None
    client_id: int | None = None
    status: str | None = None
    status_name: str | None = None
    notes: str | None = None
    requisites: Any = None
    documents: list[dict[str, Any]] = field(default_factory=list)
    client: dict[str, Any] = field(default_factory=dict)
    client_profile: ClientProfile | None = None
    bid: dict[str, Any] = field(default_factory=dict)
    auction: dict[str, Any] = field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None
    completed_at: str | None = None
    cancelled_at: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Deal:
        """Создаёт DTO сделки из ответа API."""
        deal_id = _int(data, "id")
        if deal_id is None:
            raise ValueError("Deal payload must contain an integer id")
        profile = data.get("client_profile")
        return cls(
            id=deal_id,
            uuid=_str(data, "uuid"),
            auction_id=_int(data, "auction_id"),
            partner_id=_int(data, "partner_id"),
            manager_id=_int(data, "manager_id"),
            client_id=_int(data, "client_id"),
            status=_str(data, "status"),
            status_name=_str(data, "status_name"),
            notes=_str(data, "notes"),
            requisites=data.get("requisites"),
            documents=_list(data, "documents"),
            client=_dict(data, "client"),
            client_profile=ClientProfile.from_dict(profile) if isinstance(profile, Mapping) else None,
            bid=_dict(data, "bid"),
            auction=_dict(data, "auction"),
            created_at=_str(data, "created_at"),
            updated_at=_str(data, "updated_at"),
            completed_at=_str(data, "completed_at"),
            cancelled_at=_str(data, "cancelled_at"),
            raw=dict(data),
        )

    def document_objects(self) -> list[DealDocument]:
        """Возвращает документы как DTO."""
        return [DealDocument.from_dict(item) for item in self.documents if isinstance(item, Mapping)]

    def to_dict(self) -> dict[str, Any]:
        """Возвращает исходные данные API."""
        return dict(self.raw)


@dataclass(frozen=True, slots=True)
class Webhook:
    """DTO вебхука без секрета."""

    id: int
    url: str | None = None
    events: list[str] = field(default_factory=list)
    headers: dict[str, Any] = field(default_factory=dict)
    active: bool = True
    failing: bool = False
    consecutive_failures: int = 0
    has_secret: bool = False
    created_at: str | None = None
    updated_at: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Webhook:
        """Создаёт DTO вебхука из ответа API."""
        webhook_id = _int(data, "id")
        if webhook_id is None:
            raise ValueError("Webhook payload must contain an integer id")
        return cls(
            id=webhook_id,
            url=_str(data, "url"),
            events=[str(item) for item in _list(data, "events")],
            headers=_dict(data, "headers"),
            active=_bool(data, "active", True),
            failing=_bool(data, "failing"),
            consecutive_failures=_int(data, "consecutive_failures") or 0,
            has_secret=_bool(data, "has_secret"),
            created_at=_str(data, "created_at"),
            updated_at=_str(data, "updated_at"),
            raw=dict(data),
        )

    def to_dict(self) -> dict[str, Any]:
        """Возвращает исходные данные API."""
        return dict(self.raw)
