from modules.database import db


def get_lore() -> str:
    row = db.fetchone("SELECT content FROM lore WHERE id = 1")
    return row["content"] if row else ""


def save_lore(content: str) -> None:
    db.execute(
        "UPDATE lore SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
        (content,),
        commit=True,
    )
