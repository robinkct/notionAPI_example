from notion.api import NotionAPI
from examples.database_examples import create_example_database, add_relation_property
from examples.page_examples import create_example_pages, create_page_relation
from notion.builders import BlockBuilder
import json
from notion.config import NotionConfig

def demo_filters(notion: NotionAPI, database_id: str, page_ids: list):
    """展示各種過濾器的使用"""
    filter_examples = {
        "標題過濾": {
            "property": "Name",
            "title": {"contains": "Task"}
        },
        "選擇過濾": {
            "property": "Priority",
            "select": {"equals": "High"}
        },
        "數字過濾": {
            "property": "Score",
            "number": {"greater_than": 80}
        },
        "關聯過濾": {
            "property": "Related Tasks",
            "relation": {"contains": page_ids[0] if page_ids else ""}
        }
    }

    print("\n=== 過濾器示例 ===")
    for filter_name, filter_params in filter_examples.items():
        print(f"\n正在執行 {filter_name}:")
        results = notion.query_database(
            database_id=database_id,
            filter_params=filter_params
        )
        print(f"查詢結果: {json.dumps(results, indent=2, ensure_ascii=False)}")

def demo_sorting(notion: NotionAPI, database_id: str):
    """展示排序功能"""
    sort_params = [{"property": "Score", "direction": "descending"}]
    print("\n=== 排序示例 ===")
    results = notion.query_database(
        database_id=database_id,
        sort_params=sort_params
    )
    return results

def demo_property_extraction(notion: NotionAPI, results: dict):
    """展示屬性提取功能"""
    print("\n=== 格式化屬性值示例 ===")
    for page_result in results.get("results", []):
        page_id = page_result["id"]
        formatted_props = notion.get_formatted_page_properties(page_id)
        print(f"\n頁面屬性值:")
        for prop_name, value in formatted_props.items():
            print(f"{prop_name}: {value}")

    specific_props = ["Name", "Score", "Priority", "Tags", "Related Tasks"]
    print("\n=== 特定屬性值示例（包含關聯）===")
    for page_result in results.get("results", []):
        page_id = page_result["id"]
        formatted_props = notion.get_formatted_page_properties(page_id, specific_props)
        print(f"\n頁面特定屬性值:")
        for prop_name, value in formatted_props.items():
            print(f"{prop_name}: {value}")

def demo_image_operations(notion: NotionAPI, page_id: str):
    # 創建 BlockBuilder 實例
    builder = BlockBuilder(imgur_client_id=NotionConfig.IMGUR_CLIENT_ID)
    
    blocks = [
        BlockBuilder.text_block("以下是一些圖片："),
        builder.image_block(
            "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
            caption="透過「外部 url」新增的圖片"
        ),
        BlockBuilder.text_block("再新增一張"),
        builder.image_block(
            "1.png",
            caption="透過「本地上傳」新增的圖片（先將照片傳到 imgur 再以 url 新增到 notion）"
        )
    ]
    
    notion.append_blocks(page_id, blocks)

def main():
    root_page_id = '1c6db9568fde8068bc49d3184604370f' # https://www.notion.so/1c6db9568fde8068bc49d3184604370f
    token = NotionConfig.NOTION_TOKEN
    notion = NotionAPI(token)

    # 執行示例
    database_id = create_example_database(notion, root_page_id)
    if database_id:
        add_relation_property(notion, database_id)
        created_pages = create_example_pages(notion, database_id)
        create_page_relation(notion, database_id, created_pages)
        demo_filters(notion, database_id, created_pages)
        results = demo_sorting(notion, database_id)
        demo_property_extraction(notion, results)

    demo_image_operations(notion, root_page_id)

if __name__ == "__main__":
    main() 