🎰 Mega-Sena: Simulação e Análise Estatística em Escala
Este projeto utiliza Ciência de Dados e Simulações de Monte Carlo para desmistificar padrões em jogos de azar e validar leis fundamentais da estatística. Através do processamento de milhões de jogos simulados, o projeto coloca à prova a intuição humana contra o rigor matemático.


Processamento em Escala: Desenvolvimento de um motor de simulação em Python capaz de gerar e analisar 1 milhão de concursos em poucos segundos.



Engenharia de Dados Aplicada: Consumo e análise do histórico real de mais de 2.950 concursos da Mega-Sena (desde 1996).



Data Storytelling: Transformação de dados brutos em insights de negócios (Teoria dos Jogos aplicada à economia de prêmios).


📊 Conceitos de Ciência de Dados Validados
O repositório contém scripts que provam visual e matematicamente:


Lei dos Grandes Números: Demonstração de como a frequência das dezenas converge para a média à medida que o volume de dados aumenta, eliminando "números quentes" ilusórios.



Teorema do Limite Central: Visualização da Distribuição Normal (Curva de Gauss) resultante da soma das dezenas sorteadas.



Equiprobabilidade: Validação de que, em eventos independentes, sequências "estéticas" (ex: 01-02-03-04-05-06) possuem a mesma probabilidade matemática de jogos aleatórios.


🛠️ Stack Tecnológica & Arquitetura
O projeto foi construído focando em performance, fidelidade estatística e interatividade, utilizando as seguintes bibliotecas:


 - Processamento de Dados e Vetorização: pandas e numpy para manipulação eficiente de grandes volumes de dados históricos e simulados.

 - Simulação de Alta Performance: Utilização de concurrent.futures (ProcessPoolExecutor) para paralelizar a execução em múltiplos núcleos de CPU, permitindo rodar 1 milhão de simulações em tempo recorde.


 - Geração de Números Aleatórios: Uso da biblioteca secrets em vez do padrão random, garantindo números aleatórios criptograficamente fortes, essenciais para a validade estatística de um simulador de loteria.

 - Visualização e Análise Gráfica:


    - matplotlib para a criação de histogramas e curvas de densidade (Gauss).


    - matplotlib.widgets (Slider, RangeSlider, TextBox) para criar dashboards interativos diretamente no ambiente de execução, permitindo explorar diferentes janelas temporais e frequências de dezenas.


    - matplotlib.cm, ticker e dates para formatação avançada de eixos e mapas de cores para melhor legibilidade dos dados.

📈 Insights Principais

A Memória das Bolinhas: Prova de que o sorteio não possui memória; desvios em amostras curtas são apenas ruído estatístico.


⚙️ Como Executar
## Usage

Run the script with Python:

```bash
python simulacao_e_historico.py
```


## Requirements

pip install -r requirements.txt

🔗 Artigo Completo
A tese detalhada por trás deste código pode ser lida no meu blog:


Guia Definitivo: Como Ganhar Dinheiro com Loterias (Segundo a Ciência de Dados).
https://pedroteles.blog/2025/12/27/guia-definitivo-como-ganhar-dinheiro-com-loterias-segundo-a-ciencia-de-dados/


👨‍💻 Autor

Pedro Teles – Engenheiro de Dados focado em lógica, estatística e processamento de dados em escala.