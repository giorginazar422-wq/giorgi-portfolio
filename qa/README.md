# Automated website testing — Python + Playwright

ვებსაიტის ავტომატიზირებული შემოწმება / Automated QA for the portfolio website
**https://giorginazar422-wq.github.io/giorgi-portfolio/**

The suite opens the site in a real Chromium browser, checks that everything works
(functional tests), checks that nothing looks different from the approved screenshots
(visual tests), runs basic accessibility checks and writes an HTML + JSON report.
When a check fails the report contains the error, a screenshot of the page and, for visual
defects, a *baseline | current | difference* image.

---

## 🇬🇪 ქართულად

### რას ამოწმებს

| ტიპი | ფაილი | რას ამოწმებს |
| --- | --- | --- |
| ფუნქციური | `tests/test_functional.py` | გვერდების ჩატვირთვა (200), სათაური, ვიდეოს მზადყოფნა, კონსოლის შეცდომები და გატეხილი რესურსები, ნავიგაციის ბმულები და "Next" ღილაკები, კლავიატურით მართვა, `#hash` ბმულები, "Read portfolio" დიალოგი, "Copy email" ღილაკი და ბუფერი, საკონტაქტო ბმულები (mailto, GitHub), manifest და იკონები, 404 გვერდი, `rover/` გადამისამართება, მობილურზე ჰორიზონტალური გადახვევის არარსებობა, `classic/` გვერდის ჩატი, მენიუ, ფუტერის წელი |
| ვიზუალური | `tests/test_visual.py` | 12 სკრინშოტი (desktop / tablet / mobile) შედარებულია `baseline/` საქაღალდეში შენახულ ეტალონთან. თუ პიქსელების > 1 % შეიცვალა, ეს დეფექტია და იქმნება diff სურათი |
| ხელმისაწვდომობა | `tests/test_accessibility.py` | `lang`, `<title>`, viewport, `<h1>`, ღილაკების/ბმულების სახელები, სურათების alt ტექსტი, landmark-ები, `<noscript>` |

### გაშვება

```bash
cd qa
pip install -r requirements.txt
python -m playwright install chromium

python run.py                      # ამოწმებს ცოცხალ საიტს
python run.py --local              # ამოწმებს ამ რეპოზიტორიის ფაილებს ლოკალური სერვერით
python run.py -k visual            # მხოლოდ ვიზუალური ტესტები
python run.py --headed --slowmo 300   # ბრაუზერის ფანჯრით, ნელა
python run.py --update-baselines   # ეტალონური სკრინშოტების განახლება (დიზაინის შეცვლის შემდეგ)
```

### რეპორტი

ყოველი გაშვების შემდეგ იქმნება:

- `reports/report.html` — ვიზუალური რეპორტი: სტატუსი, სტატისტიკა, დეფექტების სია შეცდომის ტექსტით და სკრინშოტებით, ყველა ტესტის ცხრილი.
- `reports/report.json` — იგივე მონაცემები მანქანური წასაკითხად.
- `reports/screenshots/` — მიმდინარე სკრინშოტები და `FAIL_*.png` ჩავარდნილი ტესტებისთვის.
- `reports/diffs/` — `baseline | current | diff` სურათები ვიზუალური ტესტებისთვის.

დეფექტებიანი რეპორტის მაგალითი: [`examples/report-with-defects.html`](examples/report-with-defects.html)
(საიტის ლოკალურ ასლში განზრახ ჩავამატეთ 4 ხარვეზი: არასწორი ელფოსტა, გატეხილი Skills ბმული,
არარსებული იკონა manifest-ში და დიალოგის გადაადგილებული სათაური — სუიტამ ყველა იპოვა).

---

## 🇬🇧 English

### What is checked

- **Functional (34 tests):** HTTP 200 for every page, title and `lang`, story video readiness,
  console errors and broken resources, navigation links, "Next" buttons, arrow controls,
  keyboard driving, hash deep links, "Read portfolio" dialog (open / close / Escape),
  "Copy email" button and clipboard content, contact links, manifest + icons, 404 page,
  `rover/` redirect, no horizontal overflow on mobile, classic page chat demo, mobile menu, footer year.
- **Visual (12 screenshots):** landing (desktop / tablet / mobile), skills room, contact room,
  portfolio dialog, classic page (full page) and the Mars page are compared pixel by pixel with
  the baselines in `baseline/`. Video, canvas and animations are frozen before the screenshot
  so results are repeatable. More than 1 % changed pixels = defect.
- **Accessibility (9 tests):** document basics, accessible names for buttons and links,
  alternative text, landmarks and live regions, `noscript` fallback.

### Running

```bash
cd qa
pip install -r requirements.txt
python -m playwright install chromium
python run.py                 # live site
python run.py --local         # this repository served locally
python run.py --site http://127.0.0.1:8000/   # any other URL
```

`run.py` forwards every other argument to pytest (`-k`, `-x`, `--headed`, `--slowmo`, `--update-baselines`).
The process exit code is non-zero when a defect was found, so it can gate a CI pipeline.

### Report

`reports/report.html` is self-contained; open it in a browser. It lists the overall status,
counts, every defect with its assertion message, captured console errors / failed requests,
a screenshot of the page at the moment of failure and the diff image for visual defects.
`reports/report.json` holds the same data for tooling.

### Project layout

```
qa/
├── run.py                 one-command entry point
├── config.py              site URL, viewports, thresholds, expected values
├── conftest.py            browser fixtures, console / network capture, local server, report hooks
├── tests/
│   ├── test_functional.py
│   ├── test_visual.py
│   └── test_accessibility.py
├── reporting/
│   ├── collector.py       collects outcomes, writes report.json / report.html
│   ├── html_report.py     HTML template
│   └── visual.py          pixel comparison + diff image (Pillow)
├── baseline/              approved screenshots (commit them)
├── reports/               generated on every run
└── examples/              sample report with defects
```

### Continuous integration

`.github/workflows/qa.yml` runs the suite on every push to `main`, every Monday against the
live site, or manually, and uploads the report as a workflow artifact.
