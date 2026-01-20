from prometheus_client import Counter

orders_created_total = Counter(
    "orders_created_total",
    "Total number of created orders"
)

orders_items_total = Counter(
    "orders_items_total",
    "Total number of items in all created orders"
)

orders_total_amount_sum = Counter(
    "orders_total_amount_sum",
    "Total value of all created orders"
)