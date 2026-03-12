# Dashboard (Dash)

דאשבורד אינטראקטיבי לדוגמה בפייתון בעזרת Dash + Plotly.

## התקנה

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## הרצה

```bash
python dashboard.py
```

ואז לפתוח בדפדפן את:

- `http://127.0.0.1:8050`

## מה יש בדאשבורד

- פילטרים: טווח תאריכים, מוצר, אזור, ערוץ
- KPI: הכנסות, הזמנות, AOV, מספר ימים
- גרפים: הכנסות לאורך זמן, הכנסות לפי מוצר, חלוקת הכנסות לפי אזור
- טבלה עם טרנזקציות (דאטה לדוגמה שנוצר בקוד)
