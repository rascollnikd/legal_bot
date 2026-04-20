import requests
from bs4 import BeautifulSoup
import time
import json
from google import genai

# === ВАШ КЛЮЧ GEMINI ===
GEMINI_KEY = "AIzaSyCjdUlJI6fUJ9n8LTEdYaYq6NkWIgEqrCE"

# === НОВАЯ ИНИЦИАЛИЗАЦИЯ (без configure) ===
client = genai.Client(api_key=GEMINI_KEY)

class MultiCourtSearcher:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def _get_ai_description(self, number, title):
        """Получить фабулу и решение от Gemini (новая версия SDK)"""
        if not GEMINI_KEY:
            return "", ""
        try:
            prompt = f"""
Ты юрист. Верни ТОЛЬКО JSON (без пояснений):
{{"fabula": "суть спора (до 10 слов)", "decision": "решение (до 8 слов)"}}

Дело: {number}
Название: {title}
"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            data = json.loads(text)
            return data.get('fabula', ''), data.get('decision', '')
        except Exception as e:
            print(f"Ошибка ИИ: {e}")
            return "", ""

    def search_all(self, query):
        results = []
        try:
            url = f"https://kad.arbitr.ru/Kad/SearchInstances?query={query}"
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for block in soup.find_all('div', class_='instance-card')[:3]:
                number = block.find('div', class_='case-number')
                title = block.find('div', class_='case-title')
                link = block.find('a', href=True)
                
                case_number = number.text.strip() if number else "—"
                case_title = title.text.strip()[:150] if title else "—"
                
                if link:
                    href = link.get('href')
                    case_link = "https://kad.arbitr.ru" + href if href.startswith('/') else href
                else:
                    case_link = None
                
                # Получаем ИИ-описание
                fabula, decision = self._get_ai_description(case_number, case_title)
                
                results.append({
                    'number': case_number,
                    'title': case_title,
                    'link': case_link,
                    'fabula': fabula,
                    'decision': decision
                })
                time.sleep(1)
        except Exception as e:
            print(f"Ошибка поиска: {e}")
        
        return results
