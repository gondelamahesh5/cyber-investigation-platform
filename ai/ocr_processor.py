import os
from PIL import Image
import pytesseract


class OCRProcessor:
    def __init__(self):
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif'}

    def process_image(self, file_path, language='eng'):
        if not file_path or not os.path.exists(file_path):
            return self._empty_result()

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_formats:
            return self._empty_result()

        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image, lang=language)
            confidence = self._calculate_confidence(image, language)

            return {
                'extracted_text': extracted_text.strip(),
                'confidence_score': confidence,
                'language': language,
                'page_count': 1,
                'status': 'processed'
            }
        except Exception as e:
            return {
                'extracted_text': '',
                'confidence_score': 0.0,
                'language': language,
                'page_count': 0,
                'status': f'error: {str(e)}'
            }

    def _calculate_confidence(self, image, language):
        try:
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            if confidences:
                return round(sum(confidences) / len(confidences), 2)
        except Exception:
            pass
        return 0.0

    def _empty_result(self):
        return {
            'extracted_text': '',
            'confidence_score': 0.0,
            'language': 'eng',
            'page_count': 0,
            'status': 'no image provided'
        }