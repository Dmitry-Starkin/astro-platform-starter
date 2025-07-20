import React, { useState, useEffect } from 'react';

interface Note {
  id: string;
  title: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

const NotesApp: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Загрузка заметок из localStorage
  useEffect(() => {
    const savedNotes = localStorage.getItem('notes');
    if (savedNotes) {
      try {
        const parsed = JSON.parse(savedNotes);
        setNotes(parsed.map((note: any) => ({
          ...note,
          createdAt: new Date(note.createdAt),
          updatedAt: new Date(note.updatedAt)
        })));
      } catch (error) {
        console.error('Ошибка при загрузке заметок:', error);
      }
    }
  }, []);

  // Сохранение заметок в localStorage
  useEffect(() => {
    localStorage.setItem('notes', JSON.stringify(notes));
  }, [notes]);

  const createNote = () => {
    const newNote: Note = {
      id: Date.now().toString(),
      title: 'Новая заметка',
      content: '',
      createdAt: new Date(),
      updatedAt: new Date()
    };
    setNotes([newNote, ...notes]);
    setSelectedNote(newNote);
    setIsCreating(true);
  };

  const updateNote = (id: string, updates: Partial<Note>) => {
    setNotes(notes.map(note =>
      note.id === id
        ? { ...note, ...updates, updatedAt: new Date() }
        : note
    ));
    if (selectedNote && selectedNote.id === id) {
      setSelectedNote({ ...selectedNote, ...updates, updatedAt: new Date() });
    }
  };

  const deleteNote = (id: string) => {
    setNotes(notes.filter(note => note.id !== id));
    if (selectedNote && selectedNote.id === id) {
      setSelectedNote(null);
    }
  };

  const filteredNotes = notes.filter(note =>
    note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    note.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto">
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Боковая панель со списком заметок */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex gap-3 mb-6">
              <button
                onClick={createNote}
                className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors duration-200 font-medium"
              >
                + Новая заметка
              </button>
            </div>

            <div className="mb-4">
              <input
                type="text"
                placeholder="Поиск заметок..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredNotes.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  {notes.length === 0 ? 'Нет заметок. Создайте первую!' : 'Заметки не найдены'}
                </div>
              ) : (
                filteredNotes.map((note) => (
                  <div
                    key={note.id}
                    onClick={() => setSelectedNote(note)}
                    className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                      selectedNote?.id === note.id
                        ? 'bg-green-100 border-green-300'
                        : 'bg-gray-50 hover:bg-gray-100 border-transparent'
                    } border`}
                  >
                    <h4 className="font-semibold text-gray-800 truncate">{note.title}</h4>
                    <p className="text-sm text-gray-600 truncate mt-1">
                      {note.content || 'Пустая заметка'}
                    </p>
                    <div className="text-xs text-gray-400 mt-2">
                      {note.updatedAt.toLocaleDateString('ru-RU')}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Основная область редактирования */}
        <div className="lg:col-span-2">
          {selectedNote ? (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <input
                  type="text"
                  value={selectedNote.title}
                  onChange={(e) => updateNote(selectedNote.id, { title: e.target.value })}
                  className="text-2xl font-bold text-gray-800 bg-transparent border-none outline-none flex-1"
                  placeholder="Заголовок заметки"
                />
                <button
                  onClick={() => deleteNote(selectedNote.id)}
                  className="ml-4 px-3 py-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors duration-200"
                >
                  🗑️ Удалить
                </button>
              </div>

              <div className="mb-4">
                <div className="text-sm text-gray-500">
                  Создано: {selectedNote.createdAt.toLocaleString('ru-RU')}
                  {selectedNote.updatedAt.getTime() !== selectedNote.createdAt.getTime() && (
                    <span className="ml-4">
                      Изменено: {selectedNote.updatedAt.toLocaleString('ru-RU')}
                    </span>
                  )}
                </div>
              </div>

              <textarea
                value={selectedNote.content}
                onChange={(e) => updateNote(selectedNote.id, { content: e.target.value })}
                placeholder="Начните писать вашу заметку..."
                className="w-full h-96 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
              />

              <div className="mt-4 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  Символов: {selectedNote.content.length}
                </div>
                <div className="text-xs text-gray-400">
                  Автосохранение включено
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-lg p-6 h-96 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <div className="text-6xl mb-4">📝</div>
                <h3 className="text-xl font-semibold mb-2">Выберите заметку</h3>
                <p>Выберите существующую заметку или создайте новую</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Статистика */}
      <div className="mt-8 bg-gradient-to-r from-green-50 to-teal-50 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-3xl font-bold text-green-600">{notes.length}</div>
            <div className="text-gray-600">Всего заметок</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-teal-600">
              {notes.reduce((total, note) => total + note.content.length, 0)}
            </div>
            <div className="text-gray-600">Символов написано</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600">
              {notes.filter(note => note.content.length > 0).length}
            </div>
            <div className="text-gray-600">Заполненных заметок</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotesApp;