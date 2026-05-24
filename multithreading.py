import requests
import time
import csv
import random
import threading
import concurrent.futures
import json 

from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

BASE_URL = "https://havokkmorands.github.io/movie-catalog/"
data_lock = threading.Lock()
movies_data_list = [] 

def extract_movie_details(movie_link):
    time.sleep(random.uniform(0, 0.1)) # Delay leve para simular requisição 
    
    try:
        response = requests.get(movie_link, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return

    movie_soup = BeautifulSoup(response.content, "html.parser")
    detail_container = movie_soup.find("section", attrs={"data-testid": "movie-detail"})
    
    if detail_container is None:
        return

    title_tag = detail_container.find(attrs={"data-testid": "movie-title"})
    release_tag = detail_container.find(attrs={"data-testid": "movie-release"})
    rating_tag = detail_container.find(attrs={"data-testid": "movie-rating"})
    synopsis_tag = detail_container.find(attrs={"data-testid": "movie-synopsis"})

    title = title_tag.get_text(strip=True) if title_tag else None
    date = release_tag.get_text(strip=True).replace("Lançamento:", "").strip() if release_tag else None
    rating = rating_tag.get_text(strip=True).replace("Nota:", "").strip() if rating_tag else None
    plot_text = synopsis_tag.get_text(strip=True).replace("Sinopse:", "").strip() if synopsis_tag else None

    if all([title, date, rating, plot_text]):
        movie_dict = {
            "nome": title,
            "data_lancamento": date,
            "nota": rating,
            "sinopse": plot_text
        }

        with data_lock:
            with open("movies.csv", mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([title, date, rating, plot_text])
            
            movies_data_list.append(movie_dict)

def extract_movies(soup, num_threads):
    container = soup.find("section", attrs={"data-testid": "movies-list"})
    if container is None:
        print("Container principal não encontrado.")
        return

    movies_table = container.find_all("article", attrs={"data-testid": "movie-item"})
    if not movies_table:
        print("Lista de filmes não encontrada.")
        return

    movie_links = []
    for movie in movies_table:
        a_tag = movie.find("a", attrs={"data-testid": "movie-link"}, href=True)
        if a_tag:
            movie_links.append(urljoin(BASE_URL, a_tag["href"]))

    if not movie_links:
        print("Nenhum link de filme foi encontrado.")
        return

    print(f"-> Executando extração com {num_threads} thread(s)...")
    
    threads = min(num_threads, len(movie_links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(extract_movie_details, movie_links)

def executar_teste_completo(soup, qtd_threads):
    global movies_data_list
    movies_data_list = [] # Limpa a lista para o novo teste
    
    # Reinicia o arquivo CSV para não duplicar dados entre os testes
    with open("movies.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Data de Lancamento", "Nota", "Sinopse"])
        
    start_time = time.time()
    extract_movies(soup, qtd_threads)
    end_time = time.time()
    
    return end_time - start_time

def main():
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        print("=== INICIANDO EXPERIMENTO DE PERFORMANCE ===")
        
        # 1. Teste com Apenas 1 Thread 
        tempo_single = executar_teste_completo(soup, qtd_threads=1)
        print(f"   Tempo com 1 Thread: {tempo_single:.2f} segundos\n")
        
        # 2. Teste com Múltiplas Threads 
        QTD_MULTITHREAD = 15 
        tempo_multi = executar_teste_completo(soup, qtd_threads=QTD_MULTITHREAD)
        print(f"   Tempo com {QTD_MULTITHREAD} Threads: {tempo_multi:.2f} segundos\n")
        
        # Salva o arquivo JSON final 
        with open("movies.json", "w", encoding="utf-8") as json_file:
            json.dump(movies_data_list, json_file, ensure_ascii=False, indent=4)
            
        # 3. RELATÓRIO COMPARATIVO 
        print("================ RELATÓRIO ================")
        print(f"Single-Thread (1 thread): {tempo_single:.2f}s")
        print(f"Multi-Thread ({QTD_MULTITHREAD} threads): {tempo_multi:.2f}s")
        ganho_performance = (tempo_single / tempo_multi)
        print(f"O Multithreading foi {ganho_performance:.1f}x mais rápido!")
        print("===========================================")
        print("Arquivos 'movies.csv' e 'movies.json' salvos")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página principal: {e}")

if __name__ == "__main__":
    main()