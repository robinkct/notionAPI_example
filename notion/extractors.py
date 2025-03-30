from .config import NotionConfig
class PropertyValueExtractor:
    @staticmethod
    def extract_rollup_value(rollup_data: dict) -> any:
        """提取 rollup 屬性的值"""
        rollup_type = rollup_data.get('type')
        if not rollup_type:
            return None

        value = rollup_data.get(rollup_type)
        if not value:
            return None

        # 根據不同的 rollup 類型處理值
        if rollup_type in ['number', 'date']:
            return value
        elif rollup_type == 'array':
            # 處理數組類型的 rollup
            return [PropertyValueExtractor.extract_value(item) for item in value]
        elif rollup_type == 'unsupported':
            return None
        
        return value

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
            NotionConfig.PropertyType.RELATION: lambda x: [rel['id'] for rel in x['relation']],
            NotionConfig.PropertyType.ROLLUP: lambda x: PropertyValueExtractor.extract_rollup_value(x['rollup'])
        }

        extractor = extractors.get(prop_type)
        return extractor(property_data) if extractor else property_data[prop_type]
