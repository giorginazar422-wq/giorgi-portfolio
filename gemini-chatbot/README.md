# Giorgi AI — Gemini Chatbot

მობილურსა და კომპიუტერზე მორგებული ქართულენოვანი AI ჩატბოტი. Frontend: HTML/CSS/JavaScript; backend: Vercel serverless function; AI: Gemini API.

## ფუნქციები
- თეთრი-ლურჯი ინტერფეისი და dark mode
- ახალი ჩატის შექმნა, ისტორიაში გადართვა, ჩატის წაშლა
- ისტორიას ინახავს ამავე ბრაუზერში (localStorage)
- Enter-ით გაგზავნა; Shift+Enter ახალი სტრიქონისთვის
- პასუხის კოპირება და შეცდომების შეტყობინებები
- უსაფრთხო backend: API გასაღები კოდში არ ინახება

## გაშვება Vercel-ზე
1. GitHub-ზე გახსენი `giorginazar422-wq/giorgi-portfolio` და Vercel-ში აირჩიე **Import Git Repository**.
2. **Root Directory** მიუთითე `gemini-chatbot` (სავალდებულოა — პორტფოლიოს პროექტი არ შეცვალო).
3. Framework Preset: **Other**. Build Command: ცარიელი. Output Directory: ცარიელი.
4. Project Settings → Environment Variables დაამატე `GEMINI_API_KEY` = შენი ახალი Google AI Studio API გასაღები.
5. სურვილისამებრ დაამატე `GEMINI_MODEL` = `gemini-2.5-flash`.
6. დააჭირე Deploy (ან Redeploy, თუ გასაღები მოგვიანებით დაამატე).
7. გახსენი Vercel-ის მისამართი და შეამოწმე ჩატი.

> **უსაფრთხოება:** ადრე ჩატში გაზიარებული API გასაღები შეცვალე/გააუქმე Google AI Studio-ში. არასოდეს ჩაწერო გასაღები HTML-ში, JS-ში ან GitHub-ში. საჯარო endpoint-ს production-ში სჭირდება rate limiting/abuse protection, რადგან საიტის სტუმრებს შეუძლიათ შენი კვოტის გამოყენება.

## ლოკალური ტესტი
`npx vercel dev` (Vercel CLI და დაკავშირებული Vercel პროექტი/გარემოს ცვლადი დაგჭირდება).
მხოლოდ HTML ფაილის გახსნა UI-ს გაჩვენებს, მაგრამ სერვერული /api/chat-ის გარეშე AI პასუხები არ იმუშავებს.

## ფაილები
- `index.html` — რესპონსიული UI, ისტორია, თემები
- `api/chat.js` — Gemini API proxy, server-side
- `vercel.json` — სერვერული ფუნქციის კონფიგურაცია
- `package.json` — Node.js პროექტის მეტამონაცემები

## შენიშვნები
- საუბრები ინახება მოწყობილობაზე და არა სერვერზე.
- ეს არის საწყისი დემო; საჯარო, დიდ დატვირთვაზე აუცილებელია rate limiting, მონიტორინგი და დამატებითი წვდომის კონტროლი.
- **GitHub Pages მარტო ვერ გაუშვებს /api/chat ფუნქციას**; საიტის სრული მუშაობისთვის საჭიროა Vercel ან მსგავსი backend ჰოსტინგი.
