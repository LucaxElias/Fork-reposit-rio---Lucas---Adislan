# Aplicação para Reserva de Salas

Aplicação web para consulta e reserva de salas e laboratórios, desenvolvida em **Python** utilizando o framework **Streamlit**.

##  Sobre o projeto

O sistema tem como objetivo facilitar a consulta de salas disponíveis e o gerenciamento de reservas de ambientes acadêmicos.

O projeto está sendo desenvolvido de forma modular, separando a interface, os componentes, os serviços de lógica e os dados da aplicação.

##  Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- Git
- GitHub

##  Estrutura do projeto

```text
├── app/
│   ├── main.py
│   ├── pages/
│   │   ├── 1_Home.py
│   │   ├── 2_Salas.py
│   │   ├── 3_Detalhes_Sala.py
│   │   ├── 4_Reservar.py
│   │   └── 5_Minhas_Reservas.py
│   ├── components/
│   ├── services/
│   └── utils/
│
├── data/
│   ├── usuarios.csv
│   ├── salas.csv
│   ├── equipamentos.csv
│   ├── sala_equipamento.csv
│   └── reservas.csv
│
├── docs/
├── assets/
├── requirements.txt
└── README.md