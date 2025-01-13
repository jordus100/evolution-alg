import random
import numpy as np
import matplotlib.pyplot as plt

def load_cities_from_file(filename):
    cities = {}
    with open(filename, 'r') as file:
        for line in file:
            name, x, y = line.strip().split(',')
            cities[name] = (int(x), int(y))
    return cities

def distance(city1, city2):
    return np.linalg.norm(np.array(city1) - np.array(city2))

def create_distance_matrix(cities):
    city_list = list(cities.values())
    n = len(city_list)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = distance(city_list[i], city_list[j])
    return matrix

def initialize_population(pop_size, num_cities):
    population = [random.sample(range(num_cities), num_cities) for _ in range(pop_size)]
    return population

def calculate_route_length(individual, distance_matrix):
    total_distance = sum(distance_matrix[individual[i], individual[i + 1]] for i in range(len(individual) - 1))
    total_distance += distance_matrix[individual[-1], individual[0]]
    return total_distance

def roulette_selection(population, fitness):
    total_fitness = sum(fitness)
    probabilities = [f / total_fitness for f in fitness]
    selected_idx = np.random.choice(len(population), len(population), p=probabilities)
    return [population[i] for i in selected_idx]

def order_crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size
    child[start:end + 1] = parent1[start:end + 1]
    fill_from_parent2 = [gene for gene in parent2 if gene not in child]
    for i in range(size):
        if child[i] == -1:
            child[i] = fill_from_parent2.pop(0)
    return child

def uniform_mutation(individual, mutation_rate):
    if random.random() < mutation_rate:
        i = random.randint(0, len(individual) - 1)
        j = random.randint(0, len(individual) - 1)
        if i == j:
            j += 1
            j = j % len(individual)
        individual[i], individual[j] = individual[j], individual[i]
    return individual

def genetic_algorithm(cities, pop_size, num_generations, mutation_rate, crossover_rate=0.5):
    distance_matrix = create_distance_matrix(cities)
    num_cities = len(cities)
    population = initialize_population(pop_size, num_cities)
    fitness_history = []

    best_overall = None
    best_distance_overall = float('inf')
    best_generation = -1

    worst_overall = None
    worst_distance_overall = 0
    worst_generation = -1

    for generation in range(num_generations):
        fitness = [1 / calculate_route_length(ind, distance_matrix) for ind in population]
        fitness_history.append((max(fitness), min(fitness), sum(fitness) / len(fitness)))

        current_best = min(population, key=lambda ind: calculate_route_length(ind, distance_matrix))
        current_best_distance = calculate_route_length(current_best, distance_matrix)

        if current_best_distance < best_distance_overall:
            best_overall = current_best
            best_distance_overall = current_best_distance
            best_generation = generation

        current_worst = max(population, key=lambda ind: calculate_route_length(ind, distance_matrix))
        current_worst_distance = calculate_route_length(current_worst, distance_matrix)

        if current_worst_distance > worst_distance_overall:
            worst_overall = current_worst
            worst_distance_overall = current_worst_distance
            worst_generation = generation

        probs = [fit / sum(fitness) for fit in fitness]
        probs_sorted = probs.copy()
        probs_sorted.sort(reverse=True)
        print(probs_sorted)
        new_pop = []
        while len(new_pop) < pop_size:
            rand = random.random()
            prob_sum = 0
            for i in range(pop_size):
                if rand < probs_sorted[i] + prob_sum:
                    new_pop.append(population[probs.index(probs_sorted[i])])
                    break
                prob_sum += probs_sorted[i]
        cross_pop = new_pop.copy()
        print(len(new_pop))
        for i in range(pop_size):
            if random.random() < crossover_rate / 2:
                parent2 = random.randint(0, pop_size - 1)
                child1 = order_crossover(new_pop[i], new_pop[parent2])
                child2 = order_crossover(new_pop[parent2], new_pop[i])
                cross_pop[i] = child1
                cross_pop[parent2] = child2
        new_population = [uniform_mutation(ind, mutation_rate) for ind in cross_pop]

        population = new_population

    return best_overall, best_distance_overall, worst_overall, worst_distance_overall, fitness_history, best_generation, worst_generation

print("Program rozwiązujący problem komiwojażera za pomocą algorytmu genetycznego!")
filename = input("Podaj nazwę pliku z miastami (np. miasta.txt): ")
cities = load_cities_from_file(filename)

pop_size = int(input("Podaj rozmiar populacji: "))
num_generations = int(input("Podaj liczbę pokoleń: "))
mutation_rate = float(input("Podaj prawdopodobieństwo mutacji (np. 0.1 dla 10%): "))

best_individual, best_distance, worst_individual, worst_distance, fitness_history, best_generation, worst_generation = genetic_algorithm(cities, pop_size, num_generations, mutation_rate)

city_names = list(cities.keys())
city_coords = list(cities.values())

best_route_coords = [city_coords[i] for i in best_individual] + [city_coords[best_individual[0]]]
best_route_names = [city_names[i] for i in best_individual] + [city_names[best_individual[0]]]

worst_route_coords = [city_coords[i] for i in worst_individual] + [city_coords[worst_individual[0]]]
worst_route_names = [city_names[i] for i in worst_individual] + [city_names[worst_individual[0]]]

plt.figure(figsize=(15, 7))

plt.subplot(1, 3, 1)
plt.plot([1 / gen[0] for gen in fitness_history], label='Najkrótsza odległość')
plt.plot([1 / gen[1] for gen in fitness_history], label='Najdłuższa odległość')
plt.plot([1 / gen[2] for gen in fitness_history], label='Średnia odległość')
plt.xlabel('Pokolenie')
plt.ylabel('Odległość')
plt.title('Odległość w kolejnych pokoleniach')
plt.legend()

plt.subplot(1, 3, 2)
x, y = zip(*city_coords)
plt.scatter(x, y, color='red')
for i, name in enumerate(city_names):
    plt.text(city_coords[i][0] + 0.2, city_coords[i][1] + 0.2, name)
best_route_x, best_route_y = zip(*best_route_coords)
plt.plot(best_route_x, best_route_y, color='blue')
plt.title(f'Najlepsza trasa (Odległość: {best_distance:.2f}, Pokolenie: {best_generation})')
plt.legend()

plt.subplot(1, 3, 3)
plt.scatter(x, y, color='red')
for i, name in enumerate(city_names):
    plt.text(city_coords[i][0] + 0.2, city_coords[i][1] + 0.2, name)
worst_route_x, worst_route_y = zip(*worst_route_coords)
plt.plot(worst_route_x, worst_route_y, color='orange')
plt.title(f'Najgorsza trasa (Odległość: {worst_distance:.2f}, Pokolenie: {worst_generation})')
plt.legend()

plt.tight_layout()
plt.show()
