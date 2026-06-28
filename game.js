"use strict";

const STAGE_CONFIG = [
    { id: "drums",  label: "Drums",              badge: "DRUMS",  hint: "Just the rhythm." },
    { id: "bass",   label: "+ Bass",              badge: "BASS",   hint: "Low end joins in." },
    { id: "guitar", label: "+ Guitar",            badge: "GUITAR", hint: "Guitar layers added." },
    { id: "piano",  label: "+ Piano / Keys",      badge: "KEYS",   hint: "Keyboard instruments added." },
    { id: "other",  label: "+ Synths & Strings",  badge: "SYNTHS", hint: "Remaining instruments." },
    { id: "vocals", label: "+ Vocals",            badge: "VOX",    hint: "Vocals enter." },
    { id: "full",   label: "Full Song",           badge: "FULL",   hint: "The complete recording." },
];

const TOTAL_CLUES   = STAGE_CONFIG.length;
const POINTS        = [70, 60, 50, 40, 30, 20, 10];
const DAILY_EPOCH_MS = Date.UTC(2025, 0, 1);

const state = {
    songs: [], currentSong: null, clueIndex: 0, score: 0, streak: 0,
    audio: null, isPlaying: false, mode: "daily", dailyNumber: 0,
    customSongId: null, gameOver: false,
};

const $ = id => document.getElementById(id);
const clean = s => s.toLowerCase().replace(/[^a-z0-9]/g, "");

function parseURLParams() {
    const params = new URLSearchParams(window.location.search);
    const mode   = params.get("mode");
    const song   = params.get("song");

    if (mode === "random") {
        state.mode = "random";
    } else if (mode === "custom" && song) {
        state.mode = "custom";
        state.customSongId = song;
    } else {
        state.mode = "daily";
    }
}

function getDailyInfo(songs) {
    const dayIndex = Math.floor((Date.now() - DAILY_EPOCH_MS) / 86400000);
    return { number: dayIndex + 1, song: songs[dayIndex % songs.length] };
}

async function loadData() {
    try {
        const res = await fetch("dataComp.json");
        if (!res.ok) throw new Error(`HTTP ${res.status} loading dataComp.json`);
        const data = await res.json();
        state.songs = data.songs || [];

        if (!state.songs.length) throw new Error("dataComp.json has no songs.");

        parseURLParams();
        populateSongPicker();
        setActiveModeButton();
        startRound();
    } catch (err) {
        console.error(err);
        $("clue-content").innerHTML = `<div class="load-error">Could not load songs.<br><br>Error: ${err.message}</div>`;
    }
}

function startRound() {
    stopAudio();

    if (state.mode === "daily") {
        const daily = getDailyInfo(state.songs);
        state.currentSong = daily.song;
        state.dailyNumber = daily.number;
        $("mode-badge").textContent = "Daily Challenge #" + daily.number;
    } else if (state.mode === "custom") {
        const found = state.songs.find(s => s.id === state.customSongId);
        if (!found) {
            console.warn("Custom song ID not found, defaulting to first song.");
        }
        state.currentSong = found || state.songs[0];
        $("mode-badge").textContent = "Custom Challenge";
    } else {
        state.currentSong = state.songs[Math.floor(Math.random() * state.songs.length)];
        $("mode-badge").textContent = "Random";
    }

    state.clueIndex = 0;
    state.gameOver = false;
    state.isPlaying = false;

    $("game-area").style.display = "block";
    $("result-screen").style.display = "none";
    $("custom-panel").style.display = "none";
    $("guess-input").value = "";
    $("autocomplete-dropdown").style.display = "none";

    setFeedback("", "");
    renderTrackPanel();
    renderPips();
    $("play-clue-btn").textContent = "Play Clue 1 of " + TOTAL_CLUES;
}

function stopAudio() {
    if (state.audio) {
        state.audio.pause();
        state.audio = null;
    }
    state.isPlaying = false;
}

function playCurrentClue() {
    if (!state.currentSong || state.gameOver) return;

    // Safety check: Ensure the stage exists in the JSON
    const stagePath = state.currentSong.stages ? state.currentSong.stages[state.clueIndex] : null;
    if (!stagePath) {
        setFeedback("Audio file missing for this clue. Try skipping.", "error");
        return;
    }

    stopAudio();
    state.audio = new Audio(stagePath);

    state.audio.addEventListener("ended", () => {
        state.isPlaying = false;
        renderTrackPanel();
        $("play-clue-btn").textContent = "Play Clue " + (state.clueIndex + 1) + " again";
    });

    state.audio.play().catch(err => {
        console.warn("Audio playback error:", err);
        setFeedback("Could not play audio. File might be missing on GitHub.", "error");
        state.isPlaying = false;
        renderTrackPanel();
    });

    state.isPlaying = true;
    renderTrackPanel();
    $("play-clue-btn").textContent = "Playing Clue " + (state.clueIndex + 1) + " of " + TOTAL_CLUES + "...";
}

function renderTrackPanel() {
    let html = "";
    for (let i = 0; i < STAGE_CONFIG.length; i++) {
        const cfg = STAGE_CONFIG[i];
        let rowState = "locked";
        if (i < state.clueIndex) rowState = "done";
        else if (i === state.clueIndex) rowState = state.isPlaying ? "playing" : "active";

        html += `
            <div class="track track-${rowState}" data-stem="${cfg.id}">
                <div class="track-badge badge-${cfg.id}">${cfg.badge}</div>
                <div class="track-body">
                    <div class="track-label">${cfg.label}</div>
                    ${rowState !== "locked" ? `<div class="track-hint">${cfg.hint}</div>` : ""}
                </div>
                <div class="track-bars">
                    <span style="--i:0"></span><span style="--i:1"></span><span style="--i:2"></span><span style="--i:3"></span><span style="--i:4"></span>
                </div>
            </div>`;
    }
    $("clue-content").innerHTML = html;
    $("current-level").textContent = state.clueIndex + 1;
}

function renderPips() {
    let html = "";
    for (let i = 0; i < TOTAL_CLUES; i++) {
        let cls = "pip";
        if (i < state.clueIndex) cls += " pip-done";
        else if (i === state.clueIndex) cls += " pip-active";
        html += `<div class="${cls}"></div>`;
    }
    $("pips-bar").innerHTML = html;
}

// AUTOCOMPLETE LOGIC
const input = $("guess-input");
const dropdown = $("autocomplete-dropdown");

input.addEventListener("input", () => {
    const val = input.value.trim().toLowerCase();
    if (!val) {
        dropdown.style.display = "none";
        return;
    }
    
    // STRICT PREFIX MATCH ONLY
    const matches = state.songs.filter(s => 
        s.title.toLowerCase().startsWith(val)
    ).slice(0, 5); 

    if (matches.length === 0) {
        dropdown.style.display = "none";
        return;
    }

    dropdown.innerHTML = matches.map(s => `
        <div class="ac-item" data-title="${s.title}">
            ${s.title}
            <span class="ac-artist">by ${s.artists.join(", ")}</span>
        </div>
    `).join("");
    dropdown.style.display = "block";
});

dropdown.addEventListener("click", (e) => {
    const item = e.target.closest(".ac-item");
    if (item) {
        input.value = item.dataset.title;
        dropdown.style.display = "none";
    }
});

document.addEventListener("click", (e) => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = "none";
    }
});

function checkGuess() {
    if (state.gameOver) return;
    const typed = clean($("guess-input").value);
    const answer = clean(state.currentSong.title);
    if (!typed) return;

    const correct = typed === answer || (typed.length >= 4 && answer.includes(typed));

    if (correct) {
        handleCorrect();
    } else {
        setFeedback("Not quite -- the next layer is now unlocked.", "error");
        advanceClue();
    }
}

function advanceClue() {
    if (state.clueIndex < STAGE_CONFIG.length - 1) {
        state.clueIndex++;
        stopAudio();
        renderTrackPanel();
        renderPips();
        $("play-clue-btn").textContent = "Play Clue " + (state.clueIndex + 1) + " of " + TOTAL_CLUES;
    } else {
        setFeedback("Out of clues!", "error");
        handleSkip();
    }
}

function handleCorrect() {
    stopAudio();
    const pts = POINTS[state.clueIndex] || 10;
    state.score += pts;
    state.streak += 1;
    state.gameOver = true;
    updateStats();
    showResult(true, pts);
}

function handleSkip() {
    stopAudio();
    state.streak = 0;
    state.gameOver = true;
    updateStats();
    showResult(false, 0);
}

function showResult(won, points) {
    $("game-area").style.display = "none";
    $("result-screen").style.display = "block";

    const titleEl = $("result-title");
    titleEl.textContent = won ? "Correct!" : "Skipped";
    titleEl.className = won ? "result-title result-win" : "result-title result-skip";

    const artist = state.currentSong.artists.join(", ");
    $("result-song").innerHTML =
        `<strong>${state.currentSong.title}</strong> by <span class="artist-name">${artist}</span>` +
        (won ? `<br>Solved on clue ${state.clueIndex + 1} of ${TOTAL_CLUES} &bull; +${points} points` : "");

    $("result-grid").innerHTML = buildResultGrid(won);

    const showShare = (state.mode === "daily" || state.mode === "custom");
    $("share-btn").style.display = showShare ? "inline-block" : "none";

    $("next-btn").textContent =
        state.mode === "daily" ? "Play Random Instead" :
        state.mode === "custom" ? "Play Again" : "Next Song";
}

function buildResultGrid(won) {
    let cells = "";
    for (let i = 0; i < TOTAL_CLUES; i++) {
        if (i < state.clueIndex) cells += `<span class="grid-cell cell-miss"></span>`;
        else if (i === state.clueIndex && won) cells += `<span class="grid-cell cell-win"></span>`;
        else cells += `<span class="grid-cell cell-empty"></span>`;
    }
    return `<div class="result-grid-row">${cells}</div>`;
}

function buildShareText() {
    const cells = [];
    for (let i = 0; i < TOTAL_CLUES; i++) {
        if (i < state.clueIndex) cells.push("X");
        else if (i === state.clueIndex) cells.push("O");
        else cells.push(".");
    }
    const grid = cells.join(" ");
    const base = window.location.origin + window.location.pathname;
    const won = cells.includes("O");

    if (state.mode === "daily") {
        return [
            "Unwrap Daily #" + state.dailyNumber,
            won ? "Solved on clue " + (state.clueIndex + 1) + " of " + TOTAL_CLUES : "Could not solve it today",
            grid, "Play: " + base
        ].join("\n");
    }
    if (state.mode === "custom") {
        return ["Can you unwrap this song?", base + "?mode=custom&song=" + state.currentSong.id].join("\n");
    }
    return base;
}

function shareResult() {
    const text = buildShareText();
    const btn = $("share-btn");
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            btn.textContent = "Copied!";
            setTimeout(() => { btn.textContent = "Share Result"; }, 2500);
        }).catch(() => fallbackCopy(text, btn));
    } else {
        fallbackCopy(text, btn);
    }
}

function fallbackCopy(text, btn) {
    const ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.focus(); ta.select();
    try { document.execCommand("copy"); btn.textContent = "Copied!"; } 
    catch (e) { window.prompt("Copy this:", text); }
    document.body.removeChild(ta);
    setTimeout(() => { btn.textContent = "Share Result"; }, 2500);
}

function populateSongPicker() {
    const picker = $("song-picker");
    if (!picker) return;
    picker.innerHTML = state.songs.map(s => `<option value="${s.id}">${s.title} -- ${s.artists.join(", ")}</option>`).join("");
    refreshCustomLink();
}

function refreshCustomLink() {
    const picker = $("song-picker");
    const linkEl = $("custom-link");
    if (!picker || !linkEl) return;
    const base = window.location.origin + window.location.pathname;
    linkEl.value = `${base}?mode=custom&song=${picker.value}`;
}

function copyCustomLink() {
    const linkEl = $("custom-link");
    const btn = $("copy-link-btn");
    if (!linkEl || !btn) return;
    fallbackCopy(linkEl.value, btn);
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = "Copy Link"; }, 2500);
}

function playCustomSong() {
    const picker = $("song-picker");
    if (!picker) return;
    state.mode = "custom";
    state.customSongId = picker.value;
    setActiveModeButton();
    startRound();
}

function toggleCustomPanel() {
    const panel = $("custom-panel");
    const isOpen = panel.style.display !== "none";
    panel.style.display = isOpen ? "none" : "block";
}

function setActiveModeButton() {
    ["btn-daily", "btn-random", "btn-custom"].forEach(id => {
        const el = $(id); if (el) el.classList.remove("mode-btn-active");
    });
    const activeId = state.mode === "daily" ? "btn-daily" : state.mode === "random" ? "btn-random" : "btn-custom";
    const el = $(activeId); if (el) el.classList.add("mode-btn-active");
}

function switchToDaily() {
    state.mode = "daily"; setActiveModeButton();
    history.replaceState(null, "", window.location.pathname); startRound();
}

function switchToRandom() {
    state.mode = "random"; setActiveModeButton();
    history.replaceState(null, "", window.location.pathname + "?mode=random"); startRound();
}

function updateStats() {
    $("score").textContent = state.score;
    $("streak").textContent = state.streak;
}

function setFeedback(msg, cls) {
    const el = $("feedback");
    el.textContent = msg;
    el.className = ("feedback " + cls).trim();
}

// EVENT LISTENERS
$("play-clue-btn").addEventListener("click", playCurrentClue);
$("submit-btn").addEventListener("click", checkGuess);
$("skip-clue-btn").addEventListener("click", () => {
    if (state.gameOver) return;
    setFeedback("Skipped to next clue.", "");
    advanceClue();
});
$("skip-btn").addEventListener("click", handleSkip);
$("share-btn").addEventListener("click", shareResult);
$("next-btn").addEventListener("click", () => {
    if (state.mode === "daily") { state.mode = "random"; setActiveModeButton(); }
    startRound();
});
$("guess-input").addEventListener("keypress", e => { if (e.key === "Enter") checkGuess(); });

$("btn-daily").addEventListener("click", switchToDaily);
$("btn-random").addEventListener("click", switchToRandom);
$("btn-custom").addEventListener("click", toggleCustomPanel);

$("song-picker").addEventListener("change", refreshCustomLink);
$("copy-link-btn").addEventListener("click", copyCustomLink);
$("play-custom-btn").addEventListener("click", playCustomSong);

loadData();
