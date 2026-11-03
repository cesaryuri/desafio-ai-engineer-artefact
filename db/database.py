import json
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

CSV_TABLES = {
    "categories": "desafio_tecnico_ai_eng - categories.csv",
    "customers": "desafio_tecnico_ai_eng - customers.csv",
    "orders": "desafio_tecnico_ai_eng - orders.csv",
    "order_items": "desafio_tecnico_ai_eng - order_items.csv",
    "products": "desafio_tecnico_ai_eng - products.csv",
    "promotions": "desafio_tecnico_ai_eng - promotions.csv",
}


def _clean_dataframe(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    if table_name == "products":
        df.loc[df["status"] == "discontinued", "stock_quantity"] = 0

        def parse_specs(raw):
            if not isinstance(raw, str):
                return {}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {}

        parsed = df["specs"].apply(parse_specs)
        df["strings"] = parsed.apply(lambda d: d.get("strings"))
        df["electronics"] = parsed.apply(lambda d: d.get("electronics"))
        df["color"] = parsed.apply(lambda d: d.get("color"))

    return df


def build_sqlite_db(data_dir: str = "data", db_path: str = "db/emporio_musica.db", views_path: str = "db/views.sql") -> str:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        for table_name, filename in CSV_TABLES.items():
            csv_path = os.path.join(data_dir, filename)
            df = pd.read_csv(csv_path)
            df = _clean_dataframe(table_name, df)
            df.to_sql(table_name, conn, if_exists="replace", index=False)

        if os.path.exists(views_path):
            with open(views_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

    return db_path


def get_db(db_url: str = None, data_dir: str = "data", db_path: str = "db/emporio_musica.db") -> SQLDatabase:
    if not os.path.exists(db_path):
        build_sqlite_db(data_dir=data_dir, db_path=db_path)

    uri = db_url or f"sqlite:///{db_path}"
    engine = create_engine(uri)
    if engine.dialect.name == "sqlite":
        engine.dialect.get_materialized_view_names = lambda connection, schema=None, **kw: []
    return SQLDatabase(engine, view_support=True)


if __name__ == "__main__":
    path = build_sqlite_db()
    print(f"Banco SQLite gerado em: {path}")
