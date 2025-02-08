import requests
import openai
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import fuzz
import itertools
from urllib.parse import urlparse, urljoin
requests.packages.urllib3.disable_warnings()


base_link = 'https://www.thisiscolossal.com/'
to_find = ['privacy policy', 'privacy']
ollama_model = "llama3.2"  # deepseek-r1 compatible, removes think tag


def get_page_content(link, text_only=False):
    headers = {
        'accept': '*/*',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    loaded = False
    for i in range(3):
        try:
            resp = requests.get(link, headers=headers, verify=False).text
            loaded = True
            break
        except:
            print("Failed to open {}".format(link))
    if not loaded:
        return "", []
    soup = bs(resp, 'html.parser')
    page_text = soup.get_text(separator='\n')
    if text_only:
        return page_text, []
    page_text = '\n'.join([x.strip() for x in page_text.split('\n')])
    page_links = soup.find_all('a', href=True)
    domain = urlparse(link).netloc.replace('www.', '')
    # filter internal links and links without domain
    page_links = [link['href'] for link in page_links]
    final_links = []
    for link in page_links:
        if link.startswith('//'):
            link = 'https:' + link
        elif link.startswith('://'):
            link = 'https' + link

        if not link.startswith('http'):
            link = 'https://' + link
        if urlparse(link).netloc.replace('www.', '') != domain:
            continue
        link = urljoin(urlparse(link).scheme + '://' +
                       domain, urlparse(link).path)
        final_links.append(link)
    return page_text, final_links


def find_possible_content_page(links):
    global to_find
    # remove domain from the link
    domain = urlparse(links[0]).netloc.replace('www.', '')
    links = [link.replace('https://' + domain, '') for link in links]
    to_find = [x.lower() for x in to_find]
    # for link in links:
    #     print(link)

    most_accurate_link = None
    accuracy_ratio = 90
    for word_1, word_2 in itertools.product(links, to_find):
        ratio = fuzz.partial_ratio(word_1, word_2)
        if ratio > accuracy_ratio:
            most_accurate_link = word_1
            if ratio > accuracy_ratio:
                accuracy_ratio = ratio
    most_accurate_link = 'https://' + domain + '/' + most_accurate_link
    return most_accurate_link


def get_completion(prompt, model=ollama_model):
    messages = [
        {"role": "system", "content": r"You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    client = openai.OpenAI(
        base_url="http://localhost:11434/v1", api_key="ollama")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    response_text = response.choices[0].message.content
    response_text = response_text.split('</think>')[-1].strip()
    return response_text.strip()


if __name__ == "__main__":
    if not base_link.startswith('http'):
        base_link = 'https://' + base_link
    page_text, page_links = get_page_content(base_link)
    if page_links:
        contact_link = find_possible_content_page(page_links)
        print(contact_link)
        page_text, page_links = get_page_content(contact_link, text_only=True)
        prompt = "Summarize this text in 5 sentences: \n\n" + page_text
        response = get_completion(prompt)
        print(response)
    else:
        print("No links found in this page, maybe bot protected website!")
