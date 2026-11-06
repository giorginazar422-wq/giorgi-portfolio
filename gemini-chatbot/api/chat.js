const MODEL = process.env.GEMINI_MODEL || "gemini-3.5-flash-lite";
const MAX_MESSAGES = 20;
module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({error:"გამოიყენე POST მოთხოვნა."});
  }
  const key = process.env.GEMINI_API_KEY;
  if (!key) return res.status(503).json({error:"Gemini API გასაღები სერვერზე არ არის დაყენებული."});
  const messages = req.body && req.body.messages;
  if (!Array.isArray(messages) || !messages.length || messages.length > MAX_MESSAGES) {
    return res.status(400).json({error:"არასწორი შეტყობინებები."});
  }
  if (messages.some(m => !m || !["user","assistant"].includes(m.role) ||
      typeof m.text !== "string" || !m.text.trim() || m.text.length > 6000)) {
    return res.status(400).json({error:"არასწორი შეტყობინების ფორმატი."});
  }
  const contents = messages.map(m=>({
    role: m.role === "assistant" ? "model" : "user",
    parts: [{text:m.text}]
  }));
  const controller = new AbortController();
  const timeout = setTimeout(()=>controller.abort(),25000);
  try {
    const upstream = await fetch(
      "https://generativelanguage.googleapis.com/v1beta/models/" +
      encodeURIComponent(MODEL) + ":generateContent",
      {method:"POST",
       headers:{"Content-Type":"application/json","x-goog-api-key":key},
       body:JSON.stringify({
         systemInstruction:{parts:[{text:"You are Giorgi AI, a friendly, precise assistant. Reply in the same language as the user, with natural Georgian when the user writes in Georgian. Be transparent about limitations."}]},
         contents,
         generationConfig:{maxOutputTokens:2048,temperature:0.7}
       }),signal:controller.signal}
    );
    const data = await upstream.json().catch(()=>({}));
    if (!upstream.ok) {
      const status=upstream.status===429?429:502;
      const error=upstream.status===429?
        "Gemini-ის მოთხოვნების ლიმიტი ამოიწურა. სცადე მოგვიანებით.":
        "Gemini API დროებით მიუწვდომელია. გადაამოწმე მოდელი და API გასაღები.";
      console.error("Gemini error",upstream.status,data?.error?.status||"");
      return res.status(status).json({error});
    }
    const reply=(data.candidates?.[0]?.content?.parts||[])
      .map(p=>typeof p.text==="string"?p.text:"").join("").trim();
    if (!reply) return res.status(502).json({error:"Gemini-მ ტექსტური პასუხი ვერ დააბრუნა."});
    return res.status(200).json({reply});
  } catch (err) {
    return res.status(err.name==="AbortError"?504:502).json({
      error:err.name==="AbortError"?"Gemini-ის პასუხის დრო ამოიწურა.":"სერვერთან კავშირის შეცდომაა."
    });
  } finally {clearTimeout(timeout);}
};