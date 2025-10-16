"""
GLS Tracking Poller Service.

Este servicio consulta periódicamente el estado de tracking de envíos GLS
y actualiza Mirakl cuando detecta cambios en el estado.

Como GLS ShipIT no ofrece webhooks nativos, implementamos polling activo.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from ..adapters.carriers.gls import GlsAdapter
from ..adapters.marketplaces.mirakl import MiraklAdapter
from ..core.unified_order_logger import unified_order_logger
from ..utils.csv_ops_logger import csv_ops_logger

logger = logging.getLogger(__name__)


class GlsTrackingPoller:
    """
    Servicio de polling para tracking de GLS.
    
    Consulta periódicamente el estado de envíos activos en GLS
    y actualiza Mirakl cuando hay cambios.
    """
    
    def __init__(
        self,
        gls_adapter: Optional[GlsAdapter] = None,
        mirakl_adapter: Optional[MiraklAdapter] = None,
        poll_interval_seconds: int = 300  # 5 minutos por defecto
    ):
        """
        Inicializa el poller.
        
        Args:
            gls_adapter: Adapter de GLS (si no se proporciona, se crea uno nuevo)
            mirakl_adapter: Adapter de Mirakl (si no se proporciona, se crea uno nuevo)
            poll_interval_seconds: Intervalo entre consultas en segundos
        """
        self.gls_adapter = gls_adapter or GlsAdapter()
        self.mirakl_adapter = mirakl_adapter or MiraklAdapter()
        self.poll_interval = poll_interval_seconds
        self.running = False
        self._task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Inicia el poller en background."""
        if self.running:
            logger.warning("GLS tracking poller already running")
            return
            
        self.running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(f"GLS tracking poller started (interval: {self.poll_interval}s)")
        
    async def stop(self):
        """Detiene el poller."""
        if not self.running:
            return
            
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("GLS tracking poller stopped")
        
    async def _poll_loop(self):
        """Loop principal de polling."""
        while self.running:
            try:
                await self._poll_tracking_updates()
            except Exception as e:
                logger.error(f"Error in GLS tracking poll: {e}", exc_info=True)
                
            # Esperar hasta el próximo ciclo
            await asyncio.sleep(self.poll_interval)
            
    async def _poll_tracking_updates(self):
        """
        Consulta tracking de envíos GLS activos y actualiza Mirakl si hay cambios.
        """
        logger.info("Starting GLS tracking poll cycle")
        
        # Obtener envíos activos de GLS desde unified_order_logger
        # Estados que necesitan seguimiento: CARRIER_OK, AWAITING_TRACKING
        active_orders = unified_order_logger.get_orders_by_carrier("gls")
        
        if not active_orders:
            logger.debug("No active GLS orders to track")
            return
            
        logger.info(f"Polling tracking for {len(active_orders)} GLS orders")
        
        updates_count = 0
        errors_count = 0
        
        for order in active_orders:
            try:
                # Solo procesar órdenes que tengan tracking number
                tracking_number = order.get("tracking_number")
                if not tracking_number:
                    continue
                    
                # Consultar estado actual en GLS
                current_status = await self.gls_adapter.get_shipment_status(tracking_number)
                
                # Verificar si hay cambios respecto al último estado conocido
                last_status = order.get("carrier_status")
                new_status = current_status.get("status")
                
                if new_status != last_status:
                    # Hay un cambio de estado, actualizar Mirakl
                    logger.info(
                        f"Status change detected for order {order.get('mirakl_order_id')}: "
                        f"{last_status} -> {new_status}"
                    )
                    
                    # Actualizar tracking en Mirakl si corresponde
                    await self._update_mirakl_tracking(order, current_status)
                    
                    # Actualizar en unified logger
                    unified_order_logger.upsert_order(
                        order.get("mirakl_order_id"),
                        {
                            "carrier_status": new_status,
                            "last_event": f"GLS_STATUS_UPDATE:{new_status}",
                            "last_event_at": datetime.utcnow().isoformat(),
                            "tracking_events": current_status.get("events", [])
                        }
                    )
                    
                    updates_count += 1
                    
            except Exception as e:
                logger.error(
                    f"Error polling tracking for order {order.get('mirakl_order_id')}: {e}",
                    exc_info=True
                )
                errors_count += 1
                continue
                
        logger.info(
            f"GLS tracking poll completed: {updates_count} updates, {errors_count} errors"
        )
        
        # Log operation summary
        await csv_ops_logger.log(
            scope="gls_poller",
            action="poll_tracking",
            carrier="gls",
            status="OK" if errors_count == 0 else "PARTIAL",
            message=f"Polled {len(active_orders)} orders, {updates_count} updates, {errors_count} errors",
            meta={
                "orders_polled": len(active_orders),
                "updates": updates_count,
                "errors": errors_count
            }
        )
        
    async def _update_mirakl_tracking(self, order: Dict[str, Any], tracking_data: Dict[str, Any]):
        """
        Actualiza información de tracking en Mirakl.
        
        Args:
            order: Datos de la orden desde unified_order_logger
            tracking_data: Datos de tracking desde GLS
        """
        order_id = order.get("mirakl_order_id")
        tracking_number = order.get("tracking_number")
        carrier_code = order.get("carrier_code", "gls")
        
        if not order_id or not tracking_number:
            logger.warning(f"Missing order_id or tracking_number for order: {order}")
            return
            
        try:
            # Actualizar tracking (OR23)
            result = await self.mirakl_adapter.update_order_tracking(
                order_id=order_id,
                tracking_number=tracking_number,
                carrier_code=carrier_code,
                carrier_name="GLS",
                validate_shipment=False  # Ya fue validado al crear el envío
            )
            
            logger.info(f"Updated Mirakl tracking for order {order_id}: {result}")
            
            # Si el estado es DELIVERED, podríamos marcar como shipped en Mirakl
            # (aunque normalmente OR24 se hace al crear el envío, no al entregar)
            status = tracking_data.get("status")
            if status == "DELIVERED" and order.get("internal_state") != "DELIVERED":
                # Actualizar estado interno
                unified_order_logger.upsert_order(
                    order_id,
                    {
                        "internal_state": "DELIVERED",
                        "last_event": "GLS_DELIVERED",
                        "last_event_at": datetime.utcnow().isoformat(),
                        "delivery_date": tracking_data.get("delivery_date")
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to update Mirakl tracking for order {order_id}: {e}", exc_info=True)
            raise
            
    async def poll_once(self) -> Dict[str, Any]:
        """
        Ejecuta un ciclo de polling una vez (útil para testing o ejecución manual).
        
        Returns:
            Resumen del polling
        """
        await self._poll_tracking_updates()
        return {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def poll_specific_order(self, order_id: str) -> Dict[str, Any]:
        """
        Consulta tracking de una orden específica y actualiza Mirakl.
        
        Args:
            order_id: ID de la orden en Mirakl
            
        Returns:
            Resultado del polling
        """
        # Buscar orden en unified logger
        order = unified_order_logger.get_order_by_id(order_id)
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
            
        tracking_number = order.get("tracking_number")
        if not tracking_number:
            raise ValueError(f"Order {order_id} has no tracking number")
            
        # Consultar estado en GLS
        tracking_data = await self.gls_adapter.get_shipment_status(tracking_number)
        
        # Actualizar Mirakl
        await self._update_mirakl_tracking(order, tracking_data)
        
        return {
            "order_id": order_id,
            "tracking_number": tracking_number,
            "status": tracking_data.get("status"),
            "updated_at": datetime.utcnow().isoformat()
        }


# Instancia global del poller (se puede iniciar desde main.py)
gls_tracking_poller = GlsTrackingPoller()

