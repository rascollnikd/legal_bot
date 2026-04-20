import requests
from bs4 import BeautifulSoup
import time
import json
import os
from google import genai

# === ВАШ КЛЮЧ GEMINI  ===
GEMINI_KEY = "AIzaSyCjdUlJI6fUJ9n8LTEdYaYq6NkWIgEqrCE"

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

class MultiCourtSearcher:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        self.sites = [
            {
                'name': 'kad.arbitr.ru',
                'url': 'https://kad.arbitr.ru/Kad/SearchInstances?query={query}',
                'parser': self._parse_kad
            }
        ]

    def _get_ai_description(self, number, title):
        if not GEMINI_KEY:
            return "", ""
        try:
            prompt = f"""
Ты юрист. Верни ТОЛЬКО JSON (без пояснений):
{{"fabula": "суть спора (до 10 слов)", "decision": "решение (до 8 слов)"}}

Дело: {number}
Название: {title}
"""
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            data = json.loads(text)
            return data.get('fabula', ''), data.get('decision', '')
        except:
            return "", ""

    def search_all(self, query):
        all_results = []
        for site in self.sites:
            try:
                url = site['url'].format(query=query)
                response = requests.get(url, headers=self.headers, timeout=15)
                results = site['parser'](response.text)
                for r in results[:3]:
                    r['source'] = site['name']
                    fabula, decision = self._get_ai_description(r['number'], r['title'])
                    r['fabula'] = fabula
                    r['decision'] = decision
                    all_results.append(r)
                time.sleep(2)
            except Exception as e:
                print(f"Ошибка: {e}")
        return all_results

    def _parse_kad(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for block in soup.find_all('div', class_='instance-card')[:3]:
            number = block.find('div', class_='case-number')
            title = block.find('div', class_='case-title')
            link = block.find('a', href=True)
            if link:
                href = link.get('href')
                case_link = "https://kad.arbitr.ru" + href if href.startswith('/') else href
            else:
                case_link = None
            results.append({
                'number': number.text.strip() if number else "—",
                'title': title.text.strip()[:150] if title else "—",
                'link': case_link,
                'fabula': "",
                'decision': ""
            })
        return results
