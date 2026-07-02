# ⚡ WebCoord - Simulador de Coordenação e Seletividade

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-green)
![Pandapower](https://img.shields.io/badge/Pandapower-Simulação-orange)
![Plotly](https://img.shields.io/badge/Plotly.js-Gráficos-blueviolet)

Um simulador web interativo para estudos de coordenação de proteção, seletividade e cálculo de curto-circuito em redes de distribuição de energia elétrica de Média Tensão (MT).

## 📖 Sobre o Projeto

Estudos de proteção mal dimensionados resultam em atuações indevidas, desligando conjuntos elétricos inteiros por faltas isoladas. Na rotina de um Centro de Operações Integradas (COI), isso impacta diretamente os indicadores de continuidade (DEC e FEC) e expõe a concessionária a penalidades regulatórias.

O **WebCoord** foi desenvolvido para modernizar e simplificar esse processo. Ele substitui ferramentas legadas por uma interface web fluida, unindo a renderização de gráficos log-log em tempo real com um motor matemático robusto no backend baseado na norma IEC 60909.

### 🎯 Principais Funcionalidades

- **Coordenograma Interativo (Log-Log):** Visualização em tempo real do deslocamento de curvas de proteção ao alterar os parâmetros de *Pickup* e Dial de Tempo (TMS).
- **Biblioteca de Curvas:** Suporte nativo às equações normativas IEC (Normal, Muito e Extremamente Inversa) e ANSI/IEEE.
- **Integração de Equipamentos:** Cálculo automático de Corrente Nominal e plotagem do ponto de magnetização (*Inrush*) de transformadores.
- **Análise Dinâmica de Seletividade:** Cálculo instantâneo da margem de coordenação ($\Delta t$) com alertas visuais de aprovação/reprovação.
- **Motor de Curto-Circuito (Pandapower):** API backend que modela a topologia da rede e calcula as correntes de curto-circuito máximo (Trifásico) e mínimo (Monofásico Fase-Terra), plotando as restrições diretamente no gráfico.

## 🏗️ Arquitetura do Sistema

O projeto adota uma arquitetura em duas camadas, separando a interface gráfica do processamento elétrico pesado:

* **Frontend (Cliente):** `HTML5`, `CSS3` e `Vanilla JavaScript`. Utiliza a biblioteca **Plotly.js** para lidar com a complexidade matemática e performance de múltiplos *traces* em eixos logarítmicos simultâneos.
* **Backend (Servidor):** API construída em **Python + Flask**, utilizando a biblioteca **Pandapower** para modelagem de barramentos, transformadores e linhas de distribuição, executando o fluxo de potência e extraindo as matrizes de curto-circuito.

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.8 ou superior
- Navegador web moderno (Chrome, Edge, Firefox)

### Instalação

1. Clone o repositório:
```bash
git clone [https://github.com/breletricidadegomes/Simulador_web_coordena-o_de_rel-s_el-tricos.git](https://github.com/breletricidadegomes/Simulador_web_coordena-o_de_rel-s_el-tricos.git)
cd webcoord
