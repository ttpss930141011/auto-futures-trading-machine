"""
Infrastructure repository using the PFCF COM client to fetch positions.
"""

import threading
from typing import List

from src.interactor.dtos.get_position_dtos import PositionDto
from src.interactor.interfaces.repositories.position_repository_interface import (
    PositionRepositoryInterface,
)
from src.infrastructure.pfcf_client.api import PFCFApi


class PFCFPositionRepository(PositionRepositoryInterface):
    """Wraps PFCF COM callbacks into a blocking call."""

    def __init__(self, client: PFCFApi, timeout_sec: float = 5.0):
        """
        Args:
            client: The PFCF API client instance.
            timeout_sec: Maximum seconds to wait for callbacks.
        """
        self._client = client
        self._timeout = timeout_sec

    def get_positions(self, order_account: str, product_id: str = "") -> List[PositionDto]:
        """
        Fetch positions synchronously by registering callback handlers.

        Raises:
            TimeoutError: If callbacks do not complete in time.
            RuntimeError: If the client signals an error.
        """
        event = threading.Event()
        results: List[PositionDto] = []
        expected = 0
        error_occurred = False
        error_message = ""

        def on_data(
            count,
            recordno,
            investorAcno,
            ProductId,
            productKind,
            OTQtyB,
            OTQtyS,
            NowOrderQtyB,
            NowOrderQtyS,
            NowMatchQtyB,
            NowMatchQtyS,
            TodayEnd,
            NowOTQtyB,
            NowOTQtyS,
            RealPrice,
            AvgCostB,
            AvgCostS,
            PriceDiffB,
            PriceDiffS,
            PricePL,
            Curren,
            LiquidationPL,
        ):
            print(
                f"on_data: {count}, {recordno}, {investorAcno}, {ProductId}, {productKind}, {OTQtyB}, {OTQtyS}, {NowOrderQtyB}, {NowOrderQtyS}, {NowMatchQtyB}, {NowMatchQtyS}, {TodayEnd}, {NowOTQtyB}, {NowOTQtyS}, {RealPrice}, {AvgCostB}, {AvgCostS}, {PriceDiffB}, {PriceDiffS}, {PricePL}, {Curren}, {LiquidationPL}"
            )
            nonlocal expected, error_occurred, error_message
            try:
                expected = int(count)

                # Handle no data case
                if expected == 0:
                    print("No position data")
                    event.set()
                    return

                # Validate required fields
                if not investorAcno or not ProductId:
                    print(f"Invalid data record (第{recordno}筆)")
                    return

                # Create DTO, handle errors
                dto = PositionDto(
                    investor_account=investorAcno or "",
                    product_id=ProductId or "",
                    product_kind=int(productKind) if productKind and productKind.strip() else None,
                    yesterday_long=int(OTQtyB) if OTQtyB and OTQtyB.strip() else None,
                    yesterday_short=int(OTQtyS) if OTQtyS and OTQtyS.strip() else None,
                    today_order_long=(
                        int(NowOrderQtyB) if NowOrderQtyB and NowOrderQtyB.strip() else None
                    ),
                    today_order_short=(
                        int(NowOrderQtyS) if NowOrderQtyS and NowOrderQtyS.strip() else None
                    ),
                    today_filled_long=(
                        int(NowMatchQtyB) if NowMatchQtyB and NowMatchQtyB.strip() else None
                    ),
                    today_filled_short=(
                        int(NowMatchQtyS) if NowMatchQtyS and NowMatchQtyS.strip() else None
                    ),
                    today_closed=int(TodayEnd) if TodayEnd and TodayEnd.strip() else None,
                    current_long=int(NowOTQtyB) if NowOTQtyB and NowOTQtyB.strip() else None,
                    current_short=int(NowOTQtyS) if NowOTQtyS and NowOTQtyS.strip() else None,
                    reference_price=float(RealPrice) if RealPrice and RealPrice.strip() else None,
                    avg_cost_long=float(AvgCostB) if AvgCostB and AvgCostB.strip() else None,
                    avg_cost_short=float(AvgCostS) if AvgCostS and AvgCostS.strip() else None,
                    unrealized_pl=float(PricePL) if PricePL and PricePL.strip() else None,
                    currency=Curren.strip() if Curren else None,
                    realized_pl=(
                        float(LiquidationPL) if LiquidationPL and LiquidationPL.strip() else None
                    ),
                )
                results.append(dto)

                # Check if all data is collected
                if len(results) >= expected:
                    event.set()

            except (ValueError, TypeError) as e:
                error_occurred = True
                error_message = f"Data conversion error (第{recordno}筆): {str(e)}"
                print(error_message)
                event.set()

        def on_error(error_code, message):
            nonlocal error_occurred, error_message
            error_occurred = True
            error_message = f"PFCF OnPositionError {error_code}: {message}"
            print(error_message)
            event.set()

        # Register callback functions
        self._client.DAccountLib.OnPositionData += on_data
        self._client.DAccountLib.OnPositionError += on_error

        try:
            # Send request
            print(f"GetPosition: {order_account}, {product_id}")
            self._client.DAccountLib.GetPosition(order_account, product_id)

            # Wait for callbacks to complete
            if not event.wait(timeout=self._timeout):
                raise TimeoutError("Timed out waiting for position data")

            # Check if an error occurred
            if error_occurred:
                raise RuntimeError(error_message)

            return results

        finally:
            # Ensure callback functions are removed
            self._client.DAccountLib.OnPositionData -= on_data
            self._client.DAccountLib.OnPositionError -= on_error
