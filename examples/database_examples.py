from notion.api import NotionAPI
def create_example_database(notion: NotionAPI, root_page_id: str) -> str:
    """創建示例數據庫"""
    initial_properties = {
        "Name": {"title": {}},
        "Description": {"rich_text": {}},
        "Priority": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "green"}
                ]
            }
        },
        "Tags": {
            "multi_select": {
                "options": [
                    {"name": "Work", "color": "blue"},
                    {"name": "Personal", "color": "green"},
                    {"name": "Urgent", "color": "red"}
                ]
            }
        },
        "Due Date": {"date": {}},
        "Complete": {"checkbox": {}},
        "Score": {"number": {}},
        "Website": {"url": {}},
        "Contact": {"email": {}},
        "Phone": {"phone_number": {}}
    }

    example_db = notion.create_database(
        parent_page_id=root_page_id,
        title="Example Database",
        properties=initial_properties
    )

    if not example_db:
        print("創建數據庫失敗")
        return None

    database_id = example_db["id"]
    print(f"創建的數據庫 ID: {database_id}")
    return database_id

def add_relation_property(notion: NotionAPI, database_id: str):
    """添加關聯屬性到數據庫"""
    relation_property = {
        "Related Tasks": {
            "relation": {
                "database_id": database_id,
                "single_property": {}
            }
        }
    }
    notion.update_database(database_id, properties=relation_property)

