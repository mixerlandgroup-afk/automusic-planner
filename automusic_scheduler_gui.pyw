from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "AutoMusic Planner"
TASK_PREFIX = "AutoMusic_Planner"
POWER_SHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")

LANGUAGE_OPTIONS = [
    ("en", "English"),
    ("ru", "Русский"),
    ("es", "Español"),
    ("pt_BR", "Português (Brasil)"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("ja", "日本語"),
    ("zh_CN", "简体中文"),
    ("ar", "العربية"),
    ("hi", "हिन्दी"),
]
LANGUAGE_NAMES = dict(LANGUAGE_OPTIONS)

DAY_CODES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
DAY_PS_NAMES = {
    "MON": "Monday",
    "TUE": "Tuesday",
    "WED": "Wednesday",
    "THU": "Thursday",
    "FRI": "Friday",
    "SAT": "Saturday",
    "SUN": "Sunday",
}

BASE_EN = {
    "language": "Language",
    "ready": "Ready.",
    "main_paths": "Player and playlists",
    "preferred_player": "Player (.exe)",
    "preferred_player_placeholder": "Select the path to your player",
    "playlist_folder": "Playlist folder",
    "playlist_folder_placeholder": "Select the folder where playlists will be stored",
    "track_count": "Tracks per playlist",
    "playlist_history": "Saved playlists",
    "auto_cleanup_history": "Delete old saved playlists automatically",
    "keep_for_days": "Keep for",
    "days": "days",
    "saved_playlists_button": "Saved playlists…",
    "music_folders": "Music folders",
    "music_folders_placeholder": "Your music folders will appear here. Click “Add folder” so the app knows where to find your music.",
    "browse": "Browse",
    "add_folder": "Add folder",
    "remove_selected_folder": "Remove selected",
    "schedule": "Schedule",
    "schedule_help": "Choose when music should start automatically. You can leave this section empty.",
    "same_every_day": "Same time every day",
    "per_day": "Different times by day",
    "same_schedule_group": "Daily schedule",
    "time_start": "Start time",
    "same_time_placeholder": "Add one or more times for every day.",
    "per_day_help": "Set different times for each day if needed.",
    "per_day_placeholder": "Add one or more times for this day.",
    "time_entry_placeholder": "HH:MM (09:00)",
    "add": "Add",
    "remove_selected": "Remove selected",
    "save_settings": "Save settings",
    "play_now": "▶ Play music now",
    "footer_help": "Save settings to update the launch script and automatic schedule. Leave the schedule empty if you only want manual playback.",
    "status_saved_with_schedule": "Settings saved. Schedule updated. Tasks created: {count}",
    "status_saved_no_schedule": "Settings saved. No schedule is set — use “Play music now” for manual start.",
    "status_starting_music": "Music is starting.",
    "status_language_changed": "Language changed.",
    "status_opening_saved_playlist": "Opening saved playlist.",
    "warn_time_format": "Enter time in HH:MM format, for example 09:00 or 17:30.",
    "error_read_config": "Could not read the config. Default settings will be loaded.\n\n{error}",
    "error_invalid_time": "Invalid time in section “{label}”: {value}",
    "error_track_count_integer": "Track count must be a whole number.",
    "error_track_count_positive": "Track count must be greater than zero.",
    "error_history_days_integer": "History retention must be a whole number of days.",
    "error_history_days_positive": "History retention must be greater than zero.",
    "error_player_required": "Please choose the player (.exe).",
    "error_playlist_dir_required": "Please choose the playlist folder.",
    "error_music_folder_required": "Please add at least one music folder.",
    "error_select_saved_playlist": "Select a saved playlist first.",
    "error_run_now": "Could not start music.\n\n{error}",
    "error_unknown": "Unknown error",
    "window_only_windows": "This utility is designed for Windows.",
    "dialog_choose_player": "Choose the player file (.exe)",
    "dialog_choose_playlist_folder": "Choose the playlist folder",
    "dialog_choose_music_folder": "Choose a music folder",
    "executables": "Executable files",
    "all_files": "All files",
    "history_window_title": "Saved playlists",
    "saved_playlists_placeholder": "Saved playlists will appear here after playback.",
    "play_selected": "Play",
    "open_folder": "Open folder",
    "delete": "Delete",
    "confirm_delete_playlist_title": "Delete saved playlist",
    "confirm_delete_playlist": "Delete the selected saved playlist?\n\n{name}",
    "day_MON": "Monday",
    "day_TUE": "Tuesday",
    "day_WED": "Wednesday",
    "day_THU": "Thursday",
    "day_FRI": "Friday",
    "day_SAT": "Saturday",
    "day_SUN": "Sunday",
}

TRANSLATIONS = {
    "en": BASE_EN,
    "ru": {
        **BASE_EN,
        "language": "Язык",
        "ready": "Готово.",
        "main_paths": "Плеер и плейлисты",
        "preferred_player": "Плеер (.exe)",
        "preferred_player_placeholder": "Укажите путь к плееру",
        "playlist_folder": "Папка для плейлистов",
        "playlist_folder_placeholder": "Выберите папку, где будут храниться плейлисты",
        "track_count": "Треков в плейлисте",
        "playlist_history": "Сохранённые плейлисты",
        "auto_cleanup_history": "Автоматически удалять старые сохранённые плейлисты",
        "keep_for_days": "Хранить",
        "days": "дней",
        "saved_playlists_button": "Сохранённые плейлисты…",
        "music_folders": "Папки с музыкой",
        "music_folders_placeholder": "Здесь отобразятся папки с вашей музыкой. Нажмите «Добавить папку», чтобы программа знала, где искать музыку.",
        "browse": "Обзор",
        "add_folder": "Добавить папку",
        "remove_selected_folder": "Удалить выбранное",
        "schedule": "Расписание",
        "schedule_help": "Выберите, когда музыка должна запускаться автоматически. Этот раздел можно оставить пустым.",
        "same_every_day": "Одинаковое время каждый день",
        "per_day": "Разное время по дням",
        "same_schedule_group": "Общее расписание",
        "time_start": "Время запуска",
        "same_time_placeholder": "Добавьте одно или несколько значений для всех дней.",
        "per_day_help": "Задайте разное время по дням, если нужно.",
        "per_day_placeholder": "Добавьте одно или несколько значений для этого дня.",
        "time_entry_placeholder": "ЧЧ:ММ (09:00)",
        "add": "Добавить",
        "remove_selected": "Удалить выбранное",
        "save_settings": "Сохранить настройки",
        "play_now": "▶ Включить музыку сейчас",
        "footer_help": "Сохраните настройки, чтобы обновить скрипт запуска и автоматическое расписание. Оставьте расписание пустым, если нужен только ручной запуск.",
        "status_saved_with_schedule": "Настройки сохранены. Расписание обновлено. Создано задач: {count}",
        "status_saved_no_schedule": "Настройки сохранены. Расписание не задано — используйте «Включить музыку сейчас» для ручного запуска.",
        "status_starting_music": "Музыка запускается.",
        "status_language_changed": "Язык интерфейса изменён.",
        "status_opening_saved_playlist": "Открывается сохранённый плейлист.",
        "warn_time_format": "Укажите время в формате ЧЧ:ММ, например 09:00 или 17:30.",
        "error_read_config": "Не удалось прочитать config. Будут загружены настройки по умолчанию.\n\n{error}",
        "error_invalid_time": "Некорректное время в разделе «{label}»: {value}",
        "error_track_count_integer": "Количество треков должно быть целым числом.",
        "error_track_count_positive": "Количество треков должно быть больше нуля.",
        "error_history_days_integer": "Срок хранения должен быть целым числом дней.",
        "error_history_days_positive": "Срок хранения должен быть больше нуля.",
        "error_player_required": "Укажите путь к плееру (.exe).",
        "error_playlist_dir_required": "Укажите папку для плейлистов.",
        "error_music_folder_required": "Добавьте хотя бы одну папку с музыкой.",
        "error_select_saved_playlist": "Сначала выберите сохранённый плейлист.",
        "error_run_now": "Не удалось запустить музыку.\n\n{error}",
        "error_unknown": "Неизвестная ошибка",
        "window_only_windows": "Эта утилита рассчитана на Windows.",
        "dialog_choose_player": "Выберите файл плеера (.exe)",
        "dialog_choose_playlist_folder": "Выберите папку для плейлистов",
        "dialog_choose_music_folder": "Выберите папку с музыкой",
        "executables": "Исполняемые файлы",
        "all_files": "Все файлы",
        "history_window_title": "Сохранённые плейлисты",
        "saved_playlists_placeholder": "Здесь появятся сохранённые плейлисты после запуска музыки.",
        "play_selected": "Воспроизвести",
        "open_folder": "Открыть папку",
        "delete": "Удалить",
        "confirm_delete_playlist_title": "Удаление сохранённого плейлиста",
        "confirm_delete_playlist": "Удалить выбранный сохранённый плейлист?\n\n{name}",
        "day_MON": "Понедельник",
        "day_TUE": "Вторник",
        "day_WED": "Среда",
        "day_THU": "Четверг",
        "day_FRI": "Пятница",
        "day_SAT": "Суббота",
        "day_SUN": "Воскресенье",
    },
    "es": {
        **BASE_EN,
        "language": "Idioma",
        "main_paths": "Reproductor y listas",
        "preferred_player": "Reproductor (.exe)",
        "preferred_player_placeholder": "Selecciona la ruta de tu reproductor",
        "playlist_folder": "Carpeta de listas",
        "playlist_folder_placeholder": "Selecciona la carpeta donde se guardarán las listas",
        "track_count": "Pistas por lista",
        "playlist_history": "Listas guardadas",
        "auto_cleanup_history": "Eliminar automáticamente las listas guardadas antiguas",
        "keep_for_days": "Conservar durante",
        "days": "días",
        "saved_playlists_button": "Listas guardadas…",
        "music_folders": "Carpetas de música",
        "music_folders_placeholder": "Tus carpetas de música aparecerán aquí. Haz clic en “Añadir carpeta” para que la app sepa dónde buscar tu música.",
        "browse": "Examinar",
        "add_folder": "Añadir carpeta",
        "remove_selected_folder": "Eliminar seleccionada",
        "schedule": "Horario",
        "schedule_help": "Elige cuándo debe iniciarse la música automáticamente. Puedes dejar esta sección vacía.",
        "same_every_day": "La misma hora todos los días",
        "per_day": "Horas diferentes por día",
        "same_schedule_group": "Horario diario",
        "time_start": "Hora de inicio",
        "same_time_placeholder": "Añade una o varias horas para todos los días.",
        "per_day_help": "Define horas distintas para cada día si lo necesitas.",
        "per_day_placeholder": "Añade una o varias horas para este día.",
        "add": "Añadir",
        "remove_selected": "Eliminar seleccionadas",
        "save_settings": "Guardar ajustes",
        "play_now": "▶ Reproducir música ahora",
        "footer_help": "Guarda los ajustes para actualizar el script de inicio y el horario automático. Deja el horario vacío si solo quieres reproducción manual.",
        "saved_playlists_placeholder": "Las listas guardadas aparecerán aquí después de la reproducción.",
        "play_selected": "Reproducir",
        "open_folder": "Abrir carpeta",
        "delete": "Eliminar",
        "day_MON": "Lunes", "day_TUE": "Martes", "day_WED": "Miércoles", "day_THU": "Jueves", "day_FRI": "Viernes", "day_SAT": "Sábado", "day_SUN": "Domingo",
    },
    "pt_BR": {
        **BASE_EN,
        "language": "Idioma",
        "main_paths": "Player e playlists",
        "preferred_player": "Player (.exe)",
        "preferred_player_placeholder": "Selecione o caminho do player",
        "playlist_folder": "Pasta de playlists",
        "playlist_folder_placeholder": "Selecione a pasta onde as playlists serão salvas",
        "track_count": "Faixas por playlist",
        "playlist_history": "Playlists salvas",
        "auto_cleanup_history": "Excluir automaticamente playlists salvas antigas",
        "keep_for_days": "Manter por",
        "days": "dias",
        "saved_playlists_button": "Playlists salvas…",
        "music_folders": "Pastas de música",
        "music_folders_placeholder": "Suas pastas de música aparecerão aqui. Clique em “Adicionar pasta” para que o app saiba onde procurar sua música.",
        "browse": "Procurar",
        "add_folder": "Adicionar pasta",
        "remove_selected_folder": "Remover selecionada",
        "schedule": "Agenda",
        "schedule_help": "Escolha quando a música deve iniciar automaticamente. Você pode deixar esta seção vazia.",
        "same_every_day": "Mesmo horário todos os dias",
        "per_day": "Horários diferentes por dia",
        "same_schedule_group": "Agenda diária",
        "time_start": "Hora de início",
        "same_time_placeholder": "Adicione um ou mais horários para todos os dias.",
        "per_day_help": "Defina horários diferentes para cada dia, se necessário.",
        "per_day_placeholder": "Adicione um ou mais horários para este dia.",
        "add": "Adicionar",
        "remove_selected": "Remover selecionado",
        "save_settings": "Salvar configurações",
        "play_now": "▶ Tocar música agora",
        "footer_help": "Salve as configurações para atualizar o script de inicialização e a agenda automática. Deixe a agenda vazia se quiser apenas reprodução manual.",
        "saved_playlists_placeholder": "As playlists salvas aparecerão aqui após a reprodução.",
        "play_selected": "Tocar",
        "open_folder": "Abrir pasta",
        "delete": "Excluir",
        "day_MON": "Segunda", "day_TUE": "Terça", "day_WED": "Quarta", "day_THU": "Quinta", "day_FRI": "Sexta", "day_SAT": "Sábado", "day_SUN": "Domingo",
    },
    "de": {
        **BASE_EN,
        "language": "Sprache",
        "main_paths": "Player und Playlists",
        "preferred_player": "Player (.exe)",
        "preferred_player_placeholder": "Pfad zu deinem Player auswählen",
        "playlist_folder": "Playlist-Ordner",
        "playlist_folder_placeholder": "Ordner auswählen, in dem Playlists gespeichert werden",
        "track_count": "Titel pro Playlist",
        "playlist_history": "Gespeicherte Playlists",
        "auto_cleanup_history": "Alte gespeicherte Playlists automatisch löschen",
        "keep_for_days": "Aufbewahren für",
        "days": "Tage",
        "saved_playlists_button": "Gespeicherte Playlists…",
        "music_folders": "Musikordner",
        "music_folders_placeholder": "Deine Musikordner erscheinen hier. Klicke auf „Ordner hinzufügen“, damit die App weiß, wo sie deine Musik findet.",
        "browse": "Durchsuchen",
        "add_folder": "Ordner hinzufügen",
        "remove_selected_folder": "Auswahl entfernen",
        "schedule": "Zeitplan",
        "schedule_help": "Wähle, wann Musik automatisch starten soll. Dieser Bereich kann leer bleiben.",
        "same_every_day": "Jeden Tag dieselbe Zeit",
        "per_day": "Unterschiedliche Zeiten pro Tag",
        "same_schedule_group": "Täglicher Zeitplan",
        "time_start": "Startzeit",
        "same_time_placeholder": "Eine oder mehrere Zeiten für jeden Tag hinzufügen.",
        "per_day_help": "Lege bei Bedarf unterschiedliche Zeiten pro Tag fest.",
        "per_day_placeholder": "Eine oder mehrere Zeiten für diesen Tag hinzufügen.",
        "add": "Hinzufügen",
        "remove_selected": "Auswahl entfernen",
        "save_settings": "Einstellungen speichern",
        "play_now": "▶ Musik jetzt abspielen",
        "footer_help": "Speichere die Einstellungen, um das Startskript und den automatischen Zeitplan zu aktualisieren. Lasse den Zeitplan leer, wenn du nur manuell abspielen möchtest.",
        "saved_playlists_placeholder": "Gespeicherte Playlists erscheinen hier nach der Wiedergabe.",
        "play_selected": "Abspielen",
        "open_folder": "Ordner öffnen",
        "delete": "Löschen",
        "day_MON": "Montag", "day_TUE": "Dienstag", "day_WED": "Mittwoch", "day_THU": "Donnerstag", "day_FRI": "Freitag", "day_SAT": "Samstag", "day_SUN": "Sonntag",
    },
    "fr": {
        **BASE_EN,
        "language": "Langue",
        "main_paths": "Lecteur et playlists",
        "preferred_player": "Lecteur (.exe)",
        "preferred_player_placeholder": "Sélectionnez le chemin de votre lecteur",
        "playlist_folder": "Dossier des playlists",
        "playlist_folder_placeholder": "Sélectionnez le dossier où les playlists seront enregistrées",
        "track_count": "Titres par playlist",
        "playlist_history": "Playlists enregistrées",
        "auto_cleanup_history": "Supprimer automatiquement les anciennes playlists enregistrées",
        "keep_for_days": "Conserver pendant",
        "days": "jours",
        "saved_playlists_button": "Playlists enregistrées…",
        "music_folders": "Dossiers de musique",
        "music_folders_placeholder": "Vos dossiers de musique apparaîtront ici. Cliquez sur « Ajouter un dossier » pour que l’application sache où trouver votre musique.",
        "browse": "Parcourir",
        "add_folder": "Ajouter un dossier",
        "remove_selected_folder": "Supprimer la sélection",
        "schedule": "Planification",
        "schedule_help": "Choisissez quand la musique doit démarrer automatiquement. Vous pouvez laisser cette section vide.",
        "same_every_day": "Même heure tous les jours",
        "per_day": "Heures différentes selon le jour",
        "same_schedule_group": "Planification quotidienne",
        "time_start": "Heure de démarrage",
        "same_time_placeholder": "Ajoutez une ou plusieurs heures pour tous les jours.",
        "per_day_help": "Définissez des heures différentes pour chaque jour si nécessaire.",
        "per_day_placeholder": "Ajoutez une ou plusieurs heures pour ce jour.",
        "add": "Ajouter",
        "remove_selected": "Supprimer la sélection",
        "save_settings": "Enregistrer les réglages",
        "play_now": "▶ Lire la musique maintenant",
        "footer_help": "Enregistrez les réglages pour mettre à jour le script de lancement et la planification automatique. Laissez la planification vide si vous souhaitez uniquement un lancement manuel.",
        "saved_playlists_placeholder": "Les playlists enregistrées apparaîtront ici après la lecture.",
        "play_selected": "Lire",
        "open_folder": "Ouvrir le dossier",
        "delete": "Supprimer",
        "day_MON": "Lundi", "day_TUE": "Mardi", "day_WED": "Mercredi", "day_THU": "Jeudi", "day_FRI": "Vendredi", "day_SAT": "Samedi", "day_SUN": "Dimanche",
    },
    "ja": {
        **BASE_EN,
        "language": "言語",
        "main_paths": "プレーヤーとプレイリスト",
        "preferred_player": "プレーヤー (.exe)",
        "preferred_player_placeholder": "プレーヤーのパスを選択してください",
        "playlist_folder": "プレイリストフォルダー",
        "playlist_folder_placeholder": "プレイリストを保存するフォルダーを選択してください",
        "track_count": "プレイリストごとの曲数",
        "playlist_history": "保存済みプレイリスト",
        "auto_cleanup_history": "古い保存済みプレイリストを自動的に削除する",
        "keep_for_days": "保存期間",
        "days": "日",
        "saved_playlists_button": "保存済みプレイリスト…",
        "music_folders": "音楽フォルダー",
        "music_folders_placeholder": "音楽フォルダーがここに表示されます。「フォルダーを追加」をクリックして、音楽の場所をアプリに知らせてください。",
        "browse": "参照",
        "add_folder": "フォルダーを追加",
        "remove_selected_folder": "選択を削除",
        "schedule": "スケジュール",
        "schedule_help": "音楽を自動開始する時間を選択してください。このセクションは空のままでもかまいません。",
        "same_every_day": "毎日同じ時間",
        "per_day": "曜日ごとに異なる時間",
        "same_schedule_group": "毎日のスケジュール",
        "time_start": "開始時刻",
        "same_time_placeholder": "すべての日に適用する時刻を1つ以上追加してください。",
        "per_day_help": "必要に応じて曜日ごとに異なる時刻を設定してください。",
        "per_day_placeholder": "この曜日に適用する時刻を1つ以上追加してください。",
        "add": "追加",
        "remove_selected": "選択を削除",
        "save_settings": "設定を保存",
        "play_now": "▶ 今すぐ再生",
        "footer_help": "設定を保存すると、起動スクリプトと自動スケジュールが更新されます。手動再生だけでよい場合はスケジュールを空のままにしてください。",
        "saved_playlists_placeholder": "再生後、保存済みプレイリストがここに表示されます。",
        "play_selected": "再生",
        "open_folder": "フォルダーを開く",
        "delete": "削除",
        "day_MON": "月曜日", "day_TUE": "火曜日", "day_WED": "水曜日", "day_THU": "木曜日", "day_FRI": "金曜日", "day_SAT": "土曜日", "day_SUN": "日曜日",
    },
    "zh_CN": {
        **BASE_EN,
        "language": "语言",
        "main_paths": "播放器和播放列表",
        "preferred_player": "播放器 (.exe)",
        "preferred_player_placeholder": "选择播放器路径",
        "playlist_folder": "播放列表文件夹",
        "playlist_folder_placeholder": "选择保存播放列表的文件夹",
        "track_count": "每个播放列表的曲目数",
        "playlist_history": "已保存的播放列表",
        "auto_cleanup_history": "自动删除较旧的已保存播放列表",
        "keep_for_days": "保留",
        "days": "天",
        "saved_playlists_button": "已保存的播放列表…",
        "music_folders": "音乐文件夹",
        "music_folders_placeholder": "你的音乐文件夹会显示在这里。点击“添加文件夹”，让应用知道去哪里寻找音乐。",
        "browse": "浏览",
        "add_folder": "添加文件夹",
        "remove_selected_folder": "删除所选",
        "schedule": "计划",
        "schedule_help": "选择音乐何时自动开始。你也可以将此部分留空。",
        "same_every_day": "每天相同时间",
        "per_day": "按天设置不同时间",
        "same_schedule_group": "每日计划",
        "time_start": "开始时间",
        "same_time_placeholder": "为每天添加一个或多个时间。",
        "per_day_help": "如有需要，可为每天设置不同时间。",
        "per_day_placeholder": "为这一天添加一个或多个时间。",
        "add": "添加",
        "remove_selected": "删除所选",
        "save_settings": "保存设置",
        "play_now": "▶ 立即播放音乐",
        "footer_help": "保存设置以更新启动脚本和自动计划。如果只需要手动播放，可以将计划留空。",
        "saved_playlists_placeholder": "播放后，这里会显示已保存的播放列表。",
        "play_selected": "播放",
        "open_folder": "打开文件夹",
        "delete": "删除",
        "day_MON": "星期一", "day_TUE": "星期二", "day_WED": "星期三", "day_THU": "星期四", "day_FRI": "星期五", "day_SAT": "星期六", "day_SUN": "星期日",
    },
    "ar": {
        **BASE_EN,
        "language": "اللغة",
        "main_paths": "المشغل وقوائم التشغيل",
        "preferred_player": "المشغل (.exe)",
        "preferred_player_placeholder": "اختر مسار المشغل",
        "playlist_folder": "مجلد قوائم التشغيل",
        "playlist_folder_placeholder": "اختر المجلد الذي سيتم حفظ قوائم التشغيل فيه",
        "track_count": "عدد المقاطع في كل قائمة",
        "playlist_history": "قوائم التشغيل المحفوظة",
        "auto_cleanup_history": "حذف قوائم التشغيل المحفوظة القديمة تلقائيًا",
        "keep_for_days": "الاحتفاظ لمدة",
        "days": "أيام",
        "saved_playlists_button": "قوائم التشغيل المحفوظة…",
        "music_folders": "مجلدات الموسيقى",
        "music_folders_placeholder": "ستظهر مجلدات الموسيقى هنا. انقر على «إضافة مجلد» حتى يعرف التطبيق أين يجد موسيقاك.",
        "browse": "استعراض",
        "add_folder": "إضافة مجلد",
        "remove_selected_folder": "إزالة المحدد",
        "schedule": "الجدول",
        "schedule_help": "اختر متى يجب أن تبدأ الموسيقى تلقائيًا. يمكنك ترك هذا القسم فارغًا.",
        "same_every_day": "نفس الوقت كل يوم",
        "per_day": "أوقات مختلفة حسب اليوم",
        "same_schedule_group": "الجدول اليومي",
        "time_start": "وقت البدء",
        "same_time_placeholder": "أضف وقتًا واحدًا أو أكثر لكل يوم.",
        "per_day_help": "حدّد أوقاتًا مختلفة لكل يوم إذا لزم الأمر.",
        "per_day_placeholder": "أضف وقتًا واحدًا أو أكثر لهذا اليوم.",
        "add": "إضافة",
        "remove_selected": "إزالة المحدد",
        "save_settings": "حفظ الإعدادات",
        "play_now": "▶ شغّل الموسيقى الآن",
        "footer_help": "احفظ الإعدادات لتحديث نص التشغيل والجدول التلقائي. اترك الجدول فارغًا إذا كنت تريد التشغيل اليدوي فقط.",
        "saved_playlists_placeholder": "ستظهر قوائم التشغيل المحفوظة هنا بعد التشغيل.",
        "play_selected": "تشغيل",
        "open_folder": "فتح المجلد",
        "delete": "حذف",
        "day_MON": "الاثنين", "day_TUE": "الثلاثاء", "day_WED": "الأربعاء", "day_THU": "الخميس", "day_FRI": "الجمعة", "day_SAT": "السبت", "day_SUN": "الأحد",
    },
    "hi": {
        **BASE_EN,
        "language": "भाषा",
        "main_paths": "प्लेयर और प्लेलिस्ट",
        "preferred_player": "प्लेयर (.exe)",
        "preferred_player_placeholder": "अपने प्लेयर का पथ चुनें",
        "playlist_folder": "प्लेलिस्ट फ़ोल्डर",
        "playlist_folder_placeholder": "वह फ़ोल्डर चुनें जहाँ प्लेलिस्ट सेव होंगी",
        "track_count": "प्रति प्लेलिस्ट ट्रैक",
        "playlist_history": "सहेजी गई प्लेलिस्ट",
        "auto_cleanup_history": "पुरानी सहेजी गई प्लेलिस्ट अपने आप हटाएँ",
        "keep_for_days": "इतने समय तक रखें",
        "days": "दिन",
        "saved_playlists_button": "सहेजी गई प्लेलिस्ट…",
        "music_folders": "म्यूज़िक फ़ोल्डर",
        "music_folders_placeholder": "आपके म्यूज़िक फ़ोल्डर यहाँ दिखाई देंगे। “फ़ोल्डर जोड़ें” पर क्लिक करें ताकि ऐप जान सके कि आपकी संगीत फ़ाइलें कहाँ हैं।",
        "browse": "ब्राउज़",
        "add_folder": "फ़ोल्डर जोड़ें",
        "remove_selected_folder": "चयन हटाएँ",
        "schedule": "शेड्यूल",
        "schedule_help": "चुनें कि संगीत अपने आप कब शुरू होना चाहिए। आप इस भाग को खाली छोड़ सकते हैं।",
        "same_every_day": "हर दिन एक ही समय",
        "per_day": "दिन के अनुसार अलग समय",
        "same_schedule_group": "दैनिक शेड्यूल",
        "time_start": "शुरू होने का समय",
        "same_time_placeholder": "हर दिन के लिए एक या अधिक समय जोड़ें।",
        "per_day_help": "ज़रूरत हो तो हर दिन के लिए अलग समय सेट करें।",
        "per_day_placeholder": "इस दिन के लिए एक या अधिक समय जोड़ें।",
        "add": "जोड़ें",
        "remove_selected": "चयन हटाएँ",
        "save_settings": "सेटिंग्स सेव करें",
        "play_now": "▶ अभी संगीत चलाएँ",
        "footer_help": "लॉन्च स्क्रिप्ट और स्वचालित शेड्यूल अपडेट करने के लिए सेटिंग्स सेव करें। यदि आपको केवल मैनुअल प्लेबैक चाहिए तो शेड्यूल खाली छोड़ दें।",
        "saved_playlists_placeholder": "प्लेबैक के बाद सहेजी गई प्लेलिस्ट यहाँ दिखाई देंगी।",
        "play_selected": "चलाएँ",
        "open_folder": "फ़ोल्डर खोलें",
        "delete": "हटाएँ",
        "day_MON": "सोमवार", "day_TUE": "मंगलवार", "day_WED": "बुधवार", "day_THU": "गुरुवार", "day_FRI": "शुक्रवार", "day_SAT": "शनिवार", "day_SUN": "रविवार",
    },
}


def tr(lang: str, key: str, **kwargs) -> str:
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    return text.format(**kwargs) if kwargs else text


class PlaceholderEntry(tk.Entry):
    def __init__(self, master, placeholder: str, textvariable: tk.StringVar | None = None, width: int | None = None):
        super().__init__(master, textvariable=textvariable, width=width)
        self.placeholder = placeholder
        self.textvariable = textvariable
        self.default_fg = self.cget("fg")
        self.placeholder_fg = "gray50"
        self._showing_placeholder = False
        self.bind("<FocusIn>", self._handle_focus_in)
        self.bind("<FocusOut>", self._handle_focus_out)
        if self.textvariable is not None:
            self.textvariable.trace_add("write", self._handle_var_change)
        self.after(10, self._apply_placeholder_if_needed)

    def get_clean(self) -> str:
        value = self.textvariable.get() if self.textvariable is not None else self.get()
        value = value.strip()
        if self._showing_placeholder or value == self.placeholder:
            return ""
        return value

    def set_placeholder(self, placeholder: str) -> None:
        current_value = self.get_clean()
        self.placeholder = placeholder
        if self.textvariable is not None:
            self.textvariable.set(current_value)
        else:
            self.delete(0, tk.END)
            if current_value:
                self.insert(0, current_value)
        self._apply_placeholder_if_needed(force=True)

    def _handle_focus_in(self, _event=None) -> None:
        if self._showing_placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)
            self._showing_placeholder = False

    def _handle_focus_out(self, _event=None) -> None:
        self._apply_placeholder_if_needed()

    def _handle_var_change(self, *_args) -> None:
        if self._showing_placeholder and self.focus_get() is self:
            self.config(fg=self.default_fg)
            self._showing_placeholder = False

    def _apply_placeholder_if_needed(self, force: bool = False) -> None:
        value = self.textvariable.get().strip() if self.textvariable is not None else self.get().strip()
        if value and not force:
            if self._showing_placeholder:
                self.config(fg=self.default_fg)
                self._showing_placeholder = False
            return
        if self.focus_get() is self and not force:
            return
        self._showing_placeholder = True
        self.config(fg=self.placeholder_fg)
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)


class PlaceholderListbox(tk.Frame):
    def __init__(self, master, placeholder: str, height: int = 8, wraplength: int = 360):
        super().__init__(master)
        self.listbox = tk.Listbox(self, height=height, exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.placeholder_label = tk.Label(self, text=placeholder, justify="left", anchor="nw", fg="gray45", bg="white", wraplength=wraplength, padx=8, pady=8)
        self.placeholder_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.placeholder_label.bind("<Button-1>", lambda _e: self.listbox.focus_set())
        self.after(20, self.update_placeholder)

    def set_placeholder(self, placeholder: str) -> None:
        self.placeholder_label.config(text=placeholder)
        self.update_placeholder()

    def update_placeholder(self) -> None:
        if self.listbox.size() == 0:
            self.placeholder_label.lift()
        else:
            self.placeholder_label.lower()

    def delete(self, first, last=None):
        self.listbox.delete(first, last)
        self.update_placeholder()

    def insert(self, index, *elements):
        self.listbox.insert(index, *elements)
        self.update_placeholder()

    def get(self, first, last=None):
        if last is None:
            return self.listbox.get(first)
        return self.listbox.get(first, last)

    def curselection(self):
        return self.listbox.curselection()


class TimeEditor(ttk.Frame):
    def __init__(self, master, app: "AutomusicApp", title_key: str, placeholder_key: str):
        super().__init__(master)
        self.app = app
        self.title_key = title_key
        self.placeholder_key = placeholder_key

        self.title_label = ttk.Label(self)
        self.title_label.pack(anchor="w")
        self.listbox = PlaceholderListbox(self, placeholder="", height=7, wraplength=320)
        self.listbox.pack(fill="both", expand=True, pady=(8, 8))
        controls = ttk.Frame(self)
        controls.pack(fill="x")
        self.time_var = tk.StringVar()
        self.entry = PlaceholderEntry(controls, "", textvariable=self.time_var, width=12)
        self.entry.pack(side="left")
        self.add_button = ttk.Button(controls, command=self.add_time)
        self.add_button.pack(side="left", padx=(8, 4))
        self.remove_button = ttk.Button(controls, command=self.remove_selected)
        self.remove_button.pack(side="left")
        self.refresh_language()

    def refresh_language(self) -> None:
        self.title_label.config(text=self.app.tr(self.title_key))
        self.listbox.set_placeholder(self.app.tr(self.placeholder_key))
        self.entry.set_placeholder(self.app.tr("time_entry_placeholder"))
        self.add_button.config(text=self.app.tr("add"))
        self.remove_button.config(text=self.app.tr("remove_selected"))

    def set_times(self, times: list[str]) -> None:
        self.listbox.delete(0, tk.END)
        for time_str in sorted(set(times)):
            self.listbox.insert(tk.END, time_str)

    def get_times(self) -> list[str]:
        return list(self.listbox.get(0, tk.END))

    def add_time(self) -> None:
        raw = self.entry.get_clean()
        normalized = normalize_time(raw)
        if not normalized:
            messagebox.showwarning(APP_TITLE, self.app.tr("warn_time_format"))
            return
        current = set(self.get_times())
        current.add(normalized)
        self.set_times(sorted(current))
        self.time_var.set("")
        self.entry._apply_placeholder_if_needed(force=True)

    def remove_selected(self) -> None:
        selection = list(self.listbox.curselection())
        if not selection:
            return
        for index in reversed(selection):
            self.listbox.delete(index)


class DayTab:
    def __init__(self, notebook: ttk.Notebook, app: "AutomusicApp", day_code: str):
        self.app = app
        self.day_code = day_code
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=app.tr(f"day_{day_code}"))
        self.editor = TimeEditor(self.frame, app, "time_start", "per_day_placeholder")
        self.editor.pack(fill="both", expand=True, padx=2, pady=2)

    def refresh_language(self) -> None:
        self.app.notebook.tab(self.frame, text=self.app.tr(f"day_{self.day_code}"))
        self.editor.refresh_language()

    def set_times(self, times: list[str]) -> None:
        self.editor.set_times(times)

    def get_times(self) -> list[str]:
        return self.editor.get_times()


def app_dir() -> Path:
    return Path(__file__).resolve().parent


CONFIG_PATH = app_dir() / "automusic_config.json"
SCRIPT_PATH = app_dir() / "run-automusic-planner.ps1"

DEFAULT_CONFIG = {
    "language": "en",
    "player_path": "",
    "playlists_dir": "",
    "music_folders": [],
    "desired_count": 30,
    "schedule_mode": "per_day",
    "schedule": {day_code: [] for day_code in DAY_CODES},
    "same_every_day_times": [],
    "auto_cleanup_history": True,
    "history_keep_days": 7,
    "installed_tasks": [],
}

PS1_TEMPLATE = r'''$ErrorActionPreference = "Stop"

$configPath = "{config_path}"
if (-not (Test-Path $configPath)) {{
    Write-Error "Config file not found: $configPath"
    exit 1
}}

$config = Get-Content -Path $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$playerPath = [string]($config.player_path)
$playlistsDir = [string]$config.playlists_dir
$desiredCount = [int]($config.desired_count)
if (-not $desiredCount -or $desiredCount -lt 1) {{
    $desiredCount = 30
}}
if (-not (Test-Path $playerPath)) {{
    Write-Error "Player executable not found: $playerPath"
    exit 1
}}
if (-not (Test-Path $playlistsDir)) {{
    New-Item -ItemType Directory -Force -Path $playlistsDir | Out-Null
}}

$latestPlaylistPath = Join-Path $playlistsDir "automusic_latest.m3u"
$historyDir = Join-Path $playlistsDir "saved_playlists"
if (-not (Test-Path $historyDir)) {{
    New-Item -ItemType Directory -Force -Path $historyDir | Out-Null
}}
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$historyPlaylistPath = Join-Path $historyDir ("automusic_{0}.m3u" -f $timestamp)
$autoCleanupHistory = $true
if ($null -ne $config.auto_cleanup_history) {{
    $autoCleanupHistory = [bool]$config.auto_cleanup_history
}}
$historyKeepDays = 7
if ($config.history_keep_days) {{
    $historyKeepDays = [int]$config.history_keep_days
}}

$musicFolders = @()
foreach ($folder in $config.music_folders) {{
    if ($folder -and (Test-Path $folder)) {{
        $musicFolders += [string]$folder
    }}
}}
if ($musicFolders.Count -eq 0) {{
    Write-Error "No valid music folders found in config."
    exit 1
}}

$extensions = @("*.mp3", "*.flac", "*.wav", "*.aac", "*.m4a", "*.ogg")
$tracks = @()
foreach ($folder in $musicFolders) {{
    foreach ($ext in $extensions) {{
        $tracks += Get-ChildItem -Path $folder -Recurse -File -Filter $ext -ErrorAction SilentlyContinue
    }}
}}
if ($tracks.Count -eq 0) {{
    Write-Error "No audio tracks found in configured folders."
    exit 1
}}

function Get-ArtistNameFromTrack($track, $roots) {{
    $fullDir = $track.Directory.FullName
    foreach ($root in $roots) {{
        $rootPath = [IO.Path]::GetFullPath($root)
        if ($fullDir.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase)) {{
            $relative = $fullDir.Substring($rootPath.Length).TrimStart('\\')
            if ($relative) {{
                return ($relative -split '\\\\')[0]
            }}
        }}
    }}
    return $track.Directory.Name
}}

$grouped = $tracks | Group-Object {{ Get-ArtistNameFromTrack $_ $musicFolders }}
$selected = @()
foreach ($group in $grouped) {{
    if ($group.Count -gt 0) {{
        $selected += $group.Group | Get-Random -Count 1
    }}
}}
$selected = $selected | Get-Random -Count ([Math]::Min($desiredCount, $selected.Count))

$lines = @("#EXTM3U")
foreach ($track in $selected) {{
    $artist = $track.Directory.Name
    $title = [IO.Path]::GetFileNameWithoutExtension($track.Name)
    $info = "$artist - $title"
    $lines += "#EXTINF:-1,$info"
    $lines += $track.FullName
}}

Set-Content -Path $latestPlaylistPath -Value $lines -Encoding UTF8
Set-Content -Path $historyPlaylistPath -Value $lines -Encoding UTF8
if ($autoCleanupHistory -and $historyKeepDays -gt 0) {{
    $cutoff = (Get-Date).AddDays(-$historyKeepDays)
    Get-ChildItem -Path $historyDir -Filter "automusic_*.m3u" -File -ErrorAction SilentlyContinue |
        Where-Object {{ $_.LastWriteTime -lt $cutoff }} |
        Remove-Item -Force -ErrorAction SilentlyContinue
}}

$playerProcessName = [System.IO.Path]::GetFileNameWithoutExtension($playerPath)
Stop-Process -Name $playerProcessName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Start-Process -FilePath $playerPath -ArgumentList "`"$latestPlaylistPath`""
Write-Host "Playlist created at $latestPlaylistPath and player launched." -ForegroundColor Green
'''


def normalize_time(raw: str) -> str | None:
    raw = raw.strip()
    match = TIME_RE.match(raw)
    if not match:
        return None
    return f"{int(match.group(1)):02d}:{int(match.group(2)):02d}"


def common_times_from_schedule(schedule: dict[str, list[str]]) -> list[str]:
    if not schedule:
        return []
    values = [sorted(set(schedule.get(day_code, []))) for day_code in DAY_CODES]
    first = values[0]
    if all(v == first for v in values[1:]):
        return first
    return []


def infer_schedule_mode(schedule: dict[str, list[str]], same_times: list[str]) -> str:
    if same_times or common_times_from_schedule(schedule):
        return "same_every_day"
    return "per_day"


class AutomusicApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("920x740")
        self.minsize(860, 680)

        self.language_var = tk.StringVar(value="en")
        self.player_var = tk.StringVar()
        self.playlists_var = tk.StringVar()
        self.count_var = tk.StringVar(value="30")
        self.auto_cleanup_history_var = tk.BooleanVar(value=True)
        self.history_keep_days_var = tk.StringVar(value="7")
        self.schedule_mode_var = tk.StringVar(value="per_day")
        self.status_var = tk.StringVar(value=self.tr("ready"))
        self.day_tabs: dict[str, DayTab] = {}
        self.history_window: tk.Toplevel | None = None
        self.history_paths: list[Path] = []

        self.build_ui()
        self.load_config_into_ui(self.load_config())
        self.apply_language(initial=True)
        self.update_schedule_mode_ui()

    def tr(self, key: str, **kwargs) -> str:
        return tr(self.language_var.get(), key, **kwargs)

    def build_ui(self) -> None:
        self.container = ttk.Frame(self, padding=12)
        self.container.pack(fill="both", expand=True)

        lang_row = ttk.Frame(self.container)
        lang_row.pack(fill="x", pady=(0, 10))
        self.language_label = ttk.Label(lang_row)
        self.language_label.pack(side="left")
        self.language_combo = ttk.Combobox(lang_row, state="readonly", values=[name for _code, name in LANGUAGE_OPTIONS], width=24)
        self.language_combo.pack(side="left", padx=(8, 0))
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_selected)

        self.path_frame = ttk.LabelFrame(self.container, padding=10)
        self.path_frame.pack(fill="x", pady=(0, 10))
        self.path_frame.columnconfigure(1, weight=1)

        self.player_label = ttk.Label(self.path_frame)
        self.player_label.grid(row=0, column=0, sticky="w", pady=4)
        self.player_entry = PlaceholderEntry(self.path_frame, "", textvariable=self.player_var)
        self.player_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        self.player_button = ttk.Button(self.path_frame, command=self.pick_player)
        self.player_button.grid(row=0, column=2, pady=4)

        self.playlists_label = ttk.Label(self.path_frame)
        self.playlists_label.grid(row=1, column=0, sticky="w", pady=4)
        self.playlists_entry = PlaceholderEntry(self.path_frame, "", textvariable=self.playlists_var)
        self.playlists_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        self.playlists_button = ttk.Button(self.path_frame, command=self.pick_playlists_dir)
        self.playlists_button.grid(row=1, column=2, pady=4)

        self.count_label = ttk.Label(self.path_frame)
        self.count_label.grid(row=2, column=0, sticky="w", pady=4)
        ttk.Spinbox(self.path_frame, from_=1, to=500, textvariable=self.count_var, width=10).grid(row=2, column=1, sticky="w", padx=8, pady=4)

        self.history_label = ttk.Label(self.path_frame)
        self.history_label.grid(row=3, column=0, sticky="w", pady=4)
        history_row = ttk.Frame(self.path_frame)
        history_row.grid(row=3, column=1, sticky="w", padx=8, pady=4)
        self.auto_cleanup_check = ttk.Checkbutton(history_row, variable=self.auto_cleanup_history_var)
        self.auto_cleanup_check.pack(side="left")
        self.keep_for_label = ttk.Label(history_row)
        self.keep_for_label.pack(side="left", padx=(12, 4))
        self.keep_days_spin = ttk.Spinbox(history_row, from_=1, to=3650, textvariable=self.history_keep_days_var, width=6)
        self.keep_days_spin.pack(side="left")
        self.days_label = ttk.Label(history_row)
        self.days_label.pack(side="left", padx=(4, 0))
        self.saved_playlists_button = ttk.Button(self.path_frame, command=self.open_saved_playlists_window)
        self.saved_playlists_button.grid(row=3, column=2, pady=4)

        self.middle = ttk.Frame(self.container)
        self.middle.pack(fill="both", expand=True, pady=(0, 10))
        self.middle.columnconfigure(0, weight=1, uniform="middle")
        self.middle.columnconfigure(1, weight=1, uniform="middle")
        self.middle.rowconfigure(0, weight=1)

        self.folders_frame = ttk.LabelFrame(self.middle, padding=10)
        self.folders_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.music_listbox = PlaceholderListbox(self.folders_frame, placeholder="", height=10, wraplength=300)
        self.music_listbox.pack(fill="both", expand=True)
        folders_buttons = ttk.Frame(self.folders_frame)
        folders_buttons.pack(fill="x", pady=(8, 0))
        self.add_folder_button = ttk.Button(folders_buttons, command=self.add_music_folder)
        self.add_folder_button.pack(side="left")
        self.remove_folder_button = ttk.Button(folders_buttons, command=self.remove_music_folder)
        self.remove_folder_button.pack(side="left", padx=(8, 0))

        self.schedule_frame = ttk.LabelFrame(self.middle, padding=10)
        self.schedule_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.schedule_frame.rowconfigure(3, weight=1)
        self.schedule_help_label = ttk.Label(self.schedule_frame, wraplength=300, justify="left")
        self.schedule_help_label.pack(anchor="w", pady=(0, 8))
        mode_frame = ttk.Frame(self.schedule_frame)
        mode_frame.pack(fill="x", pady=(0, 8))
        self.same_every_day_radio = ttk.Radiobutton(mode_frame, value="same_every_day", variable=self.schedule_mode_var, command=self.update_schedule_mode_ui)
        self.same_every_day_radio.pack(side="left")
        self.per_day_radio = ttk.Radiobutton(mode_frame, value="per_day", variable=self.schedule_mode_var, command=self.update_schedule_mode_ui)
        self.per_day_radio.pack(side="left", padx=(16, 0))
        self.same_every_day_frame = ttk.LabelFrame(self.schedule_frame, padding=10)
        self.same_every_day_editor = TimeEditor(self.same_every_day_frame, self, "time_start", "same_time_placeholder")
        self.same_every_day_editor.pack(fill="both", expand=True)
        self.per_day_frame = ttk.Frame(self.schedule_frame)
        self.per_day_help_label = ttk.Label(self.per_day_frame, wraplength=300, justify="left")
        self.per_day_help_label.pack(anchor="w", pady=(0, 8))
        self.notebook = ttk.Notebook(self.per_day_frame)
        self.notebook.pack(fill="both", expand=True)
        for day_code in DAY_CODES:
            self.day_tabs[day_code] = DayTab(self.notebook, self, day_code)

        actions = ttk.Frame(self.container)
        actions.pack(fill="x")
        self.save_button = ttk.Button(actions, command=self.save_and_apply)
        self.save_button.pack(side="left")
        self.play_button = tk.Button(actions, command=self.run_now, bg="#1f6feb", fg="white", activebackground="#1a5ec8", activeforeground="white", relief="flat", padx=18, pady=8, font=("Segoe UI", 10, "bold"), cursor="hand2")
        self.play_button.pack(side="right")

        self.footer_label = ttk.Label(self.container, foreground="gray35", wraplength=940, justify="left")
        self.footer_label.pack(anchor="w", pady=(10, 0))
        status_frame = ttk.Frame(self.container)
        status_frame.pack(fill="x", pady=(8, 0))
        ttk.Label(status_frame, textvariable=self.status_var, foreground="#1f5f99").pack(anchor="w")

    def apply_language(self, initial: bool = False) -> None:
        self.language_label.config(text=self.tr("language"))
        self.language_combo.set(LANGUAGE_NAMES.get(self.language_var.get(), "English"))
        self.path_frame.config(text=self.tr("main_paths"))
        self.player_label.config(text=self.tr("preferred_player"))
        self.player_entry.set_placeholder(self.tr("preferred_player_placeholder"))
        self.player_button.config(text=self.tr("browse"))
        self.playlists_label.config(text=self.tr("playlist_folder"))
        self.playlists_entry.set_placeholder(self.tr("playlist_folder_placeholder"))
        self.playlists_button.config(text=self.tr("browse"))
        self.count_label.config(text=self.tr("track_count"))
        self.history_label.config(text=self.tr("playlist_history"))
        self.auto_cleanup_check.config(text=self.tr("auto_cleanup_history"))
        self.keep_for_label.config(text=self.tr("keep_for_days"))
        self.days_label.config(text=self.tr("days"))
        self.saved_playlists_button.config(text=self.tr("saved_playlists_button"))
        self.folders_frame.config(text=self.tr("music_folders"))
        self.music_listbox.set_placeholder(self.tr("music_folders_placeholder"))
        self.add_folder_button.config(text=self.tr("add_folder"))
        self.remove_folder_button.config(text=self.tr("remove_selected_folder"))
        self.schedule_frame.config(text=self.tr("schedule"))
        self.schedule_help_label.config(text=self.tr("schedule_help"))
        self.same_every_day_radio.config(text=self.tr("same_every_day"))
        self.per_day_radio.config(text=self.tr("per_day"))
        self.same_every_day_frame.config(text=self.tr("same_schedule_group"))
        self.same_every_day_editor.refresh_language()
        self.per_day_help_label.config(text=self.tr("per_day_help"))
        for tab in self.day_tabs.values():
            tab.refresh_language()
        self.save_button.config(text=self.tr("save_settings"))
        self.play_button.config(text=self.tr("play_now"))
        self.footer_label.config(text=self.tr("footer_help"))
        if self.history_window and self.history_window.winfo_exists():
            self.refresh_saved_playlists_window()
        if not initial:
            self.set_status(self.tr("status_language_changed"))

    def on_language_selected(self, _event=None) -> None:
        selected_name = self.language_combo.get()
        for code, name in LANGUAGE_OPTIONS:
            if name == selected_name:
                self.language_var.set(code)
                break
        self.apply_language(initial=False)

    def update_schedule_mode_ui(self) -> None:
        self.same_every_day_frame.pack_forget()
        self.per_day_frame.pack_forget()
        if self.schedule_mode_var.get() == "same_every_day":
            self.same_every_day_frame.pack(fill="both", expand=True)
        else:
            self.per_day_frame.pack(fill="both", expand=True)

    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.update_idletasks()

    def pick_player(self) -> None:
        path = filedialog.askopenfilename(title=self.tr("dialog_choose_player"), filetypes=[(self.tr("executables"), "*.exe"), (self.tr("all_files"), "*.*")])
        if path:
            self.player_var.set(path)

    def pick_playlists_dir(self) -> None:
        path = filedialog.askdirectory(title=self.tr("dialog_choose_playlist_folder"))
        if path:
            self.playlists_var.set(path)

    def add_music_folder(self) -> None:
        path = filedialog.askdirectory(title=self.tr("dialog_choose_music_folder"))
        if not path:
            return
        folders = set(self.get_music_folders())
        folders.add(path)
        self.set_music_folders(sorted(folders))

    def remove_music_folder(self) -> None:
        selection = list(self.music_listbox.curselection())
        if not selection:
            return
        for index in reversed(selection):
            self.music_listbox.delete(index)

    def get_music_folders(self) -> list[str]:
        return list(self.music_listbox.get(0, tk.END))

    def set_music_folders(self, folders: list[str]) -> None:
        self.music_listbox.delete(0, tk.END)
        for folder in folders:
            self.music_listbox.insert(tk.END, folder)
        self.music_listbox.update_placeholder()

    def load_config(self) -> dict:
        if CONFIG_PATH.exists():
            try:
                with CONFIG_PATH.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                merged = json.loads(json.dumps(DEFAULT_CONFIG))
                merged.update(data)
                if "schedule" not in merged or not isinstance(merged["schedule"], dict):
                    merged["schedule"] = {day_code: [] for day_code in DAY_CODES}
                for day_code in DAY_CODES:
                    merged["schedule"].setdefault(day_code, [])
                merged.setdefault("same_every_day_times", [])
                merged.setdefault("installed_tasks", [])
                merged.setdefault("auto_cleanup_history", True)
                merged.setdefault("history_keep_days", 7)
                if merged.get("language") not in LANGUAGE_NAMES:
                    merged["language"] = "en"
                return merged
            except Exception as exc:
                messagebox.showwarning(APP_TITLE, self.tr("error_read_config", error=str(exc)))
        return json.loads(json.dumps(DEFAULT_CONFIG))

    def load_config_into_ui(self, config: dict) -> None:
        self.language_var.set(config.get("language", "en"))
        self.player_var.set(config.get("player_path", ""))
        self.playlists_var.set(config.get("playlists_dir", ""))
        self.count_var.set(str(config.get("desired_count", 30)))
        self.auto_cleanup_history_var.set(bool(config.get("auto_cleanup_history", True)))
        self.history_keep_days_var.set(str(config.get("history_keep_days", 7)))
        self.set_music_folders(config.get("music_folders", []))
        schedule = config.get("schedule", {})
        for day_code, tab in self.day_tabs.items():
            tab.set_times(schedule.get(day_code, []))
        same_times = config.get("same_every_day_times", [])
        if not same_times:
            same_times = common_times_from_schedule(schedule)
        self.same_every_day_editor.set_times(same_times)
        self.schedule_mode_var.set(config.get("schedule_mode") or infer_schedule_mode(schedule, same_times))
        self.status_var.set(self.tr("ready"))

    def _normalize_time_list(self, raw_times: list[str], label: str) -> list[str]:
        normalized_times = []
        for raw_time in raw_times:
            normalized = normalize_time(raw_time)
            if not normalized:
                raise ValueError(self.tr("error_invalid_time", label=label, value=raw_time))
            normalized_times.append(normalized)
        return sorted(set(normalized_times))

    def collect_config_from_ui(self) -> dict:
        desired_count_raw = self.count_var.get().strip() or "30"
        try:
            desired_count = int(desired_count_raw)
        except ValueError:
            raise ValueError(self.tr("error_track_count_integer"))
        if desired_count < 1:
            raise ValueError(self.tr("error_track_count_positive"))

        history_keep_days_raw = self.history_keep_days_var.get().strip() or "7"
        try:
            history_keep_days = int(history_keep_days_raw)
        except ValueError:
            raise ValueError(self.tr("error_history_days_integer"))
        if history_keep_days < 1:
            raise ValueError(self.tr("error_history_days_positive"))

        player_path = self.player_entry.get_clean()
        playlists_dir = self.playlists_entry.get_clean()
        music_folders = self.get_music_folders()
        schedule_mode = self.schedule_mode_var.get()
        if not player_path:
            raise ValueError(self.tr("error_player_required"))
        if not playlists_dir:
            raise ValueError(self.tr("error_playlist_dir_required"))
        if not music_folders:
            raise ValueError(self.tr("error_music_folder_required"))

        if schedule_mode == "same_every_day":
            same_times = self._normalize_time_list(self.same_every_day_editor.get_times(), self.tr("same_schedule_group"))
            schedule = {day_code: list(same_times) for day_code in DAY_CODES}
        else:
            same_times = []
            schedule = {day_code: self._normalize_time_list(tab.get_times(), self.tr(f"day_{day_code}")) for day_code, tab in self.day_tabs.items()}

        existing = self.load_config()
        return {
            "language": self.language_var.get(),
            "player_path": player_path,
            "playlists_dir": playlists_dir,
            "music_folders": music_folders,
            "desired_count": desired_count,
            "schedule_mode": schedule_mode,
            "schedule": schedule,
            "same_every_day_times": same_times,
            "auto_cleanup_history": bool(self.auto_cleanup_history_var.get()),
            "history_keep_days": history_keep_days,
            "installed_tasks": existing.get("installed_tasks", []),
        }

    def save_config(self, config: dict) -> None:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def generate_ps1(self) -> None:
        SCRIPT_PATH.write_text(PS1_TEMPLATE.format(config_path=str(CONFIG_PATH).replace("\\", "\\\\")), encoding="utf-8")

    def build_task_specs(self, config: dict) -> list[tuple[str, str, str]]:
        specs: list[tuple[str, str, str]] = []
        for day_code in DAY_CODES:
            for time_str in config["schedule"].get(day_code, []):
                hhmm = time_str.replace(":", "")
                specs.append((f"{TASK_PREFIX}_{day_code}_{hhmm}", DAY_PS_NAMES[day_code], time_str))
        return specs

    def save_and_apply(self) -> None:
        try:
            config = self.collect_config_from_ui()
            self.save_config(config)
            self.generate_ps1()
            old_tasks = config.get("installed_tasks", [])
            if old_tasks:
                self._remove_tasks(old_tasks)
            installed_tasks: list[str] = []
            specs = self.build_task_specs(config)
            if specs:
                current_user = subprocess.check_output(["whoami"], text=True).strip()
                for task_name, day_ps, time_str in specs:
                    self._register_task(task_name, day_ps, time_str, current_user)
                    installed_tasks.append(task_name)
            config["installed_tasks"] = installed_tasks
            self.save_config(config)
            if self.history_window and self.history_window.winfo_exists():
                self.refresh_saved_playlists_window()
            if installed_tasks:
                message = self.tr("status_saved_with_schedule", count=len(installed_tasks))
            else:
                message = self.tr("status_saved_no_schedule")
            self.set_status(message)
            messagebox.showinfo(APP_TITLE, message)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, str(exc))

    def run_now(self) -> None:
        try:
            config = self.collect_config_from_ui()
            self.save_config(config)
            self.generate_ps1()
            subprocess.Popen([POWER_SHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT_PATH)], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self.set_status(self.tr("status_starting_music"))
        except Exception as exc:
            messagebox.showerror(APP_TITLE, self.tr("error_run_now", error=str(exc)))

    def get_saved_playlists_dir(self) -> Path:
        playlists_dir = self.playlists_entry.get_clean() or self.load_config().get("playlists_dir", "")
        if not playlists_dir:
            raise ValueError(self.tr("error_playlist_dir_required"))
        return Path(playlists_dir) / "saved_playlists"

    def list_saved_playlist_files(self) -> list[Path]:
        history_dir = self.get_saved_playlists_dir()
        if not history_dir.exists():
            return []
        return sorted(history_dir.glob("automusic_*.m3u"), key=lambda p: p.stat().st_mtime, reverse=True)

    @staticmethod
    def format_saved_playlist_name(path: Path) -> str:
        stem = path.stem
        if stem.startswith("automusic_"):
            raw = stem[len("automusic_"):]
            if len(raw) >= 19 and "_" in raw:
                date_part, time_part = raw.split("_", 1)
                return f"{date_part} {time_part.replace('-', ':')}"
        return path.name

    def open_saved_playlists_window(self) -> None:
        if self.history_window and self.history_window.winfo_exists():
            self.refresh_saved_playlists_window()
            self.history_window.deiconify()
            self.history_window.lift()
            return
        self.history_window = tk.Toplevel(self)
        self.history_window.geometry("560x420")
        self.history_window.minsize(480, 320)
        body = ttk.Frame(self.history_window, padding=12)
        body.pack(fill="both", expand=True)
        self.saved_playlists_list = PlaceholderListbox(body, placeholder=self.tr("saved_playlists_placeholder"), height=12, wraplength=500)
        self.saved_playlists_list.pack(fill="both", expand=True)
        buttons = ttk.Frame(body)
        buttons.pack(fill="x", pady=(10, 0))
        self.history_play_button = ttk.Button(buttons, command=self.play_selected_saved_playlist)
        self.history_play_button.pack(side="left")
        self.history_open_folder_button = ttk.Button(buttons, command=self.open_saved_playlists_folder)
        self.history_open_folder_button.pack(side="left", padx=(8, 0))
        self.history_delete_button = ttk.Button(buttons, command=self.delete_selected_saved_playlist)
        self.history_delete_button.pack(side="left", padx=(8, 0))
        self.history_window.protocol("WM_DELETE_WINDOW", self.history_window.withdraw)
        self.refresh_saved_playlists_window()

    def refresh_saved_playlists_window(self) -> None:
        if not (self.history_window and self.history_window.winfo_exists()):
            return
        self.history_window.title(self.tr("history_window_title"))
        self.saved_playlists_list.set_placeholder(self.tr("saved_playlists_placeholder"))
        self.history_play_button.config(text=self.tr("play_selected"))
        self.history_open_folder_button.config(text=self.tr("open_folder"))
        self.history_delete_button.config(text=self.tr("delete"))
        self.history_paths = self.list_saved_playlist_files()
        self.saved_playlists_list.delete(0, tk.END)
        for path in self.history_paths:
            self.saved_playlists_list.insert(tk.END, self.format_saved_playlist_name(path))
        self.saved_playlists_list.update_placeholder()

    def _get_selected_saved_playlist(self) -> Path:
        if not (self.history_window and self.history_window.winfo_exists()):
            raise ValueError(self.tr("error_select_saved_playlist"))
        selection = list(self.saved_playlists_list.curselection())
        if not selection:
            raise ValueError(self.tr("error_select_saved_playlist"))
        return self.history_paths[selection[0]]

    def play_selected_saved_playlist(self) -> None:
        try:
            playlist_path = self._get_selected_saved_playlist()
            player_path = self.player_entry.get_clean() or self.load_config().get("player_path", "")
            if not player_path:
                raise ValueError(self.tr("error_player_required"))
            subprocess.run(["taskkill", "/IM", f"{Path(player_path).stem}.exe", "/F"], check=False, capture_output=True)
            subprocess.Popen([player_path, str(playlist_path)], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self.set_status(self.tr("status_opening_saved_playlist"))
        except Exception as exc:
            messagebox.showerror(APP_TITLE, str(exc))

    def open_saved_playlists_folder(self) -> None:
        history_dir = self.get_saved_playlists_dir()
        history_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(str(history_dir))

    def delete_selected_saved_playlist(self) -> None:
        try:
            playlist_path = self._get_selected_saved_playlist()
            name = self.format_saved_playlist_name(playlist_path)
            if not messagebox.askyesno(self.tr("confirm_delete_playlist_title"), self.tr("confirm_delete_playlist", name=name)):
                return
            playlist_path.unlink(missing_ok=True)
            self.refresh_saved_playlists_window()
        except Exception as exc:
            messagebox.showerror(APP_TITLE, str(exc))

    def _remove_tasks(self, task_names: list[str]) -> None:
        for task_name in task_names:
            script = (
                "$ErrorActionPreference = 'SilentlyContinue';"
                f"if (Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue) "
                f"{{ Unregister-ScheduledTask -TaskName '{task_name}' -Confirm:$false }}"
            )
            subprocess.run([POWER_SHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], check=False)

    def _register_task(self, task_name: str, day_ps: str, time_str: str, current_user: str) -> None:
        script_path_ps = str(SCRIPT_PATH).replace("'", "''")
        ps = f"""
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -ExecutionPolicy Bypass -File \"{script_path_ps}\"'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek {day_ps} -At '{time_str}'
$principal = New-ScheduledTaskPrincipal -UserId '{current_user}' -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
"""
        completed = subprocess.run([POWER_SHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], text=True, capture_output=True)
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip() or self.tr("error_unknown")
            raise RuntimeError(f"{task_name}: {stderr}")


def main() -> None:
    if sys.platform != "win32":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(APP_TITLE, tr("en", "window_only_windows"))
        return
    app = AutomusicApp()
    app.mainloop()


if __name__ == "__main__":
    main()
