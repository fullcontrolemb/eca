const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const port = 3000;

const db = new sqlite3.Database('./KJA.sqlite', err => {
  if (err) console.error('Erro ao abrir banco:', err.message);
  else console.log('Conectado ao banco KJA.sqlite');
});

app.use(express.static('public'));

app.get('/api/books', (req, res) => {
  // Esta consulta tenta descobrir o nome da tabela automaticamente
  const query = 'SELECT id, name FROM books ORDER BY id';
  db.all(query, [], (err, rows) => {
    if (err) {
      // Se falhar como 'books', tenta como 'book'
      db.all('SELECT id, name FROM book ORDER BY id', [], (err2, rows2) => {
        if (err2)
          return res.status(500).json({ error: 'Tabela não encontrada' });
        res.json(rows2);
      });
    } else {
      res.json(rows);
    }
  });
});

app.get('/api/chapters/:bookId', (req, res) => {
  const bookId = req.params.bookId;
  db.get(
    'SELECT MAX(chapter) as total FROM verses WHERE book_id = ?',
    [bookId],
    (err, row) => {
      if (err || !row || !row.total) {
        db.get(
          'SELECT MAX(chapter) as total FROM verse WHERE book_id = ?',
          [bookId],
          (err2, row2) => {
            res.json({ total_chapters: row2 ? row2.total : 0 });
          }
        );
      } else {
        res.json({ total_chapters: row.total });
      }
    }
  );
});

app.listen(port, () => {
  console.log(`--- SERVIDOR ATIVO EM http://localhost:${port} ---`);
});
// Rota para buscar os versículos de um capítulo específico
app.get('/api/verses/:bookId/:chapter', (req, res) => {
  const { bookId, chapter } = req.params;
  // Tenta buscar na tabela 'verses' ou 'verse'
  const sql =
    'SELECT verse, text FROM verses WHERE book_id = ? AND chapter = ? ORDER BY verse';

  db.all(sql, [bookId, chapter], (err, rows) => {
    if (err || rows.length === 0) {
      db.all(
        'SELECT verse, text FROM verse WHERE book_id = ? AND chapter = ? ORDER BY verse',
        [bookId, chapter],
        (err2, rows2) => {
          res.json(rows2 || []);
        }
      );
    } else {
      res.json(rows);
    }
  });
});
