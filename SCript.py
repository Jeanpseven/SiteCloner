import requests
import os
from urllib.parse import urlparse, urljoin

def clone_website(url):
    try:
        # Faz a solicitação HTTP ao host especificado com um cabeçalho de agente do usuário
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        # Verifica se a solicitação foi bem-sucedida (status code 200)
        if response.status_code == 200:
            # Obtém o conteúdo HTML
            html_content = response.text
            
            # Obtém o conteúdo CSS
            css_content = get_css_content(response)
            
            # Obtém o nome do site a partir da URL
            site_name = get_site_name(url)
            
            # Cria um diretório com o nome do site
            directory = site_name
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Salva o conteúdo HTML em um arquivo index.html
            html_file_path = os.path.join(directory, "index.html")
            with open(html_file_path, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)
            
            # Salva o conteúdo CSS em um arquivo style.css
            css_file_path = os.path.join(directory, "style.css")
            with open(css_file_path, 'w', encoding='utf-8') as css_file:
                css_file.write(css_content)
            
            # Copia as imagens para a pasta img
            img_directory = os.path.join(directory, "img")
            if not os.path.exists(img_directory):
                os.makedirs(img_directory)
            
            image_urls = get_image_urls(response, url)
            for image_url in image_urls:
                save_image(image_url, img_directory)
            
            print("Clonagem concluída com sucesso!")
            print("Arquivos clonados salvos no diretório:", directory)
        else:
            print("Falha ao clonar o website. Status code:", response.status_code)
    
    except requests.exceptions.RequestException as e:
        print("Erro durante a solicitação HTTP:", e)

def get_css_content(response):
    # Verifica se o Content-Type da resposta é CSS
    if 'text/css' in response.headers.get('Content-Type'):
        return response.text
    
    # Caso contrário, procura por um link para um arquivo CSS e faz uma nova solicitação
    links = response.text.split('<link')
    for link in links:
        if 'stylesheet' in link and 'href' in link:
            css_url = link.split('href="')[1].split('"')[0]
            css_response = requests.get(css_url)
            if css_response.status_code == 200:
                return css_response.text
    
    return ""

def get_site_name(url):
    # Extrai o nome do site a partir da URL
    domain = urlparse(url).netloc
    site_name = domain.split('.')[0]
    return site_name

def get_image_urls(response, base_url):
    # Obtém as URLs das imagens no conteúdo HTML
    image_urls = []
    base_url = urlparse(base_url).scheme + "://" + urlparse(base_url).netloc
    
    images = response.text.split('<img')
    for image in images:
        if 'src' in image:
            src = image.split('src="')[1].split('"')[0]
            image_url = urljoin(base_url, src)
            image_urls.append(image_url)
    
    return image_urls

def save_image(image_url, directory):
    try:
        # Faz a solicitação HTTP para obter a imagem
        response = requests.get(image_url, stream=True)
        
        # Verifica se a solicitação foi bem-sucedida (status code 200)
        if response.status_code == 200:
            # Obtém o nome do arquivo da URL
            filename = os.path.basename(urlparse(image_url).path)
            
            # Salva a imagem no diretório especificado
            image_path = os.path.join(directory, filename)
            with open(image_path, 'wb') as image_file:
                for chunk in response.iter_content(chunk_size=1024):
                    image_file.write(chunk)
        else:
            print("Falha ao baixar a imagem:", image_url)
    
    except requests.exceptions.RequestException as e:
        print("Erro durante a solicitação HTTP:", e)

# URL fornecida pelo usuário
url = input("Digite a URL do website a ser clonado: ")
clone_website(url)
