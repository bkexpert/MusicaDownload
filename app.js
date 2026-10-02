const API = "http://127.0.0.1:5000/api";

const urlInput = document.querySelector("#url");
const inspectBtn = document.querySelector("#inspect");
const downloadBtn = document.querySelector("#download");
const statusBox = document.querySelector("#status");
const options = document.querySelector("#options");
const filename = document.querySelector("#filename");
const source = document.querySelector("#source");
const format = document.querySelector("#format");
const quality = document.querySelector("#quality");

let mediaUrl = "";

function status(message, type = "") {
  statusBox.textContent = message;
  statusBox.className = "status " + type;
}

function updateQuality() {
  if (format.value === "mp3") {
    quality.innerHTML = `
      <option value="128k">128 kbps</option>
      <option value="192k" selected>192 kbps</option>
      <option value="256k">256 kbps</option>
      <option value="320k">320 kbps</option>`;
  } else {
    quality.innerHTML = `
      <option value="360p">360p</option>
      <option value="480p">480p</option>
      <option value="720p" selected>720p</option>
      <option value="1080p">1080p</option>`;
  }
}
format.addEventListener("change", updateQuality);

inspectBtn.addEventListener("click", async () => {
  mediaUrl = urlInput.value.trim();
  options.classList.add("hidden");

  if (!mediaUrl) {
    status("Cole uma URL para continuar.", "error");
    return;
  }

  try {
    new URL(mediaUrl);
  } catch {
    status("Digite uma URL válida.", "error");
    return;
  }

  inspectBtn.disabled = true;
  status("Analisando arquivo...");

  try {
    const response = await fetch(`${API}/inspect`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({url: mediaUrl})
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Não foi possível analisar.");

    filename.textContent = data.filename;
    source.textContent = `${data.content_type || "mídia"} • ${data.size_human || "tamanho desconhecido"}`;
    options.classList.remove("hidden");
    status("Arquivo identificado. Escolha o formato e a qualidade.", "ok");
  } catch (error) {
    status(error.message + " Verifique se o backend está rodando.", "error");
  } finally {
    inspectBtn.disabled = false;
  }
});

downloadBtn.addEventListener("click", async () => {
  if (!mediaUrl) return;

  downloadBtn.disabled = true;
  status("Processando arquivo...");

  try {
    const response = await fetch(`${API}/download`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        url: mediaUrl,
        format: format.value,
        quality: quality.value
      })
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || "Falha no download.");
    }

    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="?([^"]+)"?/i);
    const name = match ? match[1] : `musiflow.${format.value}`;

    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
    URL.revokeObjectURL(a.href);
    status("Download concluído.", "ok");
  } catch (error) {
    status(error.message, "error");
  } finally {
    downloadBtn.disabled = false;
  }
});
