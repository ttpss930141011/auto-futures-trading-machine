from src.interactor.dtos.show_futures_dtos import ShowFuturesOutputDto


class ShowFuturesView:
    """ View for displaying futures data
    """

    def show(self, output_dto: ShowFuturesOutputDto):
        """ Display futures data to the user
        """
        print(f"\n{output_dto.message}")
        
        if not output_dto.success or not output_dto.futures_data:
            return

        print("\n==== Futures Data ====")
        print(f"{'商品代號':^12}{'商品名稱':^15}{'標的物':^10}{'交割月份':^12}{'市場代碼':^10}{'部位價格':^12}{'到期日':^15}")
        print("-" * 80)
        
        for future in output_dto.futures_data:
            print(f"{future.commodity_id:^12}{future.product_name:^15}{future.underlying_id:^10}"
                  f"{future.delivery_month:^12}{future.market_code:^10}{future.position_price:^12}"
                  f"{future.expiration_date:^15}")
        
        print("-" * 80)
        print(f"Total items: {len(output_dto.futures_data)}\n") 