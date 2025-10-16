"""
GLS ShipIT carrier adapter.

Implementa GlsAdapter para crear envíos, cancelar, consultar servicios
y ejecutar end of day en GLS ShipIT (REST v1).
"""

import base64
import httpx
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..interfaces.carrier import CarrierAdapter
from ...core.settings import settings

logger = logging.getLogger(__name__)


class GlsAdapter(CarrierAdapter):
    """GLS ShipIT carrier adapter implementation."""

    def __init__(self):
        # Settings esperadas en tu config
        self.base_url: str = settings.gls_base_url.rstrip("/")
        self.auth_url: str = getattr(settings, "gls_auth_url", "https://api-sandbox.gls-group.net/oauth2/v2/token")
        self.client_id: str = getattr(settings, "gls_client_id", settings.gls_username)  # OAuth2 client_id
        self.client_secret: str = getattr(settings, "gls_client_secret", settings.gls_password)  # OAuth2 client_secret
        self.username: str = settings.gls_username  # Para Basic Auth (fallback)
        self.password: str = settings.gls_password
        self.requester: Optional[str] = getattr(settings, "gls_requester", None)
        self.shipper_contact_id: str = settings.gls_contact_id
        self.label_format: str = getattr(settings, "gls_label_format", "PDF")
        self.template_set: str = getattr(settings, "gls_template_set", "NONE")
        self.mock_mode: bool = getattr(settings, "gls_mock_mode", False)
        self.use_oauth: bool = getattr(settings, "gls_use_oauth", True)  # True para OAuth2, False para Basic
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

        # Endpoints oficiales según OpenAPI spec
        self.endpoints = {
            "shipments": f"{self.base_url}/rs/shipments",  # POST - create shipments
            "validate": f"{self.base_url}/rs/shipments/validate",  # POST - validate before create
            "cancel": f"{self.base_url}/rs/shipments/cancel/{{track_id}}",  # POST - cancel parcel
            "allowed_services": f"{self.base_url}/rs/shipments/allowedservices",  # POST
            "end_of_day": f"{self.base_url}/rs/shipments/endofday",  # POST ?date=YYYY-MM-DD
            "reprint": f"{self.base_url}/rs/shipments/reprintparcel",  # POST - reprint label
            "tracking_parcels": f"{self.base_url}/rs/tracking/parcels",  # POST - find parcels
            "tracking_details": f"{self.base_url}/rs/tracking/parceldetails",  # POST - get parcel details
            "tracking_pod": f"{self.base_url}/rs/tracking/parcelpod",  # POST - get proof of delivery
        }

        # cache sencilla de idempotencia
        self._idempotency_keys = set()

    # ---- Identidad del carrier ----
    @property
    def carrier_name(self) -> str:
        return "GLS ShipIT"

    @property
    def carrier_code(self) -> str:
        return "gls"

    @property
    def is_mock_mode(self) -> bool:
        return self.mock_mode

    # ---- Utils de autenticación OAuth2 y headers ----
    async def _get_oauth_token(self) -> str:
        """Obtiene un token OAuth2 del servidor de GLS."""
        # Si ya tenemos un token válido, lo reutilizamos
        if self._access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
                return self._access_token
        
        # Solicitar nuevo token
        logger.info("[GLS] Solicitando nuevo token OAuth2...")
        
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                resp = await client.post(
                    self.auth_url,
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                resp.raise_for_status()
                data = resp.json()
                
                self._access_token = data["access_token"]
                expires_in = data.get("expires_in", 3600)  # Default 1 hora
                self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)  # 1 min de margen
                
                logger.info(f"[GLS] Token OAuth2 obtenido, expira en {expires_in}s")
                return self._access_token
                
        except Exception as e:
            logger.error(f"[GLS] Error obteniendo token OAuth2: {e}")
            raise Exception(f"Failed to obtain OAuth2 token: {e}") from e
    
    def _auth_header_basic(self) -> str:
        """Genera header de autenticación Basic (fallback)."""
        token = base64.b64encode(f"{self.username}:{self.password}".encode("utf-8")).decode("ascii")
        return f"Basic {token}"

    async def _headers(self) -> Dict[str, str]:
        """Genera headers HTTP incluyendo autenticación."""
        if self.use_oauth and not self.mock_mode:
            # Usar OAuth2
            token = await self._get_oauth_token()
            auth = f"Bearer {token}"
        else:
            # Usar Basic Auth (para mock o configuración legacy)
            auth = self._auth_header_basic()
        
        headers = {
            "Authorization": auth,
            "Accept": "application/glsVersion1+json, application/json",
            "Content-Type": "application/glsVersion1+json",
        }
        if self.requester:
            headers["Requester"] = self.requester
        return headers

    # ---- Validación de envío (antes de crear) ----
    async def validate_shipment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /rs/shipments/validate
        Valida un envío antes de crearlo para detectar errores de configuración.
        Útil para validar datos antes de crear el envío real.
        """
        if self.mock_mode:
            return {
                "Success": True,
                "ValidationResult": {
                    "Issues": []
                },
                "message": "Mock validation: shipment is valid"
            }

        payload = self._transform_order_to_gls_request(order_data)
        # Para validate solo necesitamos el Shipment, no PrintingOptions
        validate_payload = {"Shipment": payload["Shipment"]}
        
        headers = await self._headers()

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
            try:
                resp = await client.post(
                    self.endpoints["validate"],
                    headers=headers,
                    json=validate_payload
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"[GLS] Validate shipment error: {e.response.text}")
                body = None
                try:
                    body = e.response.json()
                except Exception:
                    body = {"raw": e.response.text[:500]}
                raise Exception(f"GLS validation error {e.response.status_code}: {body}") from e

        return resp.json()

    # ---- Creación de envío (F-114) ----
    async def create_shipment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.mock_mode:
            return await self._create_shipment_mock(order_data)
        return await self._create_shipment_real(order_data)

    async def _create_shipment_mock(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        order_id = order_data.get("order_id", "UNKNOWN")
        weight = float(order_data.get("weight", 1.0))
        track_id = f"GLS{hash(order_id) % 10_000_000:07d}"
        shipment_id = track_id  # en GLS la clave operativa es TrackID por paquete

        result = {
            "shipment_id": shipment_id,
            "track_id": track_id,
            "status": "CREATED",
            "estimated_delivery": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "cost": 14.90 + (weight * 2.2),
            "currency": "EUR",
            "carrier": self.carrier_code,
            "service": "PARCEL",
            "created_at": datetime.utcnow().isoformat(),
            # Simulamos label PDF inline:
            "label": {
                "format": "PDF",
                "bytes_b64": base64.b64encode(
                    f"GLS MOCK LABEL\nTrackID: {track_id}\n".encode("utf-8")
                ).decode("ascii"),
            },
        }
        logger.info(f"[MOCK][GLS] Created shipment track_id={track_id}")
        return result

    async def _create_shipment_real(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._transform_order_to_gls_request(order_data)
        headers = await self._headers()

        timeout = httpx.Timeout(20.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.post(self.endpoints["shipments"], headers=headers, json=payload)
                resp.raise_for_status()
            except httpx.TimeoutException as e:
                logger.error("[GLS] Timeout creating shipment", exc_info=True)
                raise Exception(f"GLS timeout: {e}") from e
            except httpx.HTTPStatusError as e:
                body = None
                try:
                    body = e.response.json()
                except Exception:
                    body = {"raw": e.response.text[:500]}
                # ShipIT suele mandar 'message', 'error', 'args' en headers ó body
                msg = body.get("message") if isinstance(body, dict) else None
                code = body.get("error") if isinstance(body, dict) else None
                args = body.get("args") if isinstance(body, dict) else None
                logger.error(f"[GLS] HTTP {e.response.status_code} error; code={code} msg={msg} args={args} raw={body}")
                raise Exception(f"GLS error {e.response.status_code}: {code} {msg} {args}") from e

        data = resp.json()

        # Normalizamos a nuestro contrato (track_id + label embebido si ReturnLabels)
        created = data.get("CreatedShipment", {})
        parcels = created.get("ParcelData", []) or []
        track_id = parcels[0].get("TrackID") if parcels else None

        # Lectura robusta del label (ReturnLabels)
        # En algunos despliegues el label viene como { "PrintData": { "Format": "PDF", "Content": "<b64>" } },
        # en otros como lista/documentos. Añade fallback:
        print_data = created.get("PrintData") or data.get("PrintData")
        label_norm = None
        if print_data:
            # caso objeto directo
            if isinstance(print_data, dict) and print_data.get("Content"):
                label_norm = {"format": print_data.get("Format", self.label_format),
                              "bytes_b64": print_data["Content"]}
            # caso lista de documentos
            elif isinstance(print_data, list) and print_data:
                doc = print_data[0]
                if isinstance(doc, dict) and doc.get("Content"):
                    label_norm = {"format": doc.get("Format", self.label_format),
                                  "bytes_b64": doc["Content"]}

        result = {
            "shipment_id": track_id,
            "track_id": track_id,
            "status": "CREATED" if track_id else "UNKNOWN",
            "carrier": self.carrier_code,
            "service": "PARCEL" if payload.get("Shipment", {}).get("Product") == "PARCEL" else "EXPRESS",
            "raw": data,  # útil para auditoría
        }
        if label_norm:
            result["label"] = label_norm

        return result

    # ---- Bulk ----
    async def create_shipments_bulk(self, orders_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        # GLS no publica un endpoint bulk en ShipIT; iteramos (respetando idempotencia si la usas arriba)
        created, failed = [], []
        for order in orders_data:
            try:
                made = await self.create_shipment(order)
                created.append(made)
            except Exception as e:
                failed.append({"order": order.get("order_id"), "error": str(e)})
        return {
            "shipments": created,
            "total_created": len(created),
            "total_failed": len(failed),
            "failed": failed,
            "currency": "EUR",
        }

    # ---- Estado / tracking ----
    async def get_shipment_status(self, shipment_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado detallado de un envío por TrackID usando /rs/tracking/parceldetails.
        Retorna información normalizada de tracking.
        """
        if self.mock_mode:
            return await self._get_shipment_status_mock(shipment_id)
        return await self._get_tracking_details_real(shipment_id)

    async def _get_shipment_status_mock(self, shipment_id: str) -> Dict[str, Any]:
        states = ["CREATED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"]
        status = states[hash(shipment_id) % len(states)]
        return {
            "shipment_id": shipment_id,
            "track_id": shipment_id,
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
            "carrier": self.carrier_code,
            "events": [
                {
                    "date": datetime.utcnow().isoformat(),
                    "status_code": status,
                    "description": f"Mock status: {status}",
                    "location": "Madrid",
                    "country": "ES"
                }
            ]
        }

    async def _get_tracking_details_real(self, track_id: str) -> Dict[str, Any]:
        """
        POST /rs/tracking/parceldetails
        Obtiene detalles completos de tracking incluyendo historial de eventos.
        """
        headers = await self._headers()
        payload = {"TrackID": track_id}

        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0)) as client:
            try:
                resp = await client.post(
                    self.endpoints["tracking_details"],
                    headers=headers,
                    json=payload
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"[GLS] Tracking details error for {track_id}: {e.response.text}")
                raise Exception(f"GLS tracking error {e.response.status_code}: {e.response.text}") from e

        data = resp.json()
        unit_detail = data.get("UnitDetail", {})
        
        # Normalizar historia de eventos
        history = unit_detail.get("History", [])
        events = []
        for h in history:
            events.append({
                "date": h.get("Date"),
                "status_code": h.get("StatusCode"),
                "description": h.get("Description"),
                "location": h.get("Location"),
                "location_code": h.get("LocationCode"),
                "country": h.get("Country")
            })

        # Determinar status general basado en último evento
        status = "UNKNOWN"
        if history:
            last_status = history[-1].get("StatusCode", "")
            # Mapeo aproximado de códigos GLS a estados estándar
            if "DELIVER" in last_status.upper():
                status = "DELIVERED"
            elif "OUT" in last_status.upper() or "DELIVERY" in last_status.upper():
                status = "OUT_FOR_DELIVERY"
            elif "TRANSIT" in last_status.upper() or "HUB" in last_status.upper():
                status = "IN_TRANSIT"
            elif "PICKUP" in last_status.upper() or "COLLECT" in last_status.upper():
                status = "PICKED_UP"
            else:
                status = "IN_TRANSIT"

        return {
            "shipment_id": track_id,
            "track_id": track_id,
            "status": status,
            "weight": unit_detail.get("Weight"),
            "delivery_date": unit_detail.get("DeliveryDate"),
            "signature": unit_detail.get("Signature"),
            "product": unit_detail.get("Product"),
            "updated_at": datetime.utcnow().isoformat(),
            "carrier": self.carrier_code,
            "events": events,
            "raw": data  # Para auditoría completa
        }

    async def find_parcels(
        self,
        *,
        track_id: Optional[str] = None,
        shipment_reference: Optional[str] = None,
        shipment_unit_reference: Optional[str] = None,
        parcel_number: Optional[str] = None,
        partner_parcel_number: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        POST /rs/tracking/parcels
        Busca paquetes por diferentes referencias en un rango de fechas.
        Útil para consultas masivas o cuando no tienes el TrackID exacto.
        """
        if self.mock_mode:
            return {
                "UnitItems": [
                    {
                        "TrackID": track_id or "MOCK12345",
                        "ParcelNumber": parcel_number or "1234567890",
                        "Status": "IN_TRANSIT",
                        "InitialDate": datetime.utcnow().isoformat()
                    }
                ]
            }

        headers = await self._headers()
        
        # date_from y date_to son requeridos según spec
        if not date_from or not date_to:
            raise ValueError("date_from and date_to are required for find_parcels")

        payload: Dict[str, Any] = {
            "DateFrom": date_from.isoformat() if isinstance(date_from, datetime) else date_from,
            "DateTo": date_to.isoformat() if isinstance(date_to, datetime) else date_to,
        }
        
        # Agregar referencias opcionales
        if track_id:
            payload["TrackID"] = track_id
        if shipment_reference:
            payload["ShipmentReference"] = shipment_reference
        if shipment_unit_reference:
            payload["ShipmentUnitReference"] = shipment_unit_reference
        if parcel_number:
            payload["ParcelNumber"] = parcel_number
        if partner_parcel_number:
            payload["PartnerParcelNumber"] = partner_parcel_number

        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0)) as client:
            try:
                resp = await client.post(
                    self.endpoints["tracking_parcels"],
                    headers=headers,
                    json=payload
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"[GLS] Find parcels error: {e.response.text}")
                raise Exception(f"GLS find parcels error {e.response.status_code}: {e.response.text}") from e

        return resp.json()

    # ---- Labels ----
    async def get_shipment_label(self, shipment_id: str) -> bytes:
        """
        ShipIT devuelve etiquetas en la creación si usas ReturnLabels.
        Aquí asumimos que guardaste 'label.bytes_b64' tras create_shipment.
        Si necesitas re-hidratar, deberás persistirla o reemitir create (no ideal).
        """
        if self.mock_mode:
            return base64.b64decode(
                base64.b64encode(f"GLS MOCK LABEL\nTrackID: {shipment_id}\n".encode("utf-8"))
            )
        raise NotImplementedError(
            "Persistencia de etiquetas no implementada. Guarda la respuesta de create_shipment."
        )

    # ---- Cancelación (F-116) ----
    async def cancel_shipment(self, shipment_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        if self.mock_mode:
            return {
                "track_id": shipment_id,
                "result": "CANCELLATION_PENDING",
                "cancelled_at": datetime.utcnow().isoformat(),
                "reason": reason,
                "mock": True,
            }

        headers = await self._headers()
        url = self.endpoints["cancel"].format(track_id=shipment_id)

        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0)) as client:
            try:
                resp = await client.post(url, headers=headers)
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"[GLS] Cancel error: {e.response.text}")
                raise
        return resp.json()

    # ---- Servicios permitidos (F-117) ----
    async def get_allowed_services(
        self,
        source_country: str,
        source_zip: str,
        dest_country: str,
        dest_zip: str,
        contact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.mock_mode:
            return {
                "AllowedServices": [
                    {"ProductName": "PARCEL"},
                    {"ProductName": "EXPRESS"},
                    {"ServiceName": "service_cash"},
                    {"ServiceName": "service_flexdelivery"},
                ]
            }

        headers = await self._headers()
        body = {
            "Source": {"CountryCode": source_country, "ZIPCode": source_zip},
            "Destination": {"CountryCode": dest_country, "ZIPCode": dest_zip},
        }
        if contact_id:
            body["ContactID"] = contact_id

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
            resp = await client.post(self.endpoints["allowed_services"], headers=headers, json=body)
            resp.raise_for_status()
            return resp.json()

    # ---- End of day (F-118) ----
    async def run_end_of_day(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecuta cierre de día y retorna envíos afectados.
        date: 'YYYY-MM-DD' (si None, hoy en UTC)
        """
        if self.mock_mode:
            return {
                "Shipments": [
                    {
                        "ShippingDate": (datetime.utcnow().date()).isoformat(),
                        "Product": "PARCEL",
                        "Shipper": {"ContactID": self.shipper_contact_id},
                        "ShipmentUnit": [{"Weight": "3.4", "TrackID": "GLS0001234"}],
                    }
                ]
            }

        headers = await self._headers()
        the_date = date or datetime.utcnow().date().isoformat()
        url = f"{self.endpoints['end_of_day']}?date={the_date}"

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=8.0)) as client:
            resp = await client.post(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    # ---- Idempotencia (igual patrón que TIPSA) ----
    def _generate_idempotency_key(self, order_data: Dict[str, Any]) -> str:
        addr = order_data.get("shipping_address", {}) or {}
        key_data = f"{order_data.get('order_id','')}_{order_data.get('weight',0)}_{addr.get('postal_code','')}_{addr.get('city','')}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    async def create_shipment_with_idempotency(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        key = self._generate_idempotency_key(order_data)
        if key in self._idempotency_keys:
            logger.info(f"[GLS] Idempotent hit key={key}")
            return await self._get_cached_shipment(key)
        res = await self.create_shipment(order_data)
        # en GLS usamos track_id como identificador
        res["expedition_id"] = res.get("track_id")
        self._idempotency_keys.add(key)
        return res

    async def _get_cached_shipment(self, idem_key: str) -> Dict[str, Any]:
        return {
            "shipment_id": f"CACHED-{idem_key[:8]}",
            "expedition_id": f"CACHED-{idem_key[:8]}",
            "track_id": f"CACHED-{idem_key[:8]}",
            "status": "CREATED",
            "cached": True,
        }

    # ---- Transformación de nuestro pedido → GLS ShipIT (F-114) ----
    def _transform_order_to_gls_request(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapea nuestro order_data (Mirakl/standard) al body GLS:
        {
          "Shipment": {...},
          "PrintingOptions": {...},
          "CustomContent": {...} (opcional)
        }
        """
        addr = order_data.get("shipping_address", {}) or {}
        weight = float(order_data.get("weight", 1.0))
        product = "EXPRESS" if order_data.get("service") == "EXPRESS" else "PARCEL"

        # Consignee Address (mínimos) con saneado de strings y StreetNumber desde address2
        street = (addr.get("street") or addr.get("address1") or "Calle Desconocida").strip()
        number = (addr.get("street_number") or addr.get("address2") or "").strip()
        consignee_address = {
            "Name1": (order_data.get("customer_name") or addr.get("name") or "Cliente")[:40],
            "CountryCode": (addr.get("country_code") or addr.get("country") or "ES")[:2],
            "ZIPCode": (addr.get("postal_code") or addr.get("zip") or "28001")[:10],
            "City": (addr.get("city") or "Madrid")[:40],
            "Street": street[:40],
        }
        if number:
            consignee_address["StreetNumber"] = number[:40]
        if order_data.get("customer_email"):
            consignee_address["eMail"] = order_data["customer_email"]
        if addr.get("phone"):
            consignee_address["MobilePhoneNumber"] = addr["phone"]

        # Shipper (ContactID obligatorio; alt address opcional)
        shipper = {"ContactID": self.shipper_contact_id}

        # Shipment Unit (peso obligatorio; refs opcionales)
        unit: Dict[str, Any] = {"Weight": weight}
        # referencias opcionales para trazabilidad
        if order_data.get("order_id"):
            unit["ShipmentUnitReference"] = [str(order_data["order_id"])]

        # Servicios: ejemplo FlexDelivery si 2C y Cash si reembolso
        services_shipment: List[Dict[str, Any]] = []
        if order_data.get("delivery_flex", False):
            services_shipment.append({"Service": {"ServiceName": "service_flexdelivery"}})

        # Cash-on-delivery (reembolso)
        cod = order_data.get("cod_amount") or order_data.get("cash_on_delivery")
        if cod:
            unit.setdefault("Service", [])
            unit["Service"].append(
                {
                    "Cash": {
                        "ServiceName": "service_cash",
                        "Reason": f"Order {order_data.get('order_id')}",
                        "Amount": f"{float(cod):.2f}",
                        "Currency": order_data.get("currency", "EUR"),
                    }
                }
            )

        # Incoterm para destinos aduaneros (ej. CH, UY...)
        incoterm = None
        dest_cc = consignee_address.get("CountryCode", "ES").upper()
        if dest_cc in {"CH", "GB", "NO", "IS", "LI", "UY"}:
            incoterm = order_data.get("incoterm") or "10"  # DAP by default per doc examples

        # FR FNCR/APN si están en pedido (no obligatorios salvo shipper francés)
        fr_fncr = order_data.get("fr_alpha_customer_reference")  # len 10
        fr_apn = order_data.get("fr_alpha_parcel_reference")  # len 18
        if fr_fncr:
            shipper["FRAlphaCustomerReference"] = fr_fncr
        if fr_apn:
            unit["FRAlphaParcelReference"] = fr_apn

        shipment: Dict[str, Any] = {
            "Product": product,
            "Consignee": {"Address": consignee_address},
            "Shipper": shipper,
            "ShipmentUnit": [unit],
            "Middleware": order_data.get("middleware") or "Mirakl-Orchestrator",
        }

        # Referencias de envío
        refs = []
        if order_data.get("order_id"):
            refs.append(str(order_data["order_id"]))
        if order_data.get("external_reference"):
            refs.append(str(order_data["external_reference"]))
        if refs:
            shipment["ShipmentReference"] = refs

        if incoterm:
            shipment["IncotermCode"] = incoterm

        # Fecha de envío opcional
        if order_data.get("shipping_date"):
            shipment["ShippingDate"] = str(order_data["shipping_date"])

        # Servicios a nivel envío si hay
        if services_shipment:
            shipment["Service"] = services_shipment

        # PrintingOptions (ReturnLabels requerido en hosting central)
        printing = {
            "ReturnLabels": {
                "TemplateSet": self.template_set,  # "NONE" para PDF
                "LabelFormat": self.label_format,  # "PDF" | "ZEBRA" | "PNG"
            }
        }

        # CustomContent opcional (logo/barcode)
        custom_content = None
        if order_data.get("label_logo_b64"):
            custom_content = {"CustomerLogo": order_data["label_logo_b64"]}
        if order_data.get("label_barcode"):
            custom_content = custom_content or {}
            custom_content["Barcode"] = order_data["label_barcode"]
            if order_data.get("label_barcode_type") in {"EAN_128", "CODE_39"}:
                custom_content["BarcodeType"] = order_data["label_barcode_type"]
        if order_data.get("hide_shipper_address"):
            custom_content = custom_content or {}
            custom_content["HideShipperAddress"] = "true"

        body: Dict[str, Any] = {"Shipment": shipment, "PrintingOptions": printing}
        if custom_content:
            body["CustomContent"] = custom_content
        return body
