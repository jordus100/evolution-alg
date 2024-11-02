import math
import random
import matplotlib.pyplot as plt


def find_fn_max_genetically(optim_fn, fitness_fn, pop_size=10, pcross=0.5, pmut=0.1, ngen=10, interval=(-1, 26)):
    gene_length, offset = calc_gene_length(interval)
    pop = generate_pop(pop_size, gene_length, offset, interval)
    avg_fit = []
    max_fit = []
    min_fit = []
    for gen in range(ngen):
        fits = [fitness_fn(optim_fn, int(gene, 2) + offset, interval) for gene in pop]
        max_fit.append(max(fits))
        min_fit.append(min(fits))
        fits_sum = sum(fits)
        avg_fit.append(fits_sum / len(fits))
        probs = [fit / fits_sum for fit in fits]
        new_pop = []
        while len(new_pop) < pop_size:
            new_pop.extend([pop[i] for i in range(pop_size) if random.random() < probs[i]])
            cross_over(new_pop, pcross)
            mutate(new_pop, pmut, interval, offset)
        pop = new_pop
    plot_fn(optim_fn, interval)
    plot_results(max_fit, min_fit, avg_fit)


def calc_gene_length(interval):
    lower, upper = interval
    gene_length = int(math.log(upper - lower, 2)) + 1
    offset = lower
    return gene_length, offset


def generate_pop(pop_size, gene_length, offset, interval):
    pop = []
    while len(pop) < pop_size:
        gene = ''.join(random.choice('01') for _ in range(gene_length))
        if gene_in_interval(gene, interval, offset) and gene not in pop:
            pop.append(gene)
    return pop


def cross_over(pop, pcross):
    for i in range(len(pop)):
        if random.random() < pcross:
            cross_partner = random.randint(0, len(pop) - 1)
            if cross_partner == i:
                cross_partner = (cross_partner + 1) % len(pop)
            cross_point = random.randint(1, len(pop[i]) - 2)
            pop[i] = pop[i][:cross_point] + pop[cross_partner][cross_point:]
            pop[cross_partner] = pop[cross_partner][:cross_point] + pop[i][cross_point:]


def mutate(pop, pmut, interval, offset):
    for i in range(len(pop)):
        if random.random() < pmut:
            mutated = False
            while not mutated:
                mut_point = random.randint(0, len(pop[i]) - 1)
                new = pop[i][:mut_point] + ('0' if pop[i][mut_point] == '1' else '1') + pop[i][mut_point + 1:]
                if gene_in_interval(new, interval, offset):
                    pop[i] = new
                    mutated = True


def gene_in_interval(gene, interval, offset):
    return interval[0] <= int(gene, 2) + offset <= interval[1]


def fitness(fn, x, interval):
    if interval[0] <= x <= interval[1]:
        return fn(x)
    else:
        return 0


def plot_results(max_fit, min_fit, avg_fit):
    plt.plot(avg_fit, label='Średnie przystosowanie w kolejnych populacjach')
    plt.plot(max_fit, label='Maksymalne przystosowanie w kolejnych populacjach')
    plt.plot(min_fit, label='Minimalne przystosowanie w kolejnych populacjach')
    plt.legend()
    plt.show()


def plot_fn(fn, interval):
    x = [i for i in range(interval[0], interval[1])]
    y = [fn(i) for i in x]
    plt.plot(x, y, label='Funkcja optymalizowana')
    plt.legend()
    plt.show()


# Ask user for gen algorithm parameters
opt_fn = input("Wpisz funkcję maksymalizowaną: ")
pop_size = int(input("Wpisz rozmiar populacji: "))
pcross = float(input("Wpisz prawdopodobieństwo krzyżowania: "))
pmut = float(input("Wpisz prawdopodobieństwo mutacji:"))
ngen = int(input("Wpisz liczbę generacji:"))
lower = int(input("Wpisz dolną granicę przedziału:"))
upper = int(input("Wpisz górną granicę przedziału:"))
interval = (lower, upper)
find_fn_max_genetically(lambda x: eval(opt_fn), fitness, pop_size, pcross, pmut, ngen, interval)
