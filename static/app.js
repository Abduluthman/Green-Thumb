"use strict";

const page = document.querySelector("[data-page]")?.dataset.page;
const csrf = () => document.querySelector('meta[name="csrf-token"]').content;
const refinements = {
  Cardboard: [
    { label: "Clean cardboard", query: "Cardboard" },
    { label: "Cereal box", query: "Cereal Boxes" },
    { label: "Food-soiled pizza box", query: "Pizza Boxes" },
  ],
  Glass: [
    { label: "Bottle or jar", query: "Glass" },
    { label: "Broken glass", query: "Broken Glass" },
    { label: "Mirror", query: "Mirrors" },
  ],
  Metal: [
    { label: "Aluminium can", query: "Aluminium Can" },
    { label: "Aerosol can", query: "Aerosol Can" },
    { label: "Metal utensil", query: "Kitchen Utensils" },
  ],
  Organic: [
    { label: "Food scraps", query: "Kitchen Scraps" },
    { label: "Fruit peels", query: "Fruit Peels" },
    { label: "Branches or garden waste", query: "Trees" },
  ],
  Paper: [
    { label: "Newspaper", query: "Newspapers" },
    { label: "Receipt", query: "Receipts" },
    { label: "Used paper napkin", query: "Napkins" },
  ],
  Plastic: [
    { label: "Plastic bottle", query: "Plastic Bottles" },
    { label: "Plastic bag", query: "Nylon Bags" },
    { label: "Plastic wrapper", query: "Sweet Wrapper" },
  ],
  Trash: [
    { label: "Mixed materials", query: "Trash" },
    { label: "Nappy or diaper", query: "Diapers" },
    { label: "Sharp or hazardous item", risk: "special-handling" },
  ],
};

async function api(url, options = {}) {
  const controller = options.signal ? null : new AbortController();
  const timeout = controller
    ? setTimeout(
        () =>
          controller.abort(
            new DOMException("Request timed out", "TimeoutError"),
          ),
        120000,
      )
    : null;
  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers: { "X-CSRFToken": csrf(), ...options.headers },
      signal: options.signal || controller.signal,
    });
  } finally {
    if (timeout) clearTimeout(timeout);
  }
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The server could not complete this request. Please try again.",
    );
  }
  if (!response.ok)
    throw new Error(data.error || "Something went wrong. Please try again.");
  return data;
}

function showResult(data) {
  const uncertain = data.class === "Not Classified";
  document.getElementById("result").textContent = uncertain
    ? "No reliable match"
    : data.class;
  document.getElementById("result-detail").textContent = uncertain
    ? "Try another photo with better lighting and a plain background, or search the dictionary."
    : `Model score: ${(data.confidence * 100).toFixed(1)}%. This score is not a guarantee of correctness.`;
  const link = document.getElementById("search-link");
  link.hidden = uncertain;
  link.href = `/Search-Template.html?item=${encodeURIComponent(data.class)}`;
  const panel = document.getElementById("refine-panel");
  const options = document.getElementById("refine-options");
  if (panel && options) {
    panel.hidden = uncertain;
    options.replaceChildren();
    for (const option of refinements[data.class] || []) {
      const choice = document.createElement("a");
      const params = new URLSearchParams();
      if (option.query) params.set("q", option.query);
      if (option.risk) params.set("risk", option.risk);
      choice.href = `/WasteDictionary.html?${params}`;
      choice.textContent = option.label;
      options.append(choice);
    }
  }
}

async function classify(blob, filename, endpoint) {
  document.getElementById("result").textContent = "Classifying image...";
  document.getElementById("result-detail").textContent =
    "The first scan may take longer while the model loads.";
  document.getElementById("search-link").hidden = true;
  const refinementPanel = document.getElementById("refine-panel");
  if (refinementPanel) refinementPanel.hidden = true;
  const body = new FormData();
  body.append("file", blob, filename);
  try {
    showResult(await api(endpoint, { method: "POST", body }));
  } catch (error) {
    document.getElementById("result").textContent =
      "Image could not be classified";
    document.getElementById("result-detail").textContent =
      error.name === "TimeoutError"
        ? "The scan timed out. Please wait a moment and try again."
        : error.message;
  }
}

if (page === "upload") {
  const input = document.getElementById("fileInput");
  const button = document.getElementById("classify-button");
  const preview = document.getElementById("imagePreview");
  let objectUrl;
  input.addEventListener("change", () => {
    if (objectUrl) URL.revokeObjectURL(objectUrl);
    preview.replaceChildren();
    preview.hidden = true;
    document.getElementById("search-link").hidden = true;
    document.getElementById("result").textContent = "Image selected";
    const file = input.files[0];
    if (!file) return;
    if (
      !["image/jpeg", "image/png", "image/webp"].includes(file.type) ||
      file.size > 8 * 1024 * 1024
    ) {
      input.value = "";
      document.getElementById("result").textContent =
        "Choose a JPEG, PNG or WebP image under 8 MB.";
      return;
    }
    const image = document.createElement("img");
    objectUrl = URL.createObjectURL(file);
    image.src = objectUrl;
    image.alt = "Preview of the selected waste image";
    preview.append(image);
    preview.hidden = false;
    document.getElementById("result-detail").textContent =
      "Select “Classify image” to continue.";
  });
  button.addEventListener("click", async () => {
    const file = input.files[0];
    if (!file) {
      document.getElementById("result").textContent = "Choose an image first.";
      input.focus();
      return;
    }
    button.disabled = true;
    input.disabled = true;
    try {
      await classify(file, file.name, "/classify/upload");
    } finally {
      button.disabled = false;
      input.disabled = false;
    }
  });
}

if (page === "camera") {
  const video = document.getElementById("video");
  const start = document.getElementById("start-camera");
  const stop = document.getElementById("stop-camera");
  const capture = document.getElementById("capture");
  const status = document.getElementById("camera-status");
  let stream;
  let busy = false;
  let active = false;
  function stopCamera() {
    active = false;
    stream?.getTracks().forEach((track) => track.stop());
    stream = null;
    video.srcObject = null;
    start.disabled = false;
    stop.disabled = true;
    capture.disabled = true;
    status.textContent = "Camera is off";
  }
  start.addEventListener("click", async () => {
    active = true;
    start.disabled = true;
    status.textContent = "Waiting for camera permission...";
    try {
      if (!navigator.mediaDevices?.getUserMedia)
        throw new Error(
          "Camera access requires HTTPS or localhost and a supported browser.",
        );
      const requested = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });
      if (!active) {
        requested.getTracks().forEach((track) => track.stop());
        return;
      }
      stream = requested;
      video.srcObject = stream;
      await video.play();
      stop.disabled = false;
      capture.disabled = busy;
      status.textContent =
        "Camera is on. Frame one item and choose “Scan item”.";
    } catch (error) {
      stopCamera();
      status.textContent =
        error.name === "NotAllowedError"
          ? "Camera permission was declined. You can upload an image instead."
          : error.message;
    }
  });
  stop.addEventListener("click", stopCamera);
  window.addEventListener("pagehide", stopCamera);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopCamera();
  });
  capture.addEventListener("click", async () => {
    if (!video.videoWidth || busy) return;
    busy = true;
    capture.disabled = true;
    try {
      const canvas = document.getElementById("canvas");
      canvas.width = Math.min(video.videoWidth, 1280);
      canvas.height = Math.round(
        (canvas.width * video.videoHeight) / video.videoWidth,
      );
      canvas
        .getContext("2d")
        .drawImage(video, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", 0.9),
      );
      if (!blob)
        throw new Error("Could not capture this frame. Please try again.");
      await classify(blob, "frame.jpg", "/classify/realtime");
    } catch (error) {
      status.textContent = error.message;
    } finally {
      busy = false;
      capture.disabled = !stream;
    }
  });
}

if (page === "dictionary") {
  const search = document.getElementById("search-box");
  const streamFilter = document.getElementById("stream-filter");
  const riskFilter = document.getElementById("risk-filter");
  const list = document.getElementById("waste-list");
  const status = document.getElementById("dictionary-status");
  const params = new URLSearchParams(location.search);
  search.value = params.get("q") || "";
  streamFilter.value = params.get("stream") || "";
  riskFilter.value = params.get("risk") || "";

  function searchScore(item, query, streamLabels) {
    if (!query) return 0;
    const name = item.name.toLowerCase();
    const aliases = item.aliases.map((alias) => alias.toLowerCase());
    const streamText = item.streams
      .map((stream) => streamLabels[stream])
      .join(" ")
      .toLowerCase();
    if (name === query) return 100;
    if (aliases.includes(query)) return 90;
    if (name.startsWith(query)) return 80;
    if (aliases.some((alias) => alias.startsWith(query))) return 70;
    if (name.includes(query)) return 60;
    if (aliases.some((alias) => alias.includes(query))) return 50;
    if (streamText.includes(query)) return 30;
    if (item.description.toLowerCase().includes(query)) return 20;
    if (item.guidance.disposal.toLowerCase().includes(query)) return 10;
    return -1;
  }

  api("/dictionary.json")
    .then((catalog) => {
      const items = [...catalog.items].sort((a, b) =>
        a.name.localeCompare(b.name),
      );
      function render() {
        const query = search.value.trim().toLowerCase();
        const matches = items
          .map((item) => ({
            item,
            score: searchScore(item, query, catalog.streams),
          }))
          .filter(
            ({ item, score }) =>
              score >= 0 &&
              (!streamFilter.value ||
                item.streams.includes(streamFilter.value)) &&
              (!riskFilter.value || item.riskLevel === riskFilter.value),
          )
          .sort(
            (a, b) =>
              b.score - a.score || a.item.name.localeCompare(b.item.name),
          );
        list.replaceChildren();
        for (const { item } of matches) {
          const link = document.createElement("a");
          link.className = "dictionary-item";
          link.href = `/Search-Template.html?item=${encodeURIComponent(item.name)}`;
          const title = document.createElement("strong");
          title.textContent = item.name;
          const category = document.createElement("span");
          category.textContent = item.streams
            .map((stream) => catalog.streams[stream])
            .join(" · ");
          link.append(title, category);
          if (item.riskLevel !== "standard") {
            const risk = document.createElement("small");
            risk.className = `risk-chip ${item.riskLevel}`;
            risk.textContent = catalog.riskLevels[item.riskLevel];
            link.append(risk);
          }
          list.append(link);
        }
        status.textContent = matches.length
          ? `${matches.length} ${matches.length === 1 ? "item" : "items"}`
          : "No matches. Try another name or material.";
        const nextParams = new URLSearchParams();
        if (search.value.trim()) nextParams.set("q", search.value.trim());
        if (streamFilter.value) nextParams.set("stream", streamFilter.value);
        if (riskFilter.value) nextParams.set("risk", riskFilter.value);
        history.replaceState(
          null,
          "",
          `${location.pathname}${nextParams.size ? `?${nextParams}` : ""}`,
        );
      }
      search.addEventListener("input", render);
      streamFilter.addEventListener("change", render);
      riskFilter.addEventListener("change", render);
      render();
    })
    .catch((error) => {
      status.textContent = error.message;
    });
}

if (page === "detail") {
  const name = new URLSearchParams(location.search)
    .get("item")
    ?.trim()
    .toLowerCase();
  const title = document.getElementById("wasteName");
  api("/dictionary.json")
    .then((catalog) => {
      const item =
        catalog.items.find((item) => item.name.toLowerCase() === name) ||
        catalog.items.find((item) =>
          item.aliases.some((alias) => alias.toLowerCase() === name),
        );
      if (!item) {
        title.textContent = "Item not found. Try the dictionary.";
        return;
      }
      document.title = `${item.name} | Green Thumb`;
      title.textContent = item.name;
      document.getElementById("other-names").textContent = item.aliases.length
        ? `Also known as: ${item.aliases.join(", ")}`
        : "";
      const risk = document.getElementById("risk-level");
      risk.textContent = catalog.riskLevels[item.riskLevel];
      risk.className = `tag ${item.riskLevel}`;
      document.getElementById("waste-streams").textContent = item.streams
        .map((stream) => catalog.streams[stream])
        .join(" · ");
      document.getElementById("waste-description").textContent =
        item.description;
      document.getElementById("proper-disposal").textContent =
        item.guidance.disposal;
      document.getElementById("disposal-routes").textContent =
        `Route: ${item.guidance.routes
          .map((route) => catalog.routeLabels[route])
          .join(" · ")}`;
      document.getElementById("precautions").textContent =
        item.guidance.preparation;

      if (item.riskLevel !== "standard") {
        const alert = document.getElementById("risk-alert");
        alert.hidden = false;
        alert.className = `risk-alert ${item.riskLevel}`;
        document.getElementById("risk-alert-title").textContent =
          item.riskLevel === "special-handling"
            ? "Special handling recommended"
            : "Handle this item carefully";
        document.getElementById("risk-alert-text").textContent =
          item.guidance.preparation;
      }

      const sourceList = document.getElementById("source-list");
      sourceList.replaceChildren();
      for (const sourceId of item.guidance.sourceIds) {
        const source = catalog.sources[sourceId];
        if (!source) continue;
        const row = document.createElement("li");
        const link = document.createElement("a");
        link.href = source.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = `${source.organisation}: ${source.title}`;
        row.append(link);
        sourceList.append(row);
      }
      if (!sourceList.children.length) {
        const row = document.createElement("li");
        row.textContent =
          "No item-specific official source has been linked yet.";
        sourceList.append(row);
      }
      const linked = item.guidance.status === "source-linked";
      document.getElementById("guidance-note").textContent = linked
        ? "Related official guidance has been linked. Confirm details with the responsible authority before acting."
        : "This text comes from the original project dictionary and has not yet been independently verified.";
      document.getElementById("reviewed-at").textContent = linked
        ? `Sources linked: ${item.guidance.reviewedAt} · ${item.guidance.jurisdiction}`
        : `Status: needs review · ${item.guidance.jurisdiction}`;
      const jurisdiction = catalog.defaultJurisdiction;
      document.getElementById("local-authority").textContent =
        jurisdiction.authority;
      document.getElementById("local-contact").textContent =
        `${jurisdiction.contactNote} Official contact: ${jurisdiction.phoneNumbers.join(" / ")}`;
      const reportLink = document.getElementById("report-guidance");
      if (reportLink) {
        const reportParams = new URLSearchParams({
          topic: "Dictionary correction",
          item: item.name,
        });
        reportLink.href = `/Feedback.html?${reportParams}`;
      }
      document.getElementById("waste-details").hidden = false;
    })
    .catch((error) => {
      title.textContent = error.message;
    });
}

if (page === "feedback") {
  const form = document.getElementById("feedbackForm");
  const status = document.getElementById("feedback-status");
  const query = new URLSearchParams(window.location.search);
  const topic = query.get("topic");
  const item = query.get("item");
  if (
    [...form.elements.issue.options].some((option) => option.value === topic)
  ) {
    form.elements.issue.value = topic;
  }
  if (topic === "Dictionary correction" && item) {
    form.elements.description.value = `Dictionary item: ${item}\n\nCorrection or local update:\n`;
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("button");
    button.disabled = true;
    status.textContent = "Sending...";
    try {
      const data = await api("/submit_feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          issue: form.elements.issue.value,
          description: form.elements.description.value,
        }),
      });
      status.textContent = data.message;
      form.reset();
    } catch (error) {
      status.textContent = error.message;
    } finally {
      button.disabled = false;
    }
  });
}

if (page === "admin") {
  api("/get_feedback")
    .then((items) => {
      document.getElementById("admin-status").textContent = items.length
        ? `${items.length} submissions`
        : "No feedback yet.";
      const container = document.getElementById("feedback-container");
      for (const item of items) {
        const article = document.createElement("article");
        const title = document.createElement("h2");
        title.textContent = item.issue;
        const description = document.createElement("p");
        description.textContent = item.description;
        const time = document.createElement("time");
        time.dateTime = item.timestamp;
        time.textContent = new Date(item.timestamp).toLocaleString();
        article.append(title, description, time);
        container.append(article);
      }
    })
    .catch((error) => {
      document.getElementById("admin-status").textContent = error.message;
    });
}
