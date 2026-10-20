from sqlalchemy import inspect, text

from app.database import engine


def migrate():
    columns = {
        column["name"]
        for column in inspect(engine).get_columns("transactions")
    }

    with engine.begin() as connection:
        if "idempotency_key" not in columns:
            connection.execute(text(
                "ALTER TABLE transactions "
                "ADD COLUMN idempotency_key VARCHAR(255)"
            ))

        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS "
            "uq_transactions_idempotency_key "
            "ON transactions (idempotency_key)"
        ))

    print("Idempotency migration completed.")


if __name__ == "__main__":
    migrate()