from .config import NotionConfig
class PropertyValueExtractor:
    @staticmethod
    def extract_value(property_data: dict) -> any:
        """統一的屬性值提取方法"""
        prop_type = property_data.get('type')
        if not prop_type:
            return None

        extractors = {
            NotionConfig.PropertyType.TITLE: lambda x: x['title'][0]['text']['content'] if x['title'] else '',
            NotionConfig.PropertyType.RICH_TEXT: lambda x: x['rich_text'][0]['text']['content'] if x['rich_text'] else '',
            NotionConfig.PropertyType.NUMBER: lambda x: x['number'],
            NotionConfig.PropertyType.SELECT: lambda x: x['select']['name'] if x['select'] else '',
            NotionConfig.PropertyType.MULTI_SELECT: lambda x: [option['name'] for option in x['multi_select']],
            NotionConfig.PropertyType.DATE: lambda x: x['date']['start'] if x['date'] else '',
            NotionConfig.PropertyType.CHECKBOX: lambda x: x['checkbox'],
            NotionConfig.PropertyType.URL: lambda x: x['url'],
            NotionConfig.PropertyType.EMAIL: lambda x: x['email'],
            NotionConfig.PropertyType.PHONE: lambda x: x['phone_number'],
            NotionConfig.PropertyType.RELATION: lambda x: [rel['id'] for rel in x['relation']]
        }

        extractor = extractors.get(prop_type)
        return extractor(property_data) if extractor else property_data[prop_type]
