import secrets

def gerar_jogo_mega_sena():
    # Usa o gerador criptograficamente seguro do sistema
    rng = secrets.SystemRandom()
    
    # Sorteia 6 números únicos entre 1 e 60
    # range(1, 61) vai de 1 até 60
    numeros = rng.sample(range(1, 61), 6)
    
    # Ordena apenas para facilitar a marcação no volante
    return sorted(numeros)

# Exemplo de uso: Gerar 1 jogo
print(f"Seu jogo: {gerar_jogo_mega_sena()}")

# Exemplo: Gerar 5 jogos (Bolão)
# for i in range(5):
#     print(f"Jogo {i+1}: {gerar_jogo_mega_sena()}")