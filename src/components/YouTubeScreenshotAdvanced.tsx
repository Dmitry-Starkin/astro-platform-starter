import React, { useState, useRef, useEffect } from 'react';

interface YouTubeScreenshotAdvancedProps {}

const YouTubeScreenshotAdvanced: React.FC<YouTubeScreenshotAdvancedProps> = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [screenshotUrl, setScreenshotUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [quality, setQuality] = useState('maxresdefault');
  
  const playerRef = useRef<any>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Функция для извлечения ID видео из URL YouTube
  const extractVideoId = (url: string): string | null => {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
  };

  // Обработка изменения URL
  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setVideoUrl(url);
    setError('');
    setScreenshotUrl('');
    
    if (url) {
      const id = extractVideoId(url);
      if (id) {
        setVideoId(id);
      } else {
        setError('Неверная ссылка на YouTube видео');
      }
    } else {
      setVideoId('');
    }
  };

  // Загрузка YouTube API
  useEffect(() => {
    if (!window.YT) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);

      window.onYouTubeIframeAPIReady = () => {
        console.log('YouTube API loaded');
      };
    }
  }, []);

  // Создание YouTube плеера
  useEffect(() => {
    if (videoId && window.YT && window.YT.Player) {
      if (playerRef.current) {
        playerRef.current.destroy();
      }

      playerRef.current = new window.YT.Player('youtube-player', {
        height: '0',
        width: '0',
        videoId: videoId,
        playerVars: {
          controls: 0,
          disablekb: 1,
          fs: 0,
          iv_load_policy: 3,
          modestbranding: 1,
          rel: 0,
          showinfo: 0,
          autoplay: 0,
        },
        events: {
          onReady: (event: any) => {
            console.log('Player ready');
            setDuration(event.target.getDuration());
          },
          onStateChange: (event: any) => {
            if (event.data === window.YT.PlayerState.PLAYING) {
              setIsPlaying(true);
              updateCurrentTime();
            } else {
              setIsPlaying(false);
            }
          },
        },
      });
    }
  }, [videoId]);

  // Обновление текущего времени
  const updateCurrentTime = () => {
    if (playerRef.current && playerRef.current.getCurrentTime) {
      const time = playerRef.current.getCurrentTime();
      setCurrentTime(time);
      
      if (isPlaying) {
        setTimeout(updateCurrentTime, 100);
      }
    }
  };

  // Создание скриншота из thumbnail с временной меткой
  const createThumbnailScreenshot = async (timeInSeconds: number) => {
    setIsLoading(true);
    setError('');

    try {
      const canvas = canvasRef.current;
      if (!canvas) {
        throw new Error('Canvas не найден');
      }

      const ctx = canvas.getContext('2d');
      if (!ctx) {
        throw new Error('Не удалось получить контекст canvas');
      }

      // Устанавливаем размеры canvas
      canvas.width = 1280;
      canvas.height = 720;

      // Получаем thumbnail высокого качества
      const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/${quality}.jpg`;
      
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        // Очищаем canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Рисуем изображение
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        // Добавляем полупрозрачный overlay для информации
        const overlayHeight = 60;
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(0, canvas.height - overlayHeight, canvas.width, overlayHeight);
        
        // Добавляем информацию о времени
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(`⏱️ ${formatTime(timeInSeconds)}`, 20, canvas.height - 30);
        
        // Добавляем информацию о видео
        ctx.font = '16px Arial';
        ctx.textAlign = 'right';
        ctx.fillText(`🎬 YouTube Video ID: ${videoId}`, canvas.width - 20, canvas.height - 30);
        
        // Добавляем дату создания скриншота
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        const now = new Date();
        ctx.fillText(
          `📅 ${now.toLocaleDateString('ru-RU')} ${now.toLocaleTimeString('ru-RU')}`,
          canvas.width / 2,
          canvas.height - 10
        );
        
        // Конвертируем в blob и создаем URL
        canvas.toBlob((blob) => {
          if (blob) {
            const url = URL.createObjectURL(blob);
            setScreenshotUrl(url);
          }
        }, 'image/png', 1.0);
        
        setIsLoading(false);
      };

      img.onerror = () => {
        // Пробуем альтернативное качество
        if (quality === 'maxresdefault') {
          setQuality('hqdefault');
          img.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
        } else {
          setError('Не удалось загрузить изображение видео');
          setIsLoading(false);
        }
      };

      img.src = thumbnailUrl;

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при создании скриншота');
      setIsLoading(false);
    }
  };

  // Создание скриншота текущего кадра
  const takeCurrentScreenshot = () => {
    createThumbnailScreenshot(currentTime);
  };

  // Создание скриншота на указанном времени
  const takeTimedScreenshot = (time: number) => {
    createThumbnailScreenshot(time);
    if (playerRef.current) {
      playerRef.current.seekTo(time);
      setCurrentTime(time);
    }
  };

  // Форматирование времени
  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Скачивание скриншота
  const downloadScreenshot = () => {
    if (screenshotUrl) {
      const link = document.createElement('a');
      link.href = screenshotUrl;
      link.download = `youtube-screenshot-${videoId}-${Math.floor(currentTime)}s.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // Предустановленные моменты для скриншотов
  const presetTimes = [
    { label: 'Начало', time: 0 },
    { label: '25%', time: duration * 0.25 },
    { label: '50%', time: duration * 0.5 },
    { label: '75%', time: duration * 0.75 },
  ];

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
      {/* Ввод URL */}
      <div className="mb-6">
        <label htmlFor="video-url" className="block text-sm font-medium text-gray-700 mb-2">
          Ссылка на YouTube видео:
        </label>
        <input
          type="url"
          id="video-url"
          value={videoUrl}
          onChange={handleUrlChange}
          placeholder="https://www.youtube.com/watch?v=..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}
      </div>

      {/* Скрытый YouTube плеер */}
      {videoId && (
        <div style={{ display: 'none' }}>
          <div id="youtube-player"></div>
        </div>
      )}

      {/* Информация о видео */}
      {videoId && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-medium text-gray-700 mb-2">📹 Информация о видео</h3>
          <p className="text-sm text-gray-600 mb-2">ID видео: {videoId}</p>
          <p className="text-sm text-gray-600 mb-4">
            Длительность: {duration > 0 ? formatTime(duration) : 'Загружается...'}
          </p>
          
          {/* Предварительный просмотр */}
          <div className="mb-4">
            <img
              src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
              alt="Video thumbnail"
              className="w-48 h-auto rounded-lg shadow-sm"
            />
          </div>

          {/* Управление качеством */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Качество скриншота:
            </label>
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="maxresdefault">Максимальное (1280x720)</option>
              <option value="sddefault">Стандартное (640x480)</option>
              <option value="hqdefault">Высокое (480x360)</option>
              <option value="mqdefault">Среднее (320x180)</option>
            </select>
          </div>

          {/* Быстрые скриншоты */}
          {duration > 0 && (
            <div className="mb-4">
              <h4 className="text-md font-medium text-gray-700 mb-2">⚡ Быстрые скриншоты:</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {presetTimes.map((preset, index) => (
                  <button
                    key={index}
                    onClick={() => takeTimedScreenshot(preset.time)}
                    disabled={isLoading}
                    className="px-3 py-2 bg-indigo-500 text-white text-sm rounded-md hover:bg-indigo-600 disabled:bg-gray-400 transition-colors"
                  >
                    {preset.label}
                    <br />
                    <span className="text-xs opacity-75">
                      {formatTime(preset.time)}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Ползунок времени */}
          {duration > 0 && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🕐 Выберите время для скриншота: {formatTime(currentTime)}
              </label>
              <input
                type="range"
                min="0"
                max={duration}
                step="1"
                value={currentTime}
                onChange={(e) => {
                  const time = parseInt(e.target.value);
                  setCurrentTime(time);
                  if (playerRef.current) {
                    playerRef.current.seekTo(time);
                  }
                }}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          )}

          {/* Кнопка скриншота */}
          <div className="text-center">
            <button
              onClick={takeCurrentScreenshot}
              disabled={isLoading}
              className="px-6 py-3 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-gray-400 transition-colors"
            >
              {isLoading ? (
                <>
                  <span className="inline-block animate-spin mr-2">⏳</span>
                  Создается скриншот...
                </>
              ) : (
                <>
                  📸 Сделать скриншот в {formatTime(currentTime)}
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Скрытый canvas для создания скриншота */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Результат скриншота */}
      {screenshotUrl && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-700 mb-4">🖼️ Ваш скриншот:</h3>
          <div className="text-center">
            <div className="inline-block p-4 bg-gray-50 rounded-lg">
              <img
                src={screenshotUrl}
                alt="YouTube Screenshot"
                className="max-w-full h-auto rounded-lg shadow-md mb-4"
                style={{ maxHeight: '400px' }}
              />
              <div className="flex flex-col sm:flex-row gap-2 justify-center">
                <button
                  onClick={downloadScreenshot}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
                >
                  💾 Скачать PNG
                </button>
                <button
                  onClick={() => {
                    if (screenshotUrl) {
                      navigator.clipboard.write([
                        new ClipboardItem({
                          'image/png': fetch(screenshotUrl).then(r => r.blob())
                        })
                      ]).then(() => {
                        alert('Скриншот скопирован в буфер обмена!');
                      }).catch(() => {
                        alert('Не удалось скопировать в буфер обмена');
                      });
                    }
                  }}
                  className="px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors"
                >
                  📋 Копировать
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Инструкции */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-lg font-medium text-blue-800 mb-2">💡 Как использовать:</h4>
        <ol className="list-decimal list-inside text-sm text-blue-700 space-y-1">
          <li>Вставьте ссылку на YouTube видео в поле выше</li>
          <li>Выберите качество скриншота</li>
          <li>Используйте ползунок или кнопки быстрого доступа для выбора времени</li>
          <li>Нажмите "Сделать скриншот" для создания изображения</li>
          <li>Скачайте или скопируйте готовый скриншот</li>
        </ol>
        <p className="text-xs text-blue-600 mt-2">
          ⚠️ Примечание: Скриншоты создаются на основе thumbnail изображений YouTube, 
          поэтому точность по времени может варьироваться.
        </p>
      </div>
    </div>
  );
};

declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

export default YouTubeScreenshotAdvanced;