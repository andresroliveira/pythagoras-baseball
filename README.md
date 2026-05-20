# Pythagorean Gamma Fit

Este projeto estima empiricamente o expoente da fórmula pitagórica do baseball a partir de dados históricos de times.

A fórmula pitagórica estima a porcentagem de vitórias de um time usando apenas corridas marcadas (`RS`) e corridas sofridas (`RA`):

$$
WinPct = \frac{RS^\gamma}{RS^\gamma + RA^\gamma}
$$

Dividindo numerador e denominador por \(RS^\gamma\), obtemos a forma equivalente usada no código:

$$
WinPct = \frac{1}{1 + (RA/RS)^\gamma}
$$

O objetivo do projeto é estimar o melhor valor de \(\gamma\) e comparar três versões da fórmula:

- $\gamma = 2.00$, a versão pitagórica original;
- $\gamma = 1.83$, valor usado pelo Baseball-Reference;
- $\gamma$ estimado diretamente a partir dos dados.

## Ideia

Para cada time-temporada, o script calcula:

```text
RA_over_RS = RA / RS
WinPct     = W / (W + L)
````

Depois ajusta o modelo:

$$
y = \frac{1}{1 + x^\gamma}
$$

onde:

```text
x = RA / RS
y = WinPct
```

Além do ajuste não linear direto, o código também usa uma linearização.

Partindo de:

$$
y = \frac{1}{1+x^\gamma}
$$

temos:

$$
\frac{1}{y} - 1 = x^\gamma
$$

Tomando logaritmo:

$$
\log\left(\frac{1}{y}-1\right) = \gamma \log(x)
$$

Assim, definimos:

```text
X = log(RA / RS)
Y = log(1 / WinPct - 1)
```

e ajustamos:

$$
Y = \gamma X
$$

Também é testada uma versão com intercepto:

$$
Y = a + \gamma X
$$

O intercepto serve como diagnóstico: se $a$ fica perto de zero, a forma teórica sem intercepto está bem calibrada.

## Dados

O script espera um arquivo chamado [Teams.csv](https://raw.githubusercontent.com/cbwinslow/baseballdatabank/master/core/Teams.csv).

Esse arquivo deve conter dados históricos de times, como a tabela `Teams` do Baseball Databank.

As colunas usadas são:

```text
yearID
teamID
lgID
W
L
R
RA
```

Onde:

- `yearID`: ano da temporada;
- `teamID`: identificador do time;
- `lgID`: liga;
- `W`: vitórias;
- `L`: derrotas;
- `R`: corridas marcadas;
- `RA`: corridas sofridas.

## Como executar

Instale as dependências:

```bash
pip install pandas numpy scipy
```

Coloque o arquivo `Teams.csv` no mesmo diretório do script.

Execute:

```bash
python pythagorean_gamma_fit.py
```

## O que o script calcula

Para cada recorte histórico, o script estima:

```text
gamma_linear
gamma_nonlinear
gamma_intercept
a_intercept
```

### `gamma_linear`

Estimativa de $\gamma$ obtida pela regressão linearizada sem intercepto:

$$
Y = \gamma X
$$

### `gamma_nonlinear`

Estimativa de $\gamma$ obtida por quadrados mínimos não lineares, minimizando diretamente o erro em `WinPct`:

$$
\sum_i \left(
WinPct_i -
\frac{1}{1+(RA_i/R_i)^\gamma}
\right)^2
$$

Essa é a estimativa mais diretamente comparável ao problema original.

### `gamma_intercept`

Estimativa de $\gamma$ na regressão linearizada com intercepto:

$$
Y = a + \gamma X
$$

### `a_intercept`

Intercepto da regressão linearizada com intercepto.

Se esse valor fica próximo de zero, isso sugere que a fórmula pitagórica pura está bem centrada.

## Comparação de erros

O script também compara os erros dos modelos com:

```text
gamma = 2.00
gamma = 1.83
gamma = gamma estimado
```

A tabela de comparação contém as colunas:

```text
start
model
gamma
mae_wins
rmse_wins
mae_winpct
rmse_winpct
```

### `start`

Ano inicial do recorte histórico.

Por exemplo:

```text
1947
```

significa que foram usados todos os time-temporadas de 1947 em diante.

### `model`

Modelo testado:

```text
2.00       expoente original
1.83       expoente usado pelo Baseball-Reference
estimated  expoente estimado pelo ajuste não linear
```

### `gamma`

Valor do expoente usado na fórmula.

### `mae_wins`

Erro absoluto médio em número de vitórias.

Por exemplo, se `mae_wins = 3.18`, o modelo erra em média cerca de 3.18 vitórias por time-temporada.

### `rmse_wins`

Raiz do erro quadrático médio em vitórias.

Essa métrica pune erros grandes mais fortemente que o erro absoluto médio.

### `mae_winpct`

Erro absoluto médio em winning percentage.

Por exemplo, `mae_winpct = 0.020` significa erro médio de aproximadamente 2 pontos percentuais de winning percentage.

### `rmse_winpct`

Raiz do erro quadrático médio em winning percentage.

## Recortes históricos

O script calcula os resultados para os seguintes recortes:

```text
geral
1871+
1901+
1920+
1947+
1961+
1969+
1998+
2000+
```

A ideia é verificar se o expoente ótimo muda conforme a era histórica do baseball.

## Resultados obtidos

Em uma execução com `Teams.csv`, os principais resultados foram:

| sample| n| gamma_linear| gamma_nonlinear| gamma_intercept| a_intercept|
|---|---:|---:|---:|---:|---:|
| geral| 2983| 1.875815| 1.862384| 1.875612| 0.003380|
| 1871+| 2983| 1.875815| 1.862384| 1.875612| 0.003380|
| 1901+| 2602| 1.853545| 1.850287| 1.853563| 0.001448|
| 1920+| 2282| 1.860777| 1.856743| 1.860785| 0.001031|
| 1947+| 1850| 1.838533| 1.834723| 1.838554| 0.001222|
| 1961+| 1626| 1.848955| 1.844565| 1.848986| 0.001368|
| 1969+| 1468| 1.843210| 1.840304| 1.843244| 0.001319|
| 1998+| 720| 1.854092| 1.850420| 1.854200| 0.002348|
| 2000+| 660| 1.846218| 1.842449| 1.846339| 0.002517|

## Conclusão

Os resultados mostram que o expoente original `2.00` funciona razoavelmente, mas é sistematicamente um pouco alto.

Em todos os recortes testados, `gamma = 1.83` produziu erro menor que `gamma = 2.00`.

Além disso, o expoente estimado ficou próximo de `1.83`, especialmente em recortes modernos. No período `1947+`, por exemplo, o ajuste não linear encontrou:

```text
gamma_nonlinear = 1.834723
```

Esse valor é praticamente igual ao `1.83` usado pelo Baseball-Reference.

Portanto, o experimento reproduz empiricamente a justificativa para usar `1.83` em vez de `2.00`: a melhora é pequena, mas consistente.

## Interpretação

A escolha de `1.83` não deve ser entendida como uma constante matemática exata. Ela é uma aproximação empírica que funciona bem para dados históricos de baseball.

O valor ótimo pode mudar dependendo de:

- período histórico considerado;
- inclusão ou exclusão do século XIX;
- forma de minimizar o erro;
- uso de winning percentage ou número de vitórias;
- ponderação por número de jogos;
- mudanças no ambiente ofensivo da liga.

Mesmo assim, os resultados indicam que `1.83` é uma escolha bem calibrada para a fórmula pitagórica aplicada ao baseball moderno.

## Limitações

Este projeto usa dados agregados por time-temporada. Ele não modela jogo a jogo.

Portanto, não incorpora diretamente:

- força dos adversários;
- calendário;
- efeitos de estádio;
- mudanças de regra;
- bullpen;
- distribuição inning a inning;
- jogos de interleague;
- diferenças estruturais entre eras.

Além disso, o ajuste não prova que `1.83` é o valor verdadeiro ou universal. Ele apenas mostra que esse valor reduz o erro histórico em comparação com o expoente original `2.00`.

## Referências

- [Baseball Reference Faqs](https://www.sports-reference.com/blog/baseball-reference-faqs/)

- [Pythagoras Explained](https://thegamedesigner.blogspot.com/2012/05/pythagoras-explained.html)

- [Revisiting the Pythagorean Theorem](https://www.baseballprospectus.com/news/article/342/revisiting-the-pythagorean-theorem-putting-bill-james-pythagorean-theorem-to-the-test/)

- [Baseball Databank](https://github.com/cbwinslow/baseballdatabank)
