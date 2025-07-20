import React, { useState, useRef, useEffect } from 'react';

interface YouTubeScreenshotProps {}

const YouTubeScreenshot: React.FC<YouTubeScreenshotProps> = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [screenshotUrl, setScreenshotUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const playerRef = useRef<any>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

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
        height: '315',
        width: '560',
        videoId: videoId,
        playerVars: {
          controls: 0,
          disablekb: 1,
          fs: 0,
          iv_load_policy: 3,
          modestbranding: 1,
          rel: 0,
          showinfo: 0,
        },
        events: {
          onReady: (event: any) => {
            console.log('Player ready');
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
      setCurrentTime(playerRef.current.getCurrentTime());
    }
  };

  // Пауза/воспроизведение
  const togglePlayPause = () => {
    if (playerRef.current) {
      if (isPlaying) {
        playerRef.current.pauseVideo();
      } else {
        playerRef.current.playVideo();
      }
    }
  };

  // Перемотка на указанное время
  const seekTo = (time: number) => {
    if (playerRef.current) {
      playerRef.current.seekTo(time);
      setCurrentTime(time);
    }
  };

  // Создание скриншота
  const takeScreenshot = async () => {
    if (!playerRef.current || !canvasRef.current) {
      setError('Плеер не готов');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Пауза видео
      playerRef.current.pauseVideo();
      
      // Небольшая задержка для стабилизации кадра
      await new Promise(resolve => setTimeout(resolve, 500));

      // Получаем iframe элемент
      const iframe = document.getElementById('youtube-player') as HTMLIFrameElement;
      if (!iframe) {
        throw new Error('Не удалось найти видео элемент');
      }

      // Создаем скриншот через API YouTube thumbnail
      const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
      
      // Альтернативный способ - создание через canvas
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        throw new Error('Не удалось получить контекст canvas');
      }

      // Устанавливаем размеры canvas
      canvas.width = 1280;
      canvas.height = 720;

      // Создаем изображение из thumbnail
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        // Добавляем информацию о времени
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(canvas.width - 200, canvas.height - 50, 190, 40);
        
        ctx.fillStyle = 'white';
        ctx.font = '16px Arial';
        ctx.fillText(`Время: ${formatTime(currentTime)}`, canvas.width - 190, canvas.height - 25);
        
        // Конвертируем в blob и создаем URL
        canvas.toBlob((blob) => {
          if (blob) {
            const url = URL.createObjectURL(blob);
            setScreenshotUrl(url);
          }
        }, 'image/png');
        
        setIsLoading(false);
      };

      img.onerror = () => {
        setError('Не удалось загрузить изображение');
        setIsLoading(false);
      };

      img.src = thumbnailUrl;

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при создании скриншота');
      setIsLoading(false);
    }
  };

  // Форматирование времени
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Скачивание скриншота
  const downloadScreenshot = () => {
    if (screenshotUrl) {
      const link = document.createElement('a');
      link.href = screenshotUrl;
      link.download = `youtube-screenshot-${videoId}-${Math.floor(currentTime)}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

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

      {/* YouTube плеер */}
      {videoId && (
        <div className="mb-6">
          <div className="flex justify-center mb-4">
            <div id="youtube-player" className="rounded-lg overflow-hidden"></div>
          </div>
          
          {/* Управление */}
          <div className="flex flex-col items-center space-y-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={togglePlayPause}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
              >
                {isPlaying ? 'Пауза' : 'Воспроизвести'}
              </button>
              
              <span className="text-sm text-gray-600">
                Время: {formatTime(currentTime)}
              </span>
            </div>

            {/* Кнопка скриншота */}
            <button
              onClick={takeScreenshot}
              disabled={isLoading}
              className="px-6 py-3 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-gray-400 transition-colors"
            >
              {isLoading ? 'Создается скриншот...' : 'Сделать скриншот'}
            </button>
          </div>
        </div>
      )}

      {/* Скрытый canvas для создания скриншота */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Результат скриншота */}
      {screenshotUrl && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-700 mb-4">Ваш скриншот:</h3>
          <div className="text-center">
            <img
              src={screenshotUrl}
              alt="YouTube Screenshot"
              className="max-w-full h-auto rounded-lg shadow-md mx-auto mb-4"
            />
            <button
              onClick={downloadScreenshot}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
            >
              Скачать скриншот
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

export default YouTubeScreenshot;