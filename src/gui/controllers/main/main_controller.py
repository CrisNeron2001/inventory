class MainController:
    def __init__(self):
        self.user_inv_id: int | None = None
        self.current_cart_id: int | None = None
        self.cart: list[dict] = []
