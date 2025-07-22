
#!/data/data/com.termux/files/usr/bin/bash

#Version 1.0v beta

MUSIC_DIR="$HOME/storage/music"

clear
echo -e "\e[1;32m🎧 Termux Music Player by DesEffect\e[0m"
echo "Музыка из: $MUSIC_DIR"
echo

# Проверка папки
if [ ! -d "$MUSIC_DIR" ]; then
  echo "❌ Папка не найдена: $MUSIC_DIR"
  exit 1
fi

# Получить список треков
files=("$MUSIC_DIR"/*.mp3 "$MUSIC_DIR"/*.wav)
if [ ${#files[@]} -eq 0 ]; then
  echo "❌ Музыка не найдена!"
  exit 1
fi

# 🔁 Бесконечный цикл — до выхода
while true; do
  clear
  echo -e "\e[1;36m🎶 Список треков:\e[0m"
  for i in "${!files[@]}"; do
    echo "[$i] $(basename "${files[$i]}")"
  done
  echo "[q] Выйти"
  echo

  # Выбор трека
  read -p "🎵 Выбери номер трека: " choice

  if [[ "$choice" == "q" ]]; then
    echo "👋 Пока, Рито!"
    break
  elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -lt "${#files[@]}" ]; then
    clear
    echo -e "\e[1;34m▶ Играет: $(basename "${files[$choice]}")\e[0m"
    mpv --no-video "${files[$choice]}"
    echo -e "\n⏭ Трек закончен. Хочешь другой? 🎵"
    read -p "Нажми Enter для продолжения..."
  else
    echo "❌ Неверный выбор"
    sleep 1
  fi
done

#welcom.sh © 2025 by hexhamder распространяется по лицензии CC BY-ND 4.0.
#Чтобы ознакомиться с условиями этой лицензии, посетите сайт https://creativecommons.org/licenses/by-nd/4.0/