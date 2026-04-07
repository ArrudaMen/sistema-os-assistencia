#Sistema de Gestão de Ordens de Serviço (OS)

Um sistema desktop desenvolvido em Python focado em gerenciar Ordens de Serviço para assistências técnicas de T.I. e manutenção de hardware. O aplicativo acompanha o ciclo de vida do equipamento desde a entrada até a entrega, integrando comunicação direta com o cliente via WhatsApp e controle financeiro mensal.

#Funcionalidades Principais

* **Recepção de Equipamentos:** Cadastro de dados do cliente, avarias relatadas e laudo técnico inicial.
* **Bancada Virtual:** Painel dinâmico para acompanhamento dos equipamentos com status atualizáveis (Na Fila, Em Análise, Aguardando Peça, Pronto, etc).
* **Integração com WhatsApp:** Geração automática de mensagens personalizadas baseadas no status da OS (ex: envio de orçamentos detalhados ou aviso de equipamento pronto para retirada) direto para o WhatsApp Web.
* **Histórico e Faturamento:** Filtro inteligente de faturamento mensal, separando o lucro líquido de Mão de Obra do custo de Peças.
* **Exportação de Relatórios:** Geração de relatórios de fechamento de caixa em formato `.txt`.

#Tecnologias Utilizadas

* **Python** (Linguagem principal)
* **CustomTkinter** (Interface Gráfica UI/UX em Dark Mode)
* **SQLite3** (Banco de Dados Local estruturado)
* **Urllib / Webbrowser** (Integração externa)

#Como executar o projeto

1. Clone este repositório para a sua máquina.
2. Instale a biblioteca gráfica executando no terminal:
   `pip install customtkinter`
3. Execute o arquivo `OS_Tech.py`.
4. *Nota: O banco de dados `banco_os.db` será gerado automaticamente pelo script na primeira execução, garantindo a integridade das tabelas.*

---
Desenvolvido como projeto prático para aplicação de conceitos de Sistemas de Informação. 
