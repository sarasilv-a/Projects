import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import t

# Dados fornecidos
data_threads = {
    "Nº de Threads": [1, 2, 5, 10, 15, 25, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
    "Total Time Taken (s)": [216, 190, 219, 226, 201, 206, 180, 171, 163, 157, 157, 152, 156, 151, 149, 150, 156],
    "Memory Used by Threads (MB)": [163, 176, 167, 196, 202, 182, 213, 187, 247, 207, 256, 257, 262, 344, 307, 378, 305]
}

data_clients = {
    "Nº de Clientes": [1, 5, 10, 50, 100],
    "Total Time Taken (s)": [0.108, 1.124, 3.622, 52.097, 103.062],
    "Memory Used (MB)": [1, 8, 14, 54, 120]
}

df_threads = pd.DataFrame(data_threads)
df_clients = pd.DataFrame(data_clients)

# Escalar os valores de threads para evitar overflow
df_threads["Scaled Threads"] = df_threads["Nº de Threads"] / 100

# Função para ajuste exponencial
def exponential_func(x, a, b):
    return a * np.exp(b * x)

# Função para calcular intervalo de confiança
def confidence_interval(popt, pcov, alpha=0.05):
    n_params = len(popt)
    dof = max(0, len(df_threads) - n_params)  # graus de liberdade
    t_val = t.ppf(1 - alpha / 2, dof)  # valor crítico de t
    errors = np.sqrt(np.diag(pcov))  # desvios padrão dos parâmetros
    ci = t_val * errors  # intervalo de confiança
    return ci

# Função para calcular p-values
def calculate_p_values(popt, pcov):
    dof = max(0, len(df_threads) - len(popt))  # graus de liberdade
    errors = np.sqrt(np.diag(pcov))
    t_stats = np.abs(popt / errors)
    p_values = (1 - t.cdf(t_stats, dof)) * 2
    return p_values

# Ajuste para 'Nº de Threads vs Total Time Taken'
try:
    popt_time_threads, pcov_time_threads = curve_fit(
        exponential_func, df_threads["Scaled Threads"], df_threads["Total Time Taken (s)"]
    )
    ci_time_threads = confidence_interval(popt_time_threads, pcov_time_threads)
    p_values_time_threads = calculate_p_values(popt_time_threads, pcov_time_threads)
    r2_time_threads = np.corrcoef(df_threads["Total Time Taken (s)"], exponential_func(df_threads["Scaled Threads"], *popt_time_threads))[0, 1] ** 2
except Exception as e:
    popt_time_threads, ci_time_threads, p_values_time_threads, r2_time_threads = [None, None], [None, None], [None, None], None
    print(f"Erro no ajuste para Nº de Threads vs Total Time Taken: {e}")

# Ajuste para 'Nº de Threads vs Memory Used by Threads'
try:
    popt_memory_threads, pcov_memory_threads = curve_fit(
        exponential_func, df_threads["Scaled Threads"], df_threads["Memory Used by Threads (MB)"]
    )
    ci_memory_threads = confidence_interval(popt_memory_threads, pcov_memory_threads)
    p_values_memory_threads = calculate_p_values(popt_memory_threads, pcov_memory_threads)
    r2_memory_threads = np.corrcoef(df_threads["Memory Used by Threads (MB)"], exponential_func(df_threads["Scaled Threads"], *popt_memory_threads))[0, 1] ** 2
except Exception as e:
    popt_memory_threads, ci_memory_threads, p_values_memory_threads, r2_memory_threads = [None, None], [None, None], [None, None], None
    print(f"Erro no ajuste para Nº de Threads vs Memory Used: {e}")

# Ajuste para 'Nº de Clientes vs Total Time Taken'
popt_time_clients, pcov_time_clients = curve_fit(exponential_func, df_clients["Nº de Clientes"], df_clients["Total Time Taken (s)"])
ci_time_clients = confidence_interval(popt_time_clients, pcov_time_clients)
p_values_time_clients = calculate_p_values(popt_time_clients, pcov_time_clients)
r2_time_clients = np.corrcoef(df_clients["Total Time Taken (s)"], exponential_func(df_clients["Nº de Clientes"], *popt_time_clients))[0, 1] ** 2

# Ajuste para 'Nº de Clientes vs Memory Used'
popt_memory_clients, pcov_memory_clients = curve_fit(exponential_func, df_clients["Nº de Clientes"], df_clients["Memory Used (MB)"])
ci_memory_clients = confidence_interval(popt_memory_clients, pcov_memory_clients)
p_values_memory_clients = calculate_p_values(popt_memory_clients, pcov_memory_clients)
r2_memory_clients = np.corrcoef(df_clients["Memory Used (MB)"], exponential_func(df_clients["Nº de Clientes"], *popt_memory_clients))[0, 1] ** 2

# Estatísticas: Média e Desvio Padrão
means_threads = df_threads.mean()
std_devs_threads = df_threads.std()

means_clients = df_clients.mean()
std_devs_clients = df_clients.std()

# Impressão dos resultados
print("Regressão Exponencial para Threads:")
if popt_time_threads[0] is not None:
    print(f"Nº de Threads vs Total Time Taken (s): a = {popt_time_threads[0]:.3f}, b = {popt_time_threads[1]:.3f}, CI = ±{ci_time_threads}, p-values = {p_values_time_threads}, R² = {r2_time_threads:.3f}")
else:
    print("Nº de Threads vs Total Time Taken (s): Ajuste não realizado com sucesso.")

if popt_memory_threads[0] is not None:
    print(f"Nº de Threads vs Memory Used by Threads (MB): a = {popt_memory_threads[0]:.3f}, b = {popt_memory_threads[1]:.3f}, CI = ±{ci_memory_threads}, p-values = {p_values_memory_threads}, R² = {r2_memory_threads:.3f}")
else:
    print("Nº de Threads vs Memory Used by Threads (MB): Ajuste não realizado com sucesso.")

print("\nMédias e Desvios Padrões para Threads:")
print("Médias:", means_threads)
print("Desvios Padrões:", std_devs_threads)

print("\nRegressão Exponencial para Clientes:")
print(f"Nº de Clientes vs Total Time Taken (s): a = {popt_time_clients[0]:.3f}, b = {popt_time_clients[1]:.3f}, CI = ±{ci_time_clients}, p-values = {p_values_time_clients}, R² = {r2_time_clients:.3f}")
print(f"Nº de Clientes vs Memory Used (MB): a = {popt_memory_clients[0]:.3f}, b = {popt_memory_clients[1]:.3f}, CI = ±{ci_memory_clients}, p-values = {p_values_memory_clients}, R² = {r2_memory_clients:.3f}")

print("\nMédias e Desvios Padrões para Clientes:")
print("Médias:", means_clients)
print("Desvios Padrões:", std_devs_clients)
