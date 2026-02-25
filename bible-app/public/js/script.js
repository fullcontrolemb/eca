const bookSelect = document.getElementById('book_list');
const chapterSelect = document.getElementById('chapter_list');
// Vamos criar um lugar para mostrar o texto (garanta que tem um <div id="bible_text"> no seu HTML)
const bibleText =
  document.getElementById('bible_text') ||
  document.body.appendChild(document.createElement('div'));
if (!bibleText.id) bibleText.id = 'bible_text';

// 1. Carrega os livros
fetch('/api/books')
  .then(res => res.json())
  .then(books => {
    bookSelect.innerHTML = '<option value="">Selecione um Livro</option>';
    books.forEach(book => {
      const option = document.createElement('option');
      option.value = book.id;
      option.textContent = book.name;
      bookSelect.appendChild(option);
    });
  });

// 2. Carrega os capítulos
bookSelect.addEventListener('change', () => {
  const bookId = bookSelect.value;
  chapterSelect.innerHTML = '<option value="">...</option>';
  bibleText.innerHTML = ''; // Limpa o texto ao trocar de livro

  if (!bookId) return;

  fetch(`/api/chapters/${bookId}`)
    .then(res => res.json())
    .then(data => {
      chapterSelect.innerHTML = '<option value="">Capítulo</option>';
      for (let i = 1; i <= data.total_chapters; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `Capítulo ${i}`;
        chapterSelect.appendChild(option);
      }
    });
});

// 3. NOVIDADE: Carrega os versículos quando selecionar o capítulo
chapterSelect.addEventListener('change', () => {
  const bookId = bookSelect.value;
  const chapter = chapterSelect.value;

  if (!bookId || !chapter) return;

  bibleText.innerHTML = '<p>Carregando versículos...</p>';

  fetch(`/api/verses/${bookId}/${chapter}`)
    .then(res => res.json())
    .then(verses => {
      bibleText.innerHTML = `<h2>Capítulo ${chapter}</h2>`;
      verses.forEach(v => {
        const p = document.createElement('p');
        p.innerHTML = `<strong>${v.verse}.</strong> ${v.text}`;
        bibleText.appendChild(p);
      });
    })
    .catch(err => {
      bibleText.innerHTML = '<p>Erro ao carregar versículos.</p>';
      console.error(err);
    });
});
