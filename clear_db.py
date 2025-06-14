from app import db, Item, Category, ItemOption

def clear_all():
    db.session.query(ItemOption).delete()
    db.session.query(Item).delete()
    db.session.query(Category).delete()
    db.session.commit()
    print("資料已清空")

if __name__ == "__main__":
    clear_all()
