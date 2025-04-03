from .handlers import NotionRequestHandler
from .builders import BlockBuilder
from .config import NotionConfig
from .extractors import PropertyValueExtractor
import requests
from base64 import b64encode


class NotionAPI(NotionRequestHandler):
    def __init__(self, token: str):
        super().__init__(token)
        self.imgur_client_id = NotionConfig.IMGUR_CLIENT_ID
        self.block_builder = BlockBuilder()

    def query_database(self, database_id: str, 
                      filter_params: dict = None,
                      sort_params: list = None,
                      page_size: int = 100,
                      start_cursor: str = None) -> dict:
        """改進的數據庫查詢方法，支援分頁
        
        Args:
            database_id: 數據庫ID
            filter_params: 格式應為 {"property": "屬性名", "屬性類型": {"條件": "值"}}
            sort_params: 排序參數
            page_size: 每頁數量
            start_cursor: 分頁游標
        """
        url = f"{NotionConfig.BASE_URL}/databases/{database_id}/query"
        query_data = {}
        
        # 驗證和格式化 filter_params
        if filter_params:
            if isinstance(filter_params, dict):
                if "property" in filter_params and len(filter_params) > 1:
                    query_data["filter"] = filter_params
                else:
                    for prop_name, value in filter_params.items():
                        query_data["filter"] = {
                            "property": prop_name,
                            "select": {
                                "equals": value
                            }
                        }
        
        if sort_params:
            query_data["sorts"] = sort_params
        if page_size:
            query_data["page_size"] = page_size
        if start_cursor:
            query_data["start_cursor"] = start_cursor

        return self._make_request("POST", url, query_data)

    def query_database_all(self, database_id: str,
                          filter_params: dict = None,
                          sort_params: list = None,
                          page_size: int = 100) -> list:
        """獲取數據庫中的所有記錄
        
        Args:
            database_id: 數據庫ID
            filter_params: 過濾參數
            sort_params: 排序參數
            page_size: 每頁數量
            
        Returns:
            list: 所有查詢結果的列表
        """
        all_results = []
        has_more = True
        next_cursor = None
        
        while has_more:
            response = self.query_database(
                database_id=database_id,
                filter_params=filter_params,
                sort_params=sort_params,
                page_size=page_size,
                start_cursor=next_cursor
            )
            
            if not response:
                break
            
            results = response.get('results', [])
            all_results.extend(results)
            
            has_more = response.get('has_more', False)
            next_cursor = response.get('next_cursor')
            
            if has_more:
                print(f"已獲取 {len(all_results)} 條記錄，繼續查詢...")
        
        print(f"總共獲取 {len(all_results)} 條記錄")
        return all_results

    def get_page_properties(self, page_id: str, property_list: list = None) -> dict:
        """獲取頁面屬性，支持選擇性獲取"""
        url = f"{NotionConfig.BASE_URL}/pages/{page_id}"
        response = self._make_request("GET", url)
        
        if not response:
            return {}
            
        if not property_list:
            return response.get("properties", {})
            
        return {
            prop: response.get("properties", {}).get(prop)
            for prop in property_list
            if prop in response.get("properties", {})
        }

    def get_block_children(self, block_id: str, 
                          start_cursor: str = None,
                          page_size: int = 100) -> list:
        """改進的獲取區塊內容方法"""
        url = f"{NotionConfig.BASE_URL}/blocks/{block_id}/children"
        params = {"page_size": page_size}
        
        if start_cursor:
            params["start_cursor"] = start_cursor
            
        return self._make_request("GET", url)

    def create_page(self, database_id: str,
                   properties: dict,
                   children: list = None) -> dict:
        """創建新頁面的改進方法"""
        url = f"{NotionConfig.BASE_URL}/pages"
        data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        if children:
            data["children"] = children
            
        return self._make_request("POST", url, data)

    def update_block(self, block_id: str, block_data: dict) -> dict:
        """更新區塊內容"""
        url = f"{NotionConfig.BASE_URL}/blocks/{block_id}"
        return self._make_request("PATCH", url, block_data)

    def create_database(self, parent_page_id: str, title: str, properties: dict) -> dict:
        """創建新數據庫"""
        url = f"{NotionConfig.BASE_URL}/databases"
        data = {
            "parent": {"page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": properties
        }
        return self._make_request("POST", url, data)

    def get_formatted_page_properties(self, page_id: str, property_list: list = None, raw_page_data: dict = None) -> dict:
        """獲取格式化後的頁面屬性值
        
        Args:
            page_id: 頁面ID
            property_list: 指定要獲取的屬性列表
            raw_page_data: 頁面完整數據（如果有的話，避免重複請求）
        """
        if raw_page_data:
            raw_properties = raw_page_data.get("properties", {})
            if property_list:
                raw_properties = {
                    prop: raw_properties.get(prop)
                    for prop in property_list
                    if prop in raw_properties
                }
        else:
            raw_properties = self.get_page_properties(page_id, property_list)
        
        formatted_properties = {}
        
        for prop_name, prop_data in raw_properties.items():
            value = PropertyValueExtractor.extract_value(prop_data)
            
            # 特殊處理 relation 類型，只保留第一個關聯的 ID
            if isinstance(value, list) and prop_data.get('type') == 'relation':
                value = value[0] if value else None
            
            formatted_properties[prop_name] = value
        
        return formatted_properties

    def update_database(self, database_id: str, properties: dict = None, title: str = None) -> dict:
        """更新數據庫屬性或標題"""
        url = f"{NotionConfig.BASE_URL}/databases/{database_id}"
        data = {}
        
        if properties:
            data["properties"] = properties
        if title:
            data["title"] = [{"type": "text", "text": {"content": title}}]
            
        return self._make_request("PATCH", url, data)

    def append_blocks(self, page_id: str, blocks: list) -> dict:
        """向頁面添加多個區塊"""
        url = f"{NotionConfig.BASE_URL}/blocks/{page_id}/children"
        data = {
            "children": blocks
        }
        return self._make_request("PATCH", url, data)

    def add_image_to_page(self, page_id: str, image_url: str, caption: str = None, local_image_path: str = None) -> dict:
        """向頁面添加圖片
        
        Args:
            page_id: 頁面ID
            image_url: 圖片URL
            caption: 圖片說明文字（可選）
            local_image_path: 本地圖片路徑（可選）
        """
        if local_image_path:
            image_url = self.upload_to_imgur(local_image_path)

        image_block = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": image_url
                }
            }
        }
        
        if caption:
            image_block["image"]["caption"] = [
                {
                    "type": "text",
                    "text": {
                        "content": caption
                    }
                }
            ]
            
        return self.append_blocks(page_id, [image_block])

    def upload_to_imgur(self, image_path):
        """上传图片到 Imgur 并返回链接"""
        headers = {
            'Authorization': f'Client-ID {self.imgur_client_id}'
        }
        
        with open(image_path, 'rb') as image_file:
            image_data = b64encode(image_file.read())
        
        response = requests.post(
            'https://api.imgur.com/3/image',
            headers=headers,
            data={
                'image': image_data
            }
        )
        
        if response.status_code == 200:
            return response.json()['data']['link']
        else:
            raise Exception(f"Imgur 上传失败: {response.text}")

    def get_database_properties(self, database_id: str) -> dict:
        """獲取數據庫所有可過濾的屬性信息
        
        Args:
            database_id: 數據庫 ID
            
        Returns:
            dict: 屬性名稱及其類型的映射，例如：
            {
                "Name": "title",
                "Priority": "select",
                "Tags": "multi_select",
                "Score": "number",
                ...
            }
        """
        url = f"{NotionConfig.BASE_URL}/databases/{database_id}"
        response = self._make_request("GET", url)
        
        if not response or 'properties' not in response:
            return {}
        
        properties = {}
        for prop_name, prop_info in response['properties'].items():
            prop_type = prop_info.get('type')
            properties[prop_name] = prop_type
        
        return properties

    def get_database_select_options(self, database_id: str) -> dict:
        """獲取數據庫中所有 select 和 multi_select 類型屬性的選項信息
        
        Args:
            database_id: 數據庫 ID
            
        Returns:
            dict: 屬性名稱及其選項信息的映射，例如：
            {
                "屬性": {
                    "options": [
                        {
                            "name": "必要花費",
                            "color": "blue",
                            "id": "xxx"
                        },
                        ...
                    ]
                },
                "類別": {
                    "options": [
                        {
                            "name": "食",
                            "color": "green",
                            "id": "xxx"
                        },
                        ...
                    ]
                }
            }
        """
        url = f"{NotionConfig.BASE_URL}/databases/{database_id}"
        response = self._make_request("GET", url)
        
        if not response or 'properties' not in response:
            return {}
        
        select_options = {}
        for prop_name, prop_info in response['properties'].items():
            prop_type = prop_info.get('type')
            
            if prop_type in ['select', 'multi_select']:
                options = prop_info.get(prop_type, {}).get('options', [])
                if options:
                    select_options[prop_name] = {
                        "type": prop_type,
                        "options": [
                            {
                                "name": option['name'],
                                "color": option['color'],
                                "id": option['id']
                            }
                            for option in options
                        ]
                    }
        
        return select_options