import requests
from bs4 import BeautifulSoup
import time
import json
import os
import google.generativeai as genai

# Инициализация ИИ (ключ из переменных окружения)
GEMINI_KEY = os.environ.get("AIzaSyCjdUlJI6fUJ9n8LTEdYaYq6NkWIgEqrCE")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

class MultiCourtSearcher:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # Список сайтов для поиска
        self.sites = [
            {
                'name': 'kad.arbitr.ru',
                'url': 'https://kad.arbitr.ru/Kad/SearchInstances?query={query}',
                'parser': self._parse_kad
            },
            {
                'name': 'sudrf.ru',
                'url': 'https://sudrf.ru/search.php?search={query}',
                'parser': self._parse_sudrf
            },
            {
                'name': 'sudact.ru',
                'url': 'https://sudact.ru/search/?page=1&query={query}&source=all',
                'parser': self._parse_sudact
            }
        ]

    def _get_ai_description(self, number, title):
        """Получить фабулу и решение от Gemini"""
        if not GEMINI_KEY:
            return "", ""
        try:
            prompt = f"""
Ты юрист. Проанализируй дело:
Номер: {number}
Название: {title}

Верни ТОЛЬКО JSON (без пояснений):
{{"fabula": "суть спора одним предложением (до 10 слов)", "decision": "решение суда кратко (до 8 слов)"}}

Пример:
{{"fabula": "Арендатор не платил 6 месяцев", "decision": "Суд расторг договор"}}
"""
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Убираем markdown-обёртку
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            data = json.loads(text)
            return data.get('fabula', ''), data.get('decision', '')
        except Exception as e:
            print(f"Ошибка ИИ: {e}")
            return "", ""

    def search_all(self, query):
        """Поиск на всех сайтах"""
        all_results = []
        
        for site in self.sites:
            try:
                url = site['url'].format(query=query)
                response = requests.get(url, headers=self.headers, timeout=15)
                results = site['parser'](response.text)
                
                for r in results[:2]:  # Берём по 2 результата с сайта
                    r['source'] = site['name']
                    # Добавляем ИИ-описание
                    fabula, decision = self._get_ai_description(r['number'], r['title'])
                    r['fabula'] = fabula
                    r['decision'] = decision
                    all_results.append(r)
                    
                time.sleep(2)  # Пауза между сайтами
                
            except Exception as e:
                print(f"Ошибка на {site['name']}: {e}")
                
        return all_results

    def _parse_kad(self, html):
        """Парсинг kad.arbitr.ru"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for block in soup.find_all('div', class_='instance-card')[:2]:
            number_elem = block.find('div', class_='case-number')
            title_elem = block.find('div', class_='case-title')
            link_elem = block.find('a', href=True)
            
            case_number = number_elem.text.strip() if number_elem else "Номер не найден"
            title = title_elem.text.strip() if title_elem else "Название не найдено"
            
            if link_elem:
                href = link_elem.get('href')
                case_link = "https://kad.arbitr.ru" + href if href.startswith('/') else href
            else:
                case_link = None
            
            results.append({
                'number': case_number,
                'title': title[:150],
                'link': case_link,
                'pdf_link': None
            })
            
        return results

    def _parse_sudrf(self, html):
        """Парсинг sudrf.ru"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for link in soup.find_all('a', href=True)[:3]:
            href = link.get('href')
            text = link.text.strip()
            
            if href and any(word in href.lower() for word in ['case', 'decision', 'doc', 'act']):
                if not href.startswith('http'):
                    href = "https://sudrf.ru" + href
                
                results.append({
                    'number': 'Дело на sudrf.ru',
                    'title': text[:100] if text else "Судебный акт",
                    'link': href,
                    'pdf_link': href if '.pdf' in href.lower() else None
                })
                
        return results

    def _parse_sudact(self, html):
        """Парсинг sudact.ru"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for block in soup.find_all('div', class_='search-result-item')[:2]:
            title_elem = block.find('a', class_='search-result-item__title')
            if title_elem:
                title = title_elem.text.strip()
                link = title_elem.get('href')
                if link and not link.startswith('http'):
                    link = "https://sudact.ru" + link
                
                number_elem = block.find('span', class_='search-result-item__number')
                case_number = number_elem.text.strip() if number_elem else "Номер уточняется"
                
                results.append({
                    'number': case_number,
                    'title': title[:150],
                    'link': link,
                    'pdf_link': None
                })
                
        return results
