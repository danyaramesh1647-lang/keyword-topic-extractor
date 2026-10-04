const $ = (id) => document.getElementById(id);
const textBox = $("text");
const btn = $("extract");
let lastText = "";

const EXAMPLE =
  "Artificial intelligence is rapidly transforming healthcare. Machine learning algorithms can help doctors detect diseases earlier by analyzing medical images and patient data. AI-based systems are also being developed to improve drug discovery and provide personalized treatment.";

textBox.addEventListener("input", () => {
  const t = textBox.value.trim();
  $("c-words").textContent = `${t ? t.split(/\s+/).length : 0} words`;
});
btn.addEventListener("click", extract);
$("clear").addEventListener("click", clearAll);
$("copy").addEventListener("click", copyResults);
$("example").addEventListener("click", () => {
  textBox.value = EXAMPLE;
  textBox.dispatchEvent(new Event("input"));
  extract();
});

async function extract() {
  $("error").hidden = true;
  btn.disabled = true;
  btn.textContent = "Extracting...";
  try {
    const res = await fetch("/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: textBox.value }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    render(data);
  } catch (err) {
    $("result").hidden = true;
    $("error").textContent = err.message;
    $("error").hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = "Extract keywords";
  }
}

function render(d) {
  $("result").hidden = false;
  const s = d.stats;
  $("stats").textContent = `${s.words} words analyzed, ${s.sentences} sentences, ${d.keywords.length} keywords found`;

  const tags = $("tags");
  tags.innerHTML = "";
  d.keywords.forEach((k) => {
    const li = document.createElement("li");
    li.style.fontSize = `${0.85 + (k.relevance / 100) * 0.35}rem`;
    li.textContent = k.text;
    if (k.count > 1) {
      const small = document.createElement("small");
      small.textContent = "x" + k.count;
      li.appendChild(small);
    }
    tags.appendChild(li);
  });

  const freq = $("freq");
  freq.innerHTML = "";
  const maxCount = Math.max(...d.keywords.map((k) => k.count), 1);
  d.keywords.slice(0, 8).forEach((k) => {
    const row = document.createElement("div");
    row.innerHTML = `<span></span><div class="bar"><i></i></div><b>${k.count}</b>`;
    row.querySelector("span").textContent = k.text;
    freq.appendChild(row);
    requestAnimationFrame(() => (row.querySelector("i").style.width = (k.count / maxCount) * 100 + "%"));
  });

  const topics = $("topics");
  topics.innerHTML = "";
  d.topics.forEach((t) => {
    const li = document.createElement("li");
    const detail = t.words.length ? `Matched words: ${t.words.join(", ")}` : "Key phrase from the text";
    li.innerHTML = `<div><strong></strong><span></span></div>`;
    li.querySelector("strong").textContent = t.name;
    li.querySelector("span").textContent = detail;
    topics.appendChild(li);
  });
  if (!d.topics.length) topics.innerHTML = "<li><div>No clear topic found. Try a longer text.</div></li>";

  lastText = [
    "KEYWORDS", "", ...d.keywords.map((k) => `• ${k.text} (${k.count})`), "",
    "MAIN TOPICS", "", ...d.topics.map((t, i) => `${i + 1}. ${t.name}`),
  ].join("\n");
  $("copy").textContent = "Copy results";
}

async function copyResults() {
  try {
    await navigator.clipboard.writeText(lastText);
    $("copy").textContent = "Copied";
  } catch {
    $("copy").textContent = "Copy failed";
  }
  setTimeout(() => ($("copy").textContent = "Copy results"), 1800);
}

function clearAll() {
  textBox.value = "";
  lastText = "";
  $("c-words").textContent = "0 words";
  $("result").hidden = true;
  $("error").hidden = true;
  textBox.focus();
}