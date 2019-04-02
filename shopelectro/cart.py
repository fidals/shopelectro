from ecommerce.cart import Cart


class SECart(Cart):
    """Override Cart class for Wholesale features."""

    def get_position_data(self, position):
        """Add vendor_code to cart's positions data."""
        return {
            **super().get_position_data(position),
            'vendor_code': position.vendor_code,
            'purchase_price': position.purchase_price,
        }

    def total_revenue(self):
        return sum(
            (position['price'] - position['purchase_price']) * position['quantity']
            for _, position in self
        )
