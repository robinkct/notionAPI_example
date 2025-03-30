from notion.api import NotionAPI
import json

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

def demonstrate_database_properties(notion: NotionAPI, database_id: str):
    """展示如何獲取和使用數據庫屬性"""
    # 獲取所有屬性
    properties = notion.get_database_properties(database_id)
    
    print("\n=== 數據庫屬性 ===")
    print("\n可用的過濾屬性：")
    for prop_name, prop_type in properties.items():
        print(f"- {prop_name}: {prop_type}")
    
    # 展示如何為每種類型創建過濾器
    print("\n各類型的過濾器示例：")
    filter_examples = {}
    
    for prop_name, prop_type in properties.items():
        if prop_type == "title":
            filter_examples[prop_name] = {
                "property": prop_name,
                "title": {"contains": "任務"}
            }
        elif prop_type == "select":
            filter_examples[prop_name] = {
                "property": prop_name,
                "select": {"equals": "High"}
            }
        elif prop_type == "multi_select":
            filter_examples[prop_name] = {
                "property": prop_name,
                "multi_select": {"contains": "工作"}
            }
        elif prop_type == "number":
            filter_examples[prop_name] = {
                "property": prop_name,
                "number": {"greater_than": 50}
            }
        elif prop_type == "checkbox":
            filter_examples[prop_name] = {
                "property": prop_name,
                "checkbox": {"equals": True}
            }
        elif prop_type == "date":
            filter_examples[prop_name] = {
                "property": prop_name,
                "date": {"past_week": {}}
            }
        elif prop_type == "relation":
            filter_examples[prop_name] = {
                "property": prop_name,
                "relation": {"contains": "page_id"}
            }
    
    print("\n過濾器示例：")
    print(json.dumps(filter_examples, indent=2, ensure_ascii=False))

