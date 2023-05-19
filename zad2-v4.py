import json, sys
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import networkx as nx

def get_input():
    inputted = []

    while True:
        try:
            line = input()
        except EOFError:
            break
        inputted.append(line)

    return ''.join(inputted)


def is_acyclic(edges):
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    # Tworzenie grafu i obliczanie stopnia wejścia dla każdego wierzchołka
    for edge in edges:
        u, v = edge
        graph[u].append(v)
        in_degree[v] += 1

    # Znalezienie wierzchołków bez wchodzących krawędzi
    queue = deque([u for u in graph if in_degree[u] == 0])

    # Usuwanie wierzchołków bez wchodzących krawędzi oraz krawędzi wychodzących z nich
    while queue:
        u = queue.popleft()
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    # Jeśli po usunięciu wszystkich wierzchołków bez wchodzących krawędzi w grafie pozostają jakieś krawędzie,
    # to graf zawiera cykl i nie jest acykliczny
    for u in graph:
        if in_degree[u] > 0:
            return False

    return True


def get_adj_list(edges):
    graph = {}
    for edge in edges:
        u, v = edge
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
        graph[u].append(v)
        graph[v].append(u)

    return dict(sorted(graph.items()))


def get_ordering(adj_list, nodes):
    new_dict = {}

    for k in adj_list:
        new_dict[k] = 0
        for n in adj_list[k]:
            # znalazlem poprzednika
            if ord(n) < ord(k):
                # jesli to najdluzsza sciezka, robie update
                if new_dict[k] < (nodes[n] + new_dict[n]):
                    new_dict[k] = nodes[n] + new_dict[n]

    return new_dict


def get_next_node(node, adj_list, nodes):
    next_weight = 0
    next_node = None

    for next in adj_list[node]:
        if ord(next) > ord(node):
            if nodes[next] > next_weight:
                next_weight = nodes[next]
                next_node = next

    return next_node


def get_critical_path(adj_list, nodes):
    first_el = list(nodes.keys())[0]
    last_el = list(nodes.keys())[-1]

    critical_path = [first_el]

    act_el = first_el
    next_node = None

    while next_node != last_el:
        next_node = get_next_node(act_el, adj_list, nodes)
        # print(f"next node for : {act_el} is {next_node}")
        act_el = next_node
        critical_path.append(next_node)

    return critical_path


def print_result(critical_path, nodes, start_times):
    print(f"Ścieżka krytyczna: {' -> '.join(sorted(critical_path))}")

    last_time = 0

    print("Uszeregowanie zadań:",end=" ")
    for k, v in start_times.items():
        if k == list(start_times.keys())[-1]:
            print(f"{k} ({v}-{v+nodes[k]})")
            last_time = v+nodes[k]
        else:
            print(f"{k} ({v}-{v+nodes[k]}),", end=" ")

    print(f"Łączny czas wykonania: {last_time} dni")


def extend_nodes(adj_list, nodes):
    new_nodes = {}

    for k in adj_list.keys():
        if k in nodes:
            new_nodes[k] = nodes[k]
        else:
            new_nodes[k] = 0

    return new_nodes


def get_durations(critical_path, nodes):
    durations = []

    for k in critical_path:
        durations.append(nodes[k])

    return durations


def print_graph(edges, critical_path):
    # przygotowanie graiicznej interpretacji grafu
    G = nx.Graph()
    G.add_edges_from(edges)

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)

    # pobranie krawędzi na podstawie sciezki krytycznje
    path_edges = list(nx.utils.pairwise(critical_path))

    # kolorowanie ścieżki krytycznej na czerwono
    edge_colors = ['red' if edge in path_edges else 'black' for edge in G.edges()]
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors)

    # wyświetlenie grafu - tak aby mozliwe bylo otwarcie 2 okien na raz
    plt.show(block=False)


def print_gantt(critical_path, nodes):
    # przygotowanie graficznej interpretacji wykresu Gantta
    durations = get_durations(critical_path, nodes)

    fig, gnt = plt.subplots()

    gnt.set_ylim(0, 15 * len(critical_path))
    gnt.set_xlim(0, sum(durations))
    gnt.set_xlabel('Czas')
    gnt.set_ylabel('Zadania')

    for i in range(len(critical_path)):
        gnt.broken_barh([(sum(durations[:i]), durations[i])], (10*(i+1), 9))
        gnt.text(sum(durations[:i])+0.5*durations[i], 10*(i+1)+4.5, critical_path[i], fontsize=10, ha='center', va='center')

    plt.show()


def main():
    inputted = get_input()
    to_dict = json.loads(inputted)
    nodes = to_dict['nodes']
    edges = to_dict['edges']

    if not is_acyclic(edges):
        print("Błąd: Graf zawiera cykl, nie można wyznaczyć ścieżki krytycznej.")
        sys.exit()

    adj_list = get_adj_list(edges)

    start_times = get_ordering(adj_list, nodes)

    critical_path = get_critical_path(adj_list, nodes)

    print_result(critical_path, nodes, start_times)

    print_graph(edges, critical_path)

    print_gantt(critical_path, nodes)


main()