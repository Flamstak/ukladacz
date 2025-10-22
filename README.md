# Sorter Plików 🗂️

Prosta, ale potężna aplikacja desktopowa do automatycznego sortowania plików w folderach na podstawie ich rozszerzeń. Koniec z bałaganem w folderze "Pobrane"!



## ✨ Kluczowe Funkcje

* **Sortowanie według Reguł:** Automatycznie przenosi pliki `.mp4` do folderu `wideo/`, `.jpg` do `zdjecia/` itd.
* **Pełna Konfiguracja:** Wbudowany edytor pozwala na dodawanie, usuwanie i modyfikowanie reguł (np. dodaj `.webp` do kategorii `zdjecia`) oraz zmianę domyślnej ścieżki.
* **Dwa Tryby Pracy:**
    * **Domyślne:** Sortuje stały, zdefiniowany folder (np. `Pobrane`).
    * **Jednorazowe:** Pozwala wybrać dowolny folder do jednorazowej akcji.
* **Bezpieczny Podgląd (Preview):** 🛡️ Uruchom "Podgląd", aby zobaczyć w logu, co *zostanie* przeniesione, zanim fizycznie przeniesiesz jakikolwiek plik.
* **Sortowanie Rekursywne:** Opcjonalnie przeszukuj i sortuj pliki znajdujące się również w podfolderach.
* **Inteligentne Czyszczenie:** 🧹 Automatycznie usuwaj puste foldery, które pozostały po sortowaniu.
* **Funkcja Cofnij (Undo):** ↩️ Bezpiecznie cofnij całą ostatnią operację sortowania jednym kliknięciem.
* **Nowoczesny Interfejs:** Czysty interfejs (z trybem jasnym/ciemnym 🌗) zbudowany przy użyciu `CustomTkinter`.

## 🚀 Instalacja i Uruchomienie

Aplikacja wymaga Pythona 3.x oraz jednej zewnętrznej zależności.

1.  **Sklonuj Repozytorium:**
    Otwórz terminal i sklonuj to repozytorium na swój dysk lokalny (wymagany [Git](https://git-scm.com/)):
    ```bash
    git clone https://github.com/Flamstak/ukladacz.git
    ```
    *(Zastąp powyższy URL adresem URL swojego repozytorium)*

2.  **Przejdź do folderu:**
    ```bash
    cd sorter-plikow
    ```

3.  **Zainstaluj zależności:**
    Aplikacja używa `customtkinter`. Zainstaluj go za pomocą pip. (Zalecane jest utworzenie i aktywacja wirtualnego środowiska `python -m venv venv` przed tym krokiem).
    ```bash
    pip install customtkinter
    ```

4.  **Uruchom aplikację:**
    ```bash
    python ukladacz.py
    ```
    Aplikacja automatycznie utworzy pliki `config.json` (z regułami) i `undo.log` (po sortowaniu) w tym samym katalogu.

## ⚙️ Jak to działa?

1.  **Ustawienia (Pierwsze uruchomienie):**
    * Po uruchomieniu kliknij **"Ustawienia i Edytor Reguł"**.
    * W górnej części ustaw **"Domyślną ścieżkę"** (np. `C:/Users/TwojaNazwa/Downloads`).
    * Przejrzyj domyślne kategorie i rozszerzenia. Możesz je dowolnie modyfikować.
    * Kliknij **"Zapisz Zmiany i Zamknij"**.

2.  **Wybierz Tryb:**
    * **Domyślne:** Użyje ścieżki ustawionej w konfiguracji (idealne do regularnego sprzątania "Pobranych").
    * **Jednorazowe:** Pozwoli Ci wybrać dowolny inny folder do posortowania.

3.  **Wybierz Opcje:**
    * Zaznacz **"Sortuj rekursywnie"**, jeśli pliki są także w podfolderach.
    * Zaznacz **"Usuń puste podfoldery"**, aby automatycznie posprzątać po sortowaniu.

4.  **Wybierz Akcję:**
    * **Uruchom Podgląd:** Zobaczysz w logu, które pliki *zostałyby* przeniesione. Jest to w 100% bezpieczne, żadne pliki nie zostaną ruszone.
    * **Uruchom Sortowanie:** Rozpocznie faktyczne przenoszenie plików. Dziennik `undo.log` zostanie utworzony na wypadek pomyłki.

5.  **Cofnij:**
    * Jeśli wynik sortowania nie jest zadowalający, po prostu kliknij czerwony przycisk **"Cofnij ostatnią operację"**. Wszystkie pliki i foldery wrócą na swoje pierwotne miejsca.

## 🛠️ Technologie

* **Python 3**
* **CustomTkinter** (dla nowoczesnego GUI)
* **Tkinter** (jako baza dla CTk i okien dialogowych)
* **JSON** (do przechowywania konfiguracji)

---
Stworzone przez **Flamstak**