# SimpleNetworkTables

שיבוט לימודי של מערכת NetworkTables: שרת TCP עם הצפנה (RSA / Diffie-Hellman), ממשק גרפי לקליינט (Tkinter), והרשמת משתמשים עם פרסום ומנוי לערכי topics.

**תיעוד פרוטוקול:** [`פרוטוקול.md`](פרוטוקול.md) (עברית) · [`protocol.md`](protocol.md) (English)

---

## דרישות מערכת

| רכיב | גרסה / הערה |
|------|-------------|
| Python | **3.10 ומעלה** (נדרש בגלל `match` בקוד) |
| חבילה חיצונית | `cryptography` |
| ממשק גרפי | `tkinter` (מגיע עם Python ברוב ההתקנות) |
| רשת | פורט **67** פנוי ב-localhost |

**חשוב:** יש להריץ את השרת והקליינט **מתוך תיקיית השורש של הפרויקט** (`SimpleNetworkTables`), כדי שייבוא המודולים (`host`, `client`, `protocol`) יעבוד.

---

## התקנה ראשונית (כל מערכת הפעלה)

### 1. שכפול / פתיחת הפרויקט

פתחו טרמינל (או PowerShell) ועברו לתיקיית הפרויקט:

```bash
cd /path/to/SimpleNetworkTables
```

### 2. התקנת תלויות

```bash
pip install cryptography
```

אם `pip` לא נמצא, השתמשו ב-`py -m pip` (Windows) או `python3 -m pip` (Linux/macOS).

### 3. בדיקה מהירה

```bash
python -c "import cryptography; import tkinter; print('OK')"
```

אם `tkinter` נכשל — ראו סעיף **פתרון בעיות** למטה.

---

## איך להריץ את הפרויקט

### סדר הפעלה

1. **קודם השרת** — עדיף לרוץ לפני שהקליינט מתחבר.
2. **אחר כך הקליינט** — חלון GUI.
3. בממשק: **Settings** → בחרו RSA או Diffie-Hellman → **Connect**.
4. לאחר חיבור מוצלח: התחברות / הרשמה / Dashboard (פרסום ומנוי ל-topics).

כתובת ברירת מחדל: `127.0.0.1:67` (מוגדר ב-`client/src/BackendConstants.py` ו-`host/server_constants.py`).

---

## Windows

### דרישות

- Python 3.10+ מ-[python.org](https://www.python.org/downloads/) או Microsoft Store  
  בסימון ההתקנה: **"Add python.exe to PATH"**.
- במהלך ההתקנה אפשר לסמן **tcl/tk** (לממשק הגרפי).

### הרצה עם קבצי batch (הכי פשוט)

מתוך תיקיית הפרויקט, לחיצה כפולה או מהטרמינל:

**טרמינל 1 — שרת:**
```powershell
.\run_server.bat
```
(מריץ: `py -m host.Server`)

**טרמינל 2 — קליינט:**
```powershell
.\run_client.bat
```
(מריץ: `py -m client.src.main`)

### הרצה ידנית (PowerShell / CMD)

```powershell
cd C:\path\to\SimpleNetworkTables
py -m host.Server
```

```powershell
cd C:\path\to\SimpleNetworkTables
py -m client.src.main
```

אם `py` לא קיים, נסו:
```powershell
python -m host.Server
python -m client.src.main
```

### הערות ל-Windows

- בפעם הראשונה השרת ייצור (אם חסרים) מפתחות RSA ב-`host/RSA_private.pem`, `host/RSA_public.pem` ופרמטרי DH ב-`host/DH.pem`.
- מסד הנתונים נשמר ב-`host/db.pkl`.
- שליחת מיילים להרשמה/שחזור סיסמה דורשת גישה ל-SMTP (מוגדר ב-`host/send_email.py`); בלי רשת אימייל עדיין אפשר לבדוק חיבור ו-Network Tables אחרי login קיים.

---

## Linux

### דרישות

- Python 3.10+:
  ```bash
  python3 --version
  ```
- חבילת Tk ל-GUI (שם החבילה משתנה לפי הפצה):

  **Debian / Ubuntu:**
  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip python3-tk
  ```

  **Fedora:**
  ```bash
  sudo dnf install python3 python3-tkinter
  ```

  **Arch:**
  ```bash
  sudo pacman -S python tk
  ```

### התקנה והרצה

```bash
cd ~/path/to/SimpleNetworkTables
python3 -m venv venv
source venv/bin/activate
pip install cryptography
```

**טרמינל 1 — שרת:**
```bash
python3 -m host.Server
```

**טרמינל 2 — קליינט:**
```bash
python3 -m client.src.main
```

### הערות ל-Linux

- **רגישות לאותיות גדולות/קטנות:** הקוד מייבא `from host.Database import DataBase` בעוד שהקובץ על הדיסק הוא `host/database.py`. ב-Linux זה עלול לגרום ל-`ModuleNotFoundError`.  
  **פתרון:** שנה שם הקובץ או את הייבוא כך שיתאימו, לדוגמה:
  ```bash
  mv host/database.py host/Database.py
  ```
  (או עדכנו ב-`host/Server.py` ל-`from host.database import DataBase`).

- **פורט 67:** ב-Linux פורטים מתחת ל-1024 לפעמים דורשים הרשאות root. אם השרת נכשל ב-`bind`, אפשר:
  - להריץ עם `sudo` (לא מומלץ לפרויקט לימודי), **או**
  - לשנות ב-`host/server_constants.py` וב-`client/src/BackendConstants.py` לפורט מעל 1024 (למשל `8765`) בשני הקבצים.

- אין קבצי `.bat` — השתמשו בפקודות `python3 -m` למעלה.

---

## macOS

### דרישות

- Python 3.10+ — מומלץ להתקין מ-[python.org](https://www.python.org/downloads/) (כולל Tcl/Tk לממשק).
- לחלופין, עם Homebrew:
  ```bash
  brew install python-tk@3.12
  ```
  (גרסת Python תואמת לפי מה ש-Homebrew מציע).

### התקנה והרצה

```bash
cd ~/path/to/SimpleNetworkTables
python3 -m venv venv
source venv/bin/activate
pip install cryptography
```

**טרמינל 1 — שרת:**
```bash
python3 -m host.Server
```

**טרמינל 2 — קליינט:**
```bash
python3 -m client.src.main
```

### הערות ל-macOS

- אם `tkinter` חסר ב-Python של Homebrew, השתמשו ב-Python הרשמי מ-python.org או ב-`brew install python-tk`.
- כמו ב-Linux, ייתכן שיהיה צורך לתקן `Database` / `database` (ראו Linux).
- פורט 67 בדרך כלל לא דורש root ב-macOS, אך אם יש שגיאת `bind` — שנו פורט בשני קבצי הקבועים כמו ב-Linux.

---

## מבנה הפרויקט (תמצית)

```
SimpleNetworkTables/
├── host/                 # שרת
│   ├── Server.py         # נקודת כניסה לשרת
│   ├── database.py       # משתמשים (db.pkl)
│   └── ...
├── client/               # קליינט + GUI
│   └── src/
│       └── main.py       # נקודת כניסה ל-GUI
├── protocol/             # פרוטוקול, TCP, הצפנה
├── run_server.bat        # הרצת שרת (Windows)
├── run_client.bat        # הרצת קליינט (Windows)
├── protocol.md           # מפרט פרוטוקול (אנגלית)
└── פרוטוקול.md           # מפרט פרוטוקול (עברית)
```

---

## פתרון בעיות נפוצות

| בעיה | מה לעשות |
|------|----------|
| `ModuleNotFoundError: No module named 'host'` | הריצו מהתיקייה `SimpleNetworkTables`, לא מתוך `host` או `client`. |
| `No module named 'host.Database'` (Linux/mac) | תאמו שם קובץ/ייבוא — ראו Linux למעלה. |
| `No module named 'tkinter'` | התקינו חבילת Tk למערכת (ראו Linux/macOS) או Python מלא מ-python.org. |
| הקליינט לא מתחבר | ודאו שהשרת רץ, פורט 67 פנוי, ו-IP ב-`BackendConstants` הוא `127.0.0.1`. |
| `Permission denied` על פורט 67 (Linux) | שנה פורט ל-1024+ בשרת ובקליינט. |
| `cryptography` חסר | `pip install cryptography` בתוך venv פעיל. |
| אין מייל אימות | בדיקת הרשמה דורשת SMTP; לבדיקת NT אפשר להשתמש במשתמש שכבר אומת ב-`db.pkl`. |

---

## סיכום פקודות

| מערכת | שרת | קליינט |
|--------|-----|--------|
| Windows | `py -m host.Server` | `py -m client.src.main` |
| Linux | `python3 -m host.Server` | `python3 -m client.src.main` |
| macOS | `python3 -m host.Server` | `python3 -m client.src.main` |

**זכרו:** שרת קודם, קליינט אחר כך, חיבור מ-Settings לפני Login.

---

## קישורים

- [פרוטוקול תקשורת (עברית)](פרוטוקול.md)
- [Protocol specification (English)](protocol.md)
