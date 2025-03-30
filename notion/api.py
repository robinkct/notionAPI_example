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
                      page_size: int = 100) -> dict:
        """改進的數據庫查詢方法
        
        Args:
            database_id: 數據庫ID
            filter_params: 格式應為 {"property": "屬性名", "屬性類型": {"條件": "值"}}
            sort_params: 排序參數
            page_size: 每頁數量
        """
        url = f"{NotionConfig.BASE_URL}/databases/{database_id}/query"
        query_data = {}
        
        # 驗證和格式化 filter_params
        if filter_params:
            if isinstance(filter_params, dict):
                if "property" in filter_params and len(filter_params) > 1:
                    # filter_params 已經是正確格式
                    query_data["filter"] = filter_params
                else:
                    # 需要轉換成正確格式
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

        return self._make_request("POST", url, query_data)

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

    def get_formatted_page_properties(self, page_id: str, property_list: list = None) -> dict:
        """獲取格式化後的頁面屬性值"""
        raw_properties = self.get_page_properties(page_id, property_list)
        formatted_properties = {}
        
        for prop_name, prop_data in raw_properties.items():
            formatted_properties[prop_name] = PropertyValueExtractor.extract_value(prop_data)
            
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