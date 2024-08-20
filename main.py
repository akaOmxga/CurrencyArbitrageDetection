import requests
import networkx as nx
import numpy as np

############################################## Détection des cycles rentables ##############################################

def find_cycles(graph, start_node):
    def dfs(current_node, current_product, path, visited):
        if current_node in visited:
            if current_node == start_node and current_product > 1:
                cycles.append((list(path), current_product))
            return

        visited.add(current_node)
        path.append(current_node)

        for neighbor in graph[current_node]:
            weight = graph[current_node][neighbor]['weight']
            dfs(neighbor, current_product * weight, path, visited)

        visited.remove(current_node)
        path.pop()

    cycles = []
    dfs(start_node, 1.0, [], set())
    return cycles

def normalize_cycle(cycle):
    min_node_index = cycle.index(min(cycle))
    normalized_cycle = cycle[min_node_index:] + cycle[:min_node_index]
    return tuple(normalized_cycle)

def find_profitable_arbitrage_cycles(graph):
    all_cycles = []
    for node in graph.nodes:
        cycles = find_cycles(graph, node)
        all_cycles.extend(cycles)
    
    # Remove duplicate cycles and keep track of their profitability
    unique_cycles = []
    seen = set()
    for cycle, product in all_cycles:
        normalized_cycle = normalize_cycle(cycle)
        if normalized_cycle not in seen:
            seen.add(normalized_cycle)
            unique_cycles.append((cycle, product))
    
    # Sort cycles by profitability in descending order
    sorted_cycles = sorted(unique_cycles, key=lambda x: x[1], reverse=True)
    
    return sorted_cycles

############################################## Création du graphe ##############################################

def add_currency(graph, currency): # ajoute la currency au graph
    if currency not in graph:
        graph.add_node(currency)
    return(graph)
    
def add_exchange_rate(graph, from_currency, to_currency, rate): # ajoute le poids rate entre les sommets from_currency et to_currency au graph
    graph.add_edge(from_currency, to_currency, weight=rate)
    return(graph)
    
def fetch_exchange_rates(api_key, base_url, base_currency, currencies):
    url = f"{base_url}/{api_key}/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()
    if data["result"] == "success":
        return {currency: rate for currency, rate in data["conversion_rates"].items() if currency in currencies}
    else:
        raise Exception(f"Error fetching exchange rates: {data['error-type']}")


def NetworkCurrency(api_key, base_url, currency_list):
    base_currency = "USD"  # Devise de base pour commencer
    graph = nx.DiGraph()

    # Ajouter la devise de base si elle est dans la liste
    if base_currency in currency_list:
        add_currency(graph, base_currency)

    # Récupérer les taux de change pour la devise de base
    rates = fetch_exchange_rates(api_key, base_url, base_currency, currency_list)

    # Ajouter les devises et les taux de change au graphe
    for currency, rate in rates.items():
        if currency in currency_list:
            add_currency(graph, currency)
            add_exchange_rate(graph, base_currency, currency, rate)
            add_exchange_rate(graph, currency, base_currency, 1 / rate)

    # Récupérer les taux de change pour les autres devises
    for currency in rates.keys():
        if currency != base_currency and currency in currency_list:
            try:
                new_rates = fetch_exchange_rates(api_key, base_url, currency, currency_list)
                for new_currency, new_rate in new_rates.items():
                    if new_currency in currency_list:
                        add_currency(graph, new_currency)
                        add_exchange_rate(graph, currency, new_currency, new_rate)
                        add_exchange_rate(graph, new_currency, currency, 1 / new_rate)
            except Exception as e:
                print(f"Error fetching rates for {currency}: {e}")

    return graph

# Création du graphe 
print("#################################")
print("Etape 1 - Création du Graphe")
print("#################################")
api_key = "eb1cf95333aaf1df1a8b0719"
base_url = "https://v6.exchangerate-api.com/v6"
currency_list_top5 = ["USD", "EUR", "JPY", "GBP", "AUD"]  
currency_list_top10 = currency_list_top5 + ["CAD", "CHF", "CNY", "HKD", "NZD"]  
currency_list_top20 = currency_list_top10 + ["SEK", "KRW", "SGD", "NOK", "MXN", "INR", "RUB", "ZAR", "TRY", "BRL"]  
graph = NetworkCurrency(api_key, base_url, currency_list_top5)
print("DONE")
print("#################################")

############################################## Appel de la fonction sur le graphe ##############################################

print("Etape 2 - Recherche de Cycles Profitables")
print("#################################")
# Détection des cycles profitables dans le graphe de test
profitable_cycles = find_profitable_arbitrage_cycles(graph)
print("DONE")
print("#################################")
print("Etape 3 -Affichages des Cycles Profitables")
print("#################################")
if profitable_cycles:
    print("Profitable cycles detected:")
    for cycle, product in profitable_cycles:
        print(f"Cycle: {' -> '.join(cycle)} with product: {product}")
else:
    print("No profitable cycles detected.")

print("#################################")
print("DONE - Thanks for Using the Bot")
print("#################################")


