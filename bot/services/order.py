from database.connection import get_connection

async def get_order_by_number(order_number: str):
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            """
            SELECT order_number,
                   product_name,
                   size,
                   total_price,
                   status,
                   customer_tg_id
            FROM orders
            WHERE order_number = $1
            """,
            order_number
        )
        return row
    finally:
        await conn.close()
