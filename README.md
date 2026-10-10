# Salas do ICEx

Site que mostra, em tempo real (horário de Brasília), quais salas estão livres e qual aula está acontecendo em cada uma. Tudo sai do PDF da grade do semestre.

```
salas-icex/
├── index.html        site pronto (gerado, é o que o GitHub publica)
├── modelo.html       layout do site (o gerar.py preenche com os dados)
├── gerar.py          lê o PDF e cria o index.html
├── plantas/          imagens das plantas (1.jpg, 2.jpg, 3.jpg)
├── requirements.txt  biblioteca de Python necessária
└── .gitignore        evita subir o PDF da grade
```

---

## Parte 1: publicar no GitHub (só na primeira vez)

Não precisa instalar o Git. Dá para fazer tudo pelo navegador.

1. **Crie uma conta** em https://github.com (grátis).
2. Clique em **+** (canto superior direito) → **New repository**.
   - Repository name: `salas-icex`
   - Marque **Public** (o GitHub Pages grátis exige repositório público)
   - Não marque nenhuma opção de README, .gitignore ou licença
   - Clique em **Create repository**
3. Na página do repositório vazio, clique em **uploading an existing file**.
4. Abra a pasta `salas-icex` no seu computador, selecione **tudo que está dentro dela** (`index.html`, `modelo.html`, `gerar.py`, `plantas`, `README.md`, `requirements.txt`, `.gitignore`) e arraste para a página. Arrastar a pasta `plantas` mantém as imagens dentro dela.
   - Se o `.gitignore` não aparecer na sua pasta, é porque o sistema esconde arquivos que começam com ponto. Pode deixar de fora.
5. Role a página, escreva uma mensagem (ex.: `Primeira versão`) e clique em **Commit changes**.
6. Vá em **Settings** → **Pages** (menu da esquerda).
   - Em **Build and deployment**, escolha **Deploy from a branch**
   - Branch: `main` e pasta `/ (root)` → **Save**
7. Espere 1 a 2 minutos e atualize a página. Aparece o link do site:
   `https://SEU-USUARIO.github.io/salas-icex/`

Esse link é público: qualquer pessoa com ele acessa, sem login.

### Alternativa pelo terminal (se você já usa Git)

```bash
cd salas-icex
git init
git add .
git commit -m "Primeira versão"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/salas-icex.git
git push -u origin main
```

Depois ative o Pages como no passo 6.

---

## Parte 2: atualizar todo semestre

Você só precisa trocar o PDF e rodar um comando. O layout não muda.

**Uma vez só, no seu computador:**
- Instale o Python 3 (https://www.python.org/downloads/). No Windows, marque **Add Python to PATH**.
- Dentro da pasta do projeto, rode: `pip install -r requirements.txt`

**Todo semestre:**
1. Baixe o PDF novo da grade e salve na pasta do projeto como `grade.pdf`.
2. Rode (troque pelo semestre atual):
   ```bash
   python gerar.py grade.pdf --semestre 2027/1
   ```
3. Leia o que o script imprimiu:
   - `Pronto: N horários, N salas...` significa que deu certo.
   - `Atenção: locais que o script não reconheceu` lista salas com nome novo. Elas aparecem na seção "Outros locais" e funcionam, só ficam fora dos grupos por andar. Para agrupá-las, ajuste a função `atoms()` no `gerar.py`.
4. Abra o `index.html` no navegador e confira se as salas e os horários parecem certos.
5. No GitHub, abra o repositório → **Add file** → **Upload files** → arraste o novo `index.html` (e a pasta `plantas`, se as plantas mudaram) → **Commit changes**.
6. Em cerca de 1 minuto o site atualiza no mesmo link.

### Se o PDF vier em outro formato

O script espera a tabela com as colunas **Matéria, Código, Turma, Início, Fim, Dias, Sala**, como no PDF atual. Se a faculdade mudar o formato e o script disser que não encontrou nenhuma aula, mande o PDF novo para o Claude pedindo para ajustar o `gerar.py`.

---

## Limites

- A página não conhece feriados, reposições nem trocas de sala.
- Uma sala livre pode estar fechada. Confirme na portaria.
- O horário mostrado é sempre o de Brasília, independente do fuso do aparelho.
