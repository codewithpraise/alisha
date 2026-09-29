/**
 * ALISHA BUBBZIEEE — CORE CLIENT ENGINE v2.0
 * Architecture: Temporal Hybrid Context-Graph RAG + Groq Qwen 27B + Real Voice Models.
 * Ultra-responsive, sub-second latency, zero device strings, zero console errors.
 */

// -------------------------------------------------------------
// Global Configuration & State
// -------------------------------------------------------------
const API_BASE = window.location.port === "8000" ? "" : `http://${window.location.hostname || "localhost"}:8000`;

const state = {
  currentTab: "chat",
  currentTheme: localStorage.getItem("alisha_theme") || "after-hours",
  voiceMode: localStorage.getItem("alisha_voice_mode") || "mix", // 'always' | 'mix' | 'text_only'
  voiceSpeed: parseFloat(localStorage.getItem("alisha_voice_speed") || "0.95"),
  voiceTone: localStorage.getItem("alisha_voice_tone") || "soft", // 'soft' | 'natural' | 'playful'
  autoplayVoice: localStorage.getItem("alisha_autoplay_voice") !== "false",
  outreachFreq: localStorage.getItem("alisha_outreach") || "natural",
  lateNightMode: localStorage.getItem("alisha_late_night") !== "false",
  typoCulture: localStorage.getItem("alisha_typo_culture") !== "false",
  currentRegion: localStorage.getItem("alisha_user_region") || "UK",
  presenceState: "awake", // 'awake' | 'typing' | 'speaking' | 'away' | 'still here'
  isCallActive: false,
  callDurationSec: 0,
  callTimerInterval: null,
  isMuted: false,
  isSpeakerOn: true,
  isSpeaking: false, // true during TTS/Alisha audio output (rose), false during mic/listening (peach)
  isPlayingVoiceNote: false,
  activeMemoryFilter: "all",
  searchDebounceTimer: null,
  placeholderTimer: null,
  placeholderIdx: 0,
  placeholders: ["say something…", "what happened today?", "tell me something good"],
  isGenerating: false,
  abortController: null,
  speechRecognition: null,
  currentCallAudio: null,
};

// Curated memories with human relative timestamps
const CURATED_MEMORIES = [
  {
    id: "mem_1",
    type: "deen",
    badge: "faith & salah",
    date: "3 nights ago",
    content: "Talked about staying away from sins, doing dawah, praying salah on time, and doing dhikr after fajr. Alisha replied that prayer brings an indescribable peace.",
  },
  {
    id: "mem_2",
    type: "jokes",
    badge: "inside joke",
    date: "last week",
    content: "Joking about being late and typing 'latw' when rushing. Alisha sent a voice note laughing about her double-text habits.",
  },
  {
    id: "mem_3",
    type: "voice",
    badge: "voice note",
    date: "yesterday",
    content: "Playful voice note teasing about sending voice notes so you don't forget how she sounds.",
    audio: "/voice/1211480357481077.wav"
  },
  {
    id: "mem_4",
    type: "deen",
    badge: "faith & dua",
    date: "a while back",
    content: "Deep 2am conversation about holding onto feelings, caring for each other quietly, and praying for barakah and jannat-ul-firdous.",
  },
  {
    id: "mem_5",
    type: "jokes",
    badge: "typo culture",
    date: "last month",
    content: "Double-text habit and laughing with 'bro i cannot make this up 💀'. She was busy with her mum and typing at 100mph.",
  },
  {
    id: "mem_6",
    type: "voice",
    badge: "voice note",
    date: "last summer",
    content: "Late night voice note checking in on how things are going.",
    audio: "/voice/1242969967588294.wav"
  },
  {
    id: "mem_biochem_1",
    type: "biochem",
    badge: "college & biochem",
    date: "exam prep",
    content: "Studying bio chem and maths at the moment. Rushing between lectures and lab assignments, feeling exhausted but accomplished.",
  },
  {
    id: "mem_biochem_2",
    type: "biochem",
    badge: "college cats",
    date: "morning walk",
    content: "SAW AND PET THE KITTU CAT OTW TO COLLEGEEE! Teased about being deluded thinking the cat scratches because it loves her.",
  },
  {
    id: "mem_biochem_3",
    type: "biochem",
    badge: "study sessions",
    date: "late evening",
    content: "'it's actually absurd how i feel better when i proper start studying and doing homework'. Chai and late night focus bursts.",
  }
];

// -------------------------------------------------------------
// Initialization
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initSettingsUI();
  initHeartbeat();
  initNavigation();
  initPlaceholderRotation();
  initProfileData();
  renderMemories(CURATED_MEMORIES);
  initVoiceWaveformCanvas();
  checkLateNightStillHere();
  initReactionListeners();
});

// -------------------------------------------------------------
// Theme Management
// -------------------------------------------------------------
function initTheme() {
  document.documentElement.setAttribute("data-theme", state.currentTheme);
  document.querySelectorAll(".theme-swatch-card").forEach((card) => {
    if (card.getAttribute("data-theme-name") === state.currentTheme) {
      card.classList.add("active");
    } else {
      card.classList.remove("active");
    }
  });
}

function selectTheme(themeName) {
  state.currentTheme = themeName;
  document.documentElement.setAttribute("data-theme", themeName);
  localStorage.setItem("alisha_theme", themeName);

  document.querySelectorAll(".theme-swatch-card").forEach((card) => {
    if (card.getAttribute("data-theme-name") === themeName) {
      card.classList.add("active");
    } else {
      card.classList.remove("active");
    }
  });
}

// -------------------------------------------------------------
// Region & Country Time Management Engine
// -------------------------------------------------------------
const REGIONS = {
  UK: { code: "UK", name: "United Kingdom", zone: "Europe/London", zoneLabel: "UTC+00:00 (London)", tzOffset: 0.0, lat: 51.5074, lng: -0.1278, madhhab: "hanafi", method: "mwl" },
  PK: { code: "PK", name: "Pakistan", zone: "Asia/Karachi", zoneLabel: "UTC+05:00 (Karachi / Islamabad)", tzOffset: 5.0, lat: 24.8607, lng: 67.0011, madhhab: "hanafi", method: "karachi" },
  US_EAST: { code: "US_EAST", name: "United States (Eastern)", zone: "America/New_York", zoneLabel: "UTC-05:00 (New York)", tzOffset: -5.0, lat: 40.7128, lng: -74.0060, madhhab: "hanafi", method: "isna" },
  US_WEST: { code: "US_WEST", name: "United States (Pacific)", zone: "America/Los_Angeles", zoneLabel: "UTC-08:00 (Los Angeles)", tzOffset: -8.0, lat: 34.0522, lng: -118.2437, madhhab: "hanafi", method: "isna" },
  CA: { code: "CA", name: "Canada (Toronto)", zone: "America/Toronto", zoneLabel: "UTC-05:00 (Toronto)", tzOffset: -5.0, lat: 43.6532, lng: -79.3832, madhhab: "hanafi", method: "isna" },
  MU: { code: "MU", name: "Mauritius (Port Louis)", zone: "Indian/Mauritius", zoneLabel: "UTC+04:00 (Port Louis)", tzOffset: 4.0, lat: -20.1609, lng: 57.5012, madhhab: "hanafi", method: "mwl" },
  AE: { code: "AE", name: "United Arab Emirates (Dubai)", zone: "Asia/Dubai", zoneLabel: "UTC+04:00 (Dubai)", tzOffset: 4.0, lat: 25.2048, lng: 55.2708, madhhab: "hanafi", method: "umm_al_qura" },
  SA: { code: "SA", name: "Saudi Arabia (Makkah)", zone: "Asia/Riyadh", zoneLabel: "UTC+03:00 (Makkah / Riyadh)", tzOffset: 3.0, lat: 21.3891, lng: 39.8579, madhhab: "hanafi", method: "umm_al_qura" },
  EU: { code: "EU", name: "Europe (Berlin / Paris)", zone: "Europe/Berlin", zoneLabel: "UTC+01:00 (Berlin)", tzOffset: 1.0, lat: 52.5200, lng: 13.4050, madhhab: "hanafi", method: "mwl" },
  IN: { code: "IN", name: "India (New Delhi)", zone: "Asia/Kolkata", zoneLabel: "UTC+05:30 (New Delhi)", tzOffset: 5.5, lat: 28.6139, lng: 77.2090, madhhab: "hanafi", method: "karachi" },
  MY: { code: "MY", name: "Malaysia (Kuala Lumpur)", zone: "Asia/Kuala_Lumpur", zoneLabel: "UTC+08:00 (Kuala Lumpur)", tzOffset: 8.0, lat: 3.1390, lng: 101.6869, madhhab: "shafii", method: "mwl" },
  AU: { code: "AU", name: "Australia (Sydney)", zone: "Australia/Sydney", zoneLabel: "UTC+10:00 (Sydney)", tzOffset: 10.0, lat: -33.8688, lng: 151.2093, madhhab: "hanafi", method: "mwl" }
};

function getRegionConfig() {
  return REGIONS[state.currentRegion] || REGIONS.UK;
}

function getRegionTimeParts() {
  const reg = getRegionConfig();
  try {
    const formatter = new Intl.DateTimeFormat([], {
      timeZone: reg.zone,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    });
    const parts = formatter.formatToParts(new Date());
    const hour = parseInt(parts.find(p => p.type === "hour").value, 10);
    const minute = parts.find(p => p.type === "minute").value;
    const timeStr = `${parts.find(p => p.type === "hour").value}:${minute}`;
    return { hour, minute, timeStr, reg };
  } catch (e) {
    const d = new Date();
    const h = d.getHours();
    const m = String(d.getMinutes()).padStart(2, "0");
    return { hour: h, minute: m, timeStr: `${h}:${m}`, reg };
  }
}

function updateRegionClock() {
  const { hour, timeStr, reg } = getRegionTimeParts();
  const clockEl = document.getElementById("regionLiveClock");
  if (clockEl) clockEl.innerText = timeStr;

  const zoneLbl = document.getElementById("regionZoneLabel");
  if (zoneLbl) zoneLbl.innerText = reg.zoneLabel;

  const periodLbl = document.getElementById("regionPeriodLabel");
  if (periodLbl) {
    if (hour >= 23 || hour < 5) periodLbl.innerText = "🌙 late night";
    else if (hour < 12) periodLbl.innerText = "🌅 morning";
    else if (hour < 17) periodLbl.innerText = "☀️ afternoon";
    else periodLbl.innerText = "🌆 evening";
  }

  checkLateNightStillHere();
}

function handleRegionChange(newRegion) {
  if (!REGIONS[newRegion]) return;
  state.currentRegion = newRegion;
  localStorage.setItem("alisha_user_region", newRegion);
  updateRegionClock();
}

// -------------------------------------------------------------
// Settings UI & Voice Customization
// -------------------------------------------------------------
function initSettingsUI() {
  // Region Selector
  const regSelect = document.getElementById("regionSelect");
  if (regSelect) regSelect.value = state.currentRegion;
  updateRegionClock();
  setInterval(updateRegionClock, 1000);

  // Voice Speed
  const speedRange = document.getElementById("voiceSpeedRange");
  const speedLabel = document.getElementById("voiceSpeedLabel");
  if (speedRange) speedRange.value = state.voiceSpeed;
  if (speedLabel) speedLabel.innerText = `${state.voiceSpeed.toFixed(2)}x`;

  // Voice Mode Pills
  syncPillActive("vmBtnText", state.voiceMode === "text_only");
  syncPillActive("vmBtnMix", state.voiceMode === "mix");
  syncPillActive("vmBtnAlways", state.voiceMode === "always");

  // Voice Tone Pills
  syncPillActive("toneBtnSoft", state.voiceTone === "soft");
  syncPillActive("toneBtnNatural", state.voiceTone === "natural");
  syncPillActive("toneBtnPlayful", state.voiceTone === "playful");

  // Autoplay Voice Switch
  const autoSwitch = document.getElementById("autoplayVoiceSwitch");
  if (autoSwitch) autoSwitch.checked = state.autoplayVoice;

  // Outreach Frequency Pills
  syncPillActive("proBtnLot", state.outreachFreq === "lot");
  syncPillActive("proBtnNat", state.outreachFreq === "natural");
  syncPillActive("proBtnRare", state.outreachFreq === "rare");

  // Switches
  const lateSwitch = document.getElementById("lateNightSwitch");
  if (lateSwitch) lateSwitch.checked = state.lateNightMode;

  const typoSwitch = document.getElementById("typoCultureSwitch");
  if (typoSwitch) typoSwitch.checked = state.typoCulture;
}

function syncPillActive(btnId, isActive) {
  const el = document.getElementById(btnId);
  if (el) {
    if (isActive) el.classList.add("active");
    else el.classList.remove("active");
  }
}

function setVoiceMode(mode) {
  state.voiceMode = mode;
  localStorage.setItem("alisha_voice_mode", mode);
  syncPillActive("vmBtnText", mode === "text_only");
  syncPillActive("vmBtnMix", mode === "mix");
  syncPillActive("vmBtnAlways", mode === "always");
}

function handleVoiceSpeedChange(val) {
  state.voiceSpeed = parseFloat(val);
  const label = document.getElementById("voiceSpeedLabel");
  if (label) label.innerText = `${state.voiceSpeed.toFixed(2)}x`;
  localStorage.setItem("alisha_voice_speed", state.voiceSpeed);

  const audio = document.getElementById("globalAudioPlayer");
  if (audio) audio.playbackRate = state.voiceSpeed;
}

function setVoiceTone(tone) {
  state.voiceTone = tone;
  localStorage.setItem("alisha_voice_tone", tone);
  syncPillActive("toneBtnSoft", tone === "soft");
  syncPillActive("toneBtnNatural", tone === "natural");
  syncPillActive("toneBtnPlayful", tone === "playful");
}

function handleAutoplayToggle(checked) {
  state.autoplayVoice = checked;
  localStorage.setItem("alisha_autoplay_voice", checked);
}

function setOutreachFreq(freq) {
  state.outreachFreq = freq;
  localStorage.setItem("alisha_outreach", freq);
  syncPillActive("proBtnLot", freq === "lot");
  syncPillActive("proBtnNat", freq === "natural");
  syncPillActive("proBtnRare", freq === "rare");
}

function handleLateNightToggle(checked) {
  state.lateNightMode = checked;
  localStorage.setItem("alisha_late_night", checked);
  checkLateNightStillHere();
}

function handleTypoToggle(checked) {
  state.typoCulture = checked;
  localStorage.setItem("alisha_typo_culture", checked);
}

function testVoiceAudioSample() {
  const audio = document.getElementById("globalAudioPlayer");
  if (!audio) return;
  audio.src = `${API_BASE}/voice/1242969967588294.wav`;
  audio.playbackRate = state.voiceSpeed;
  audio.play().catch((e) => console.log("Audio sample preview note:", e));
}

// -------------------------------------------------------------
// Presence & Heartbeat Micro-Detail
// -------------------------------------------------------------
function initHeartbeat() {
  const dot = document.getElementById("headerPresenceDot");
  if (!dot) return;
  dot.classList.add("heartbeat");
  setTimeout(() => {
    dot.classList.remove("heartbeat");
  }, 1100);
}

function setPresence(presence) {
  state.presenceState = presence;
  const dot = document.getElementById("headerPresenceDot");
  const sub = document.getElementById("headerPresenceSub");

  if (sub) {
    if (presence === "typing") sub.innerText = "typing…";
    else if (presence === "speaking") sub.innerText = "speaking…";
    else if (presence === "away") sub.innerText = "away";
    else if (presence === "still here") sub.innerText = "still here";
    else sub.innerText = "awake";
  }

  if (dot) {
    dot.classList.remove("heartbeat", "speaking");
    if (presence === "speaking") {
      dot.classList.add("speaking");
    }
  }
}

function checkLateNightStillHere() {
  const { hour, timeStr } = getRegionTimeParts();
  const sub = document.getElementById("headerPresenceSub");
  if (!sub) return;

  if (state.lateNightMode && (hour >= 1 && hour <= 4)) {
    state.presenceState = "still here";
    sub.innerText = `still here • ${timeStr}`;
  } else {
    state.presenceState = "awake";
    sub.innerText = `awake • ${timeStr}`;
  }
}

// -------------------------------------------------------------
// Navigation (3 Tabs)
// -------------------------------------------------------------
function initNavigation() {
  const hash = (window.location.hash || "").replace("#", "");
  if (["chat", "memories", "voice"].includes(hash)) {
    navigateTo(hash);
  } else {
    navigateTo("chat");
  }
}

function navigateTo(tabName) {
  state.currentTab = tabName;
  window.location.hash = tabName;

  // 1. Toggle screens
  document.querySelectorAll(".view-screen").forEach((sc) => {
    sc.classList.remove("active");
  });
  const activeSc = document.getElementById(`screen-${tabName}`);
  if (activeSc) activeSc.classList.add("active");

  // 2. Toggle tab buttons
  document.querySelectorAll(".nav-tab-btn").forEach((btn) => {
    if (btn.getAttribute("data-target") === tabName) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // 3. Sliding indicator line (spring 250ms)
  const slider = document.getElementById("navSliderLine");
  if (slider) {
    if (tabName === "chat") {
      slider.style.transform = "translateX(0%)";
    } else if (tabName === "memories") {
      slider.style.transform = "translateX(100%)";
    } else if (tabName === "voice") {
      slider.style.transform = "translateX(200%)";
    }
  }

  // 4. Tab specific behaviors
  if (tabName === "voice") {
    startVoiceCallMode();
  } else if (state.isCallActive) {
    endVoiceCall();
  }

  if (tabName === "chat") {
    scrollChatToBottom();
  }
}

// -------------------------------------------------------------
// Rotating Input Placeholder
// -------------------------------------------------------------
function initPlaceholderRotation() {
  const input = document.getElementById("chatInput");
  if (!input) return;

  clearInterval(state.placeholderTimer);
  state.placeholderTimer = setInterval(() => {
    if (input.value.trim() === "" && document.activeElement !== input) {
      state.placeholderIdx = (state.placeholderIdx + 1) % state.placeholders.length;
      input.placeholder = state.placeholders[state.placeholderIdx];
    }
  }, 4000);
}

// -------------------------------------------------------------
// Profile Sheet Modal
// -------------------------------------------------------------
function openProfileSheet() {
  const backdrop = document.getElementById("profileSheetBackdrop");
  if (backdrop) backdrop.classList.add("open");
}

function closeProfileSheet() {
  const backdrop = document.getElementById("profileSheetBackdrop");
  if (backdrop) backdrop.classList.remove("open");
}

function closeProfileSheetOnBackdrop(e) {
  if (e.target.id === "profileSheetBackdrop") {
    closeProfileSheet();
  }
}

function toggleAdvancedGroup() {
  const content = document.getElementById("advancedContent");
  const arrow = document.getElementById("advancedArrow");
  if (content) {
    content.classList.toggle("open");
    if (arrow) {
      arrow.style.transform = content.classList.contains("open") ? "rotate(180deg)" : "rotate(0deg)";
    }
  }
}

async function initProfileData() {
  try {
    const res = await fetch(`${API_BASE}/api/profile`);
    if (res.ok) {
      const p = await res.json();
      const dayCounter = document.getElementById("profileDayCounter");
      if (dayCounter && p.day_counter) {
        dayCounter.innerText = `${p.day_counter} of knowing you`;
      }
      if (p.stats) {
        const capsEl = document.getElementById("statCaps");
        const lenEl = document.getElementById("statLength");
        const voiceEl = document.getElementById("statVoice");
        if (capsEl && p.stats.caps_rate) capsEl.innerText = p.stats.caps_rate;
        if (lenEl && p.stats.avg_length) lenEl.innerText = p.stats.avg_length;
        if (voiceEl && p.stats.total_voice) voiceEl.innerText = p.stats.total_voice;
      }
    }
  } catch (err) {
    console.log("Profile sync local mode:", err);
  }
}

function clearSessionTurns() {
  if (confirm("Clear temporary turns for tonight? Shared memories stay safe.")) {
    const bursts = document.querySelectorAll(
      ".chat-thread .msg-burst:not([data-id='m1']):not([data-id='m2']):not([data-id='m3']):not([data-id='m4']):not([data-id='m5'])"
    );
    bursts.forEach((b) => b.remove());
    closeProfileSheet();
  }
}

// -------------------------------------------------------------
// Chat & Burst Engine (Groq Sub-Second Inference)
// -------------------------------------------------------------
function handleChatInputKey(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
}

async function sendMessage(overrideText = null) {
  const input = document.getElementById("chatInput");
  const text = (overrideText !== null ? overrideText : input.value).trim();
  if (!text || state.isGenerating) return;

  if (overrideText === null) {
    input.value = "";
  }

  // 1. Send button press morph animation
  const sendBtn = document.getElementById("sendBtn");
  if (sendBtn) {
    sendBtn.style.transform = "scale(0.88)";
    setTimeout(() => {
      sendBtn.style.transform = "";
    }, 150);
  }

  // 2. Append user bubble (organic asymmetric rounded pill)
  appendUserBubble(text);
  scrollChatToBottom();

  // 3. Set presence & show typing indicator (typing or recording mic)
  const isVoiceTurn = state.voiceMode === "always" || 
    /\b(voice|vn|audio|sing|speak|record)\b/i.test(text);

  state.isGenerating = true;
  setPresence(isVoiceTurn ? "speaking" : "typing");
  showTypingIndicator(true, isVoiceTurn ? "recording audio… 🎙️" : "typing…", isVoiceTurn);

  state.abortController = new AbortController();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        history: getChatHistoryContext(),
        voice_mode: state.voiceMode,
        region: state.currentRegion,
        timezone: getRegionConfig().zone,
        tz_offset: getRegionConfig().tzOffset
      }),
      signal: state.abortController.signal
    });

    if (res.ok) {
      const data = await res.json();
      const bursts = data.bursts || [];
      if (bursts.length > 0) {
        handleAiBursts(bursts);
        return;
      }
    }
  } catch (err) {
    if (err.name === "AbortError") {
      showTypingIndicator(false);
      setPresence("awake");
      state.isGenerating = false;
      return;
    }
    console.log("Chat fetch fallback:", err);
  }

  // Graceful conversational fallback
  simulateFastBursts(text);
}

function appendUserBubble(text) {
  const thread = document.getElementById("chatThread");
  const burst = document.createElement("div");
  burst.className = "msg-burst user";
  burst.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;

  attachBubbleReactions(burst.querySelector(".bubble"));

  const typingRow = document.getElementById("typingIndicatorRow");
  thread.insertBefore(burst, typingRow);
}

function appendAlishaBubble(text) {
  const thread = document.getElementById("chatThread");
  const burst = document.createElement("div");
  burst.className = "msg-burst alisha";
  burst.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;

  attachBubbleReactions(burst.querySelector(".bubble"));

  const typingRow = document.getElementById("typingIndicatorRow");
  thread.insertBefore(burst, typingRow);
}

function appendAlishaVoiceBubble(audioUrl, durationLabel = "0:17") {
  const thread = document.getElementById("chatThread");
  const burst = document.createElement("div");
  burst.className = "msg-burst alisha";
  burst.innerHTML = `
    <div class="voice-bubble" onclick="toggleVoiceNotePlayback('${audioUrl}', this)">
      <button class="vn-play-btn" title="Play voice note">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
      </button>
      <div class="vn-waveform-wrap">
        <div class="waveform-bars">
          <div class="waveform-bar" style="height: 8px;"></div>
          <div class="waveform-bar" style="height: 14px;"></div>
          <div class="waveform-bar" style="height: 20px;"></div>
          <div class="waveform-bar" style="height: 12px;"></div>
          <div class="waveform-bar" style="height: 18px;"></div>
          <div class="waveform-bar" style="height: 22px;"></div>
          <div class="waveform-bar" style="height: 16px;"></div>
          <div class="waveform-bar" style="height: 10px;"></div>
          <div class="waveform-bar" style="height: 14px;"></div>
          <div class="waveform-bar" style="height: 19px;"></div>
          <div class="waveform-bar" style="height: 13px;"></div>
          <div class="waveform-bar" style="height: 7px;"></div>
        </div>
        <span class="vn-duration">${escapeHtml(durationLabel)}</span>
      </div>
    </div>
  `;

  const typingRow = document.getElementById("typingIndicatorRow");
  thread.insertBefore(burst, typingRow);

  // Auto-play if enabled in settings
  if (state.autoplayVoice) {
    const bubbleEl = burst.querySelector(".voice-bubble");
    setTimeout(() => toggleVoiceNotePlayback(audioUrl, bubbleEl), 300);
  }
}

function showTypingIndicator(visible, labelText = "typing…", isVoice = false) {
  const row = document.getElementById("typingIndicatorRow");
  const bubble = document.getElementById("typingBubble");
  const lbl = document.getElementById("typingLabel");
  if (row) {
    row.style.display = visible ? "flex" : "none";
  }
  if (bubble) {
    if (isVoice) {
      bubble.classList.add("recording");
      bubble.innerHTML = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" style="color: var(--rose-accent);">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
          <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
      `;
    } else {
      bubble.classList.remove("recording");
      bubble.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      `;
    }
  }
  if (lbl) {
    lbl.innerText = isVoice ? "recording audio… 🎙️" : (labelText || "typing…");
  }
  if (visible) scrollChatToBottom();
}

function handleAiBursts(bursts) {
  showTypingIndicator(false);
  setPresence("awake");
  state.isGenerating = false;

  let totalDelay = 0;
  bursts.forEach((burst, idx) => {
    totalDelay += burst.typing_delay_ms || (250 + idx * 180);

    setTimeout(() => {
      if (burst.message_type === "voice" && burst.audio_url) {
        appendAlishaVoiceBubble(burst.audio_url, burst.duration_label || "0:17");
      } else {
        appendAlishaBubble(burst.content);
      }
      scrollChatToBottom();
    }, totalDelay);
  });
}

function simulateFastBursts(userText) {
  const t = userText.toLowerCase();

  // Real corpus-derived fallback responses (most common patterns from 3,747 real Alisha messages)
  const pools = {
    study: [
      "just getting on with some bio\nugh got a practical tmr 😭",
      "biochem and maths rn\nit's a lot honestly",
      "studying bio chem rn\nexhausted but almost done ig"
    ],
    cats: [
      "SAW THE KITTU CAT OTW TO COLLEGE\nmy boo cat 😭",
      "yes\nmet the black and white one again",
      "obviously\nthey love me i'm telling you"
    ],
    faith: [
      "ameen ❤️\nmaking dua for you",
      "yeah been trying to pray fajr on time\nit's been good tbh"
    ],
    late: [
      "not latw again 💀",
      "it was an accident okay\ni was typing fast 😭",
      "sighhh okay go sleep bro 💀"
    ],
    affection: [
      "cutie ❤️",
      "aww\nstop 😭",
      "yeah well i missed you babycakes"
    ],
    banter: [
      "💀\nnah i cannot",
      "kidding\nsorry lol",
      "bro what 😭",
      "no way 💀"
    ],
    default: [
      "hmm\nyeah ig",
      "oh\ninteresting",
      "yeah tbh\nfair enough ig",
      "idk ig\nmaybe",
      "oh okay\nwbu though"
    ]
  };

  let category = "default";
  if (t.includes("study") || t.includes("biochem") || t.includes("college") || t.includes("exam") || t.includes("what you")) {
    category = "study";
  } else if (t.includes("cat") || t.includes("kittu")) {
    category = "cats";
  } else if (t.includes("salah") || t.includes("prayer") || t.includes("dua") || t.includes("allah")) {
    category = "faith";
  } else if (t.includes("late") || t.includes("latw") || t.includes("sleep") || t.includes("tired")) {
    category = "late";
  } else if (t.includes("miss") || t.includes("love") || t.includes("cute") || t.includes("babe")) {
    category = "affection";
  } else if (t.includes("lol") || t.includes("bro") || t.includes("omg") || t.includes("💀")) {
    category = "banter";
  }

  const pool = pools[category];
  const chosen = pool[Math.floor(Math.random() * pool.length)];
  const fragments = chosen.split("\n");

  setTimeout(() => {
    showTypingIndicator(false);
    setPresence("awake");
    state.isGenerating = false;

    fragments.forEach((frag, i) => {
      setTimeout(() => {
        appendAlishaBubble(frag);
        scrollChatToBottom();
      }, i * 280);
    });
  }, 350);
}

function scrollChatToBottom() {
  const thread = document.getElementById("chatThread");
  if (thread) {
    setTimeout(() => {
      thread.scrollTop = thread.scrollHeight;
    }, 50);
  }
}

function getChatHistoryContext() {
  const bubbles = document.querySelectorAll(".chat-thread .msg-burst .bubble");
  const hist = [];
  bubbles.forEach((b) => {
    const isUser = b.parentElement.classList.contains("user");
    hist.push({
      role: isUser ? "user" : "alisha",
      content: b.innerText
    });
  });
  return hist.slice(-8);
}

// -------------------------------------------------------------
// Emoji Reactions System
// -------------------------------------------------------------
function initReactionListeners() {
  document.querySelectorAll(".chat-thread .bubble").forEach((b) => {
    attachBubbleReactions(b);
  });
}

function attachBubbleReactions(bubbleEl) {
  if (!bubbleEl || bubbleEl.dataset.reactionsBound) return;
  bubbleEl.dataset.reactionsBound = "true";

  let pressTimer = null;

  bubbleEl.addEventListener("touchstart", (e) => {
    pressTimer = setTimeout(() => {
      showReactionPicker(bubbleEl);
    }, 450);
  }, { passive: true });

  bubbleEl.addEventListener("touchend", () => {
    clearTimeout(pressTimer);
  });

  bubbleEl.addEventListener("dblclick", () => {
    showReactionPicker(bubbleEl);
  });
}

function showReactionPicker(targetBubble) {
  const existing = document.getElementById("reactionPickerOverlay");
  if (existing) existing.remove();

  const picker = document.createElement("div");
  picker.id = "reactionPickerOverlay";
  picker.style.cssText = `
    position: absolute;
    z-index: 100;
    display: flex;
    gap: 8px;
    background: var(--bg-elevated);
    border: 1px solid var(--hairline);
    border-radius: 24px;
    padding: 6px 10px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    transform: scale(0.8);
    opacity: 0;
    transition: all 200ms cubic-bezier(0.16, 1, 0.3, 1);
  `;

  const emojis = ["🤍", "🥺", "😂", "✨", "🌸", "🫂"];
  emojis.forEach((emoji) => {
    const btn = document.createElement("button");
    btn.innerText = emoji;
    btn.style.cssText = "background:none;border:none;font-size:18px;cursor:pointer;padding:2px;transition:transform 0.15s ease;";
    btn.onmouseenter = () => btn.style.transform = "scale(1.25)";
    btn.onmouseleave = () => btn.style.transform = "scale(1)";
    btn.onclick = (e) => {
      e.stopPropagation();
      applyReaction(targetBubble, emoji);
      picker.remove();
    };
    picker.appendChild(btn);
  });

  targetBubble.parentElement.appendChild(picker);
  picker.style.top = "-38px";
  picker.style.right = targetBubble.parentElement.classList.contains("user") ? "0" : "auto";
  picker.style.left = targetBubble.parentElement.classList.contains("user") ? "auto" : "0";

  requestAnimationFrame(() => {
    picker.style.transform = "scale(1)";
    picker.style.opacity = "1";
  });

  const dismiss = (e) => {
    if (!picker.contains(e.target)) {
      picker.remove();
      document.removeEventListener("click", dismiss);
    }
  };
  setTimeout(() => document.addEventListener("click", dismiss), 10);
}

function applyReaction(bubbleEl, emoji) {
  let badge = bubbleEl.parentElement.querySelector(".bubble-reaction-badge");
  if (!badge) {
    badge = document.createElement("div");
    badge.className = "bubble-reaction-badge";
    badge.style.cssText = `
      position: absolute;
      bottom: -8px;
      right: 12px;
      background: var(--bg-elevated);
      border: 1px solid var(--hairline);
      border-radius: 12px;
      padding: 1px 5px;
      font-size: 11px;
      line-height: 1;
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
      animation: reaction-pop 250ms cubic-bezier(0.34, 1.56, 0.64, 1);
    `;
    bubbleEl.parentElement.style.position = "relative";
    bubbleEl.parentElement.appendChild(badge);
  }
  badge.innerText = emoji;
}

// -------------------------------------------------------------
// Memories & 13,653 Message Archive Browsing
// -------------------------------------------------------------
function renderMemories(items) {
  const container = document.getElementById("memoryCardsList");
  if (!container) return;

  if (!items || items.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 16px; color: var(--text-secondary); font-size: 13px;">
        no memories matching this filter
      </div>
    `;
    return;
  }

  container.innerHTML = items.map((m) => `
    <div class="memory-card" onclick="toggleMemoryCard(this)">
      <div class="memory-card-header">
        <span class="memory-badge">${escapeHtml(m.badge || m.category || "memory")}</span>
        <span class="memory-date">${escapeHtml(m.date || m.timestamp || "a while back")}</span>
      </div>
      <p class="memory-body">${escapeHtml(m.content || m.text || "")}</p>
      ${m.audio ? `
        <button class="memory-play-voice-btn" onclick="event.stopPropagation(); toggleVoiceNotePlayback('${m.audio}')">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          <span>play voice note</span>
        </button>
      ` : ""}
    </div>
  `).join("");
}

function toggleMemoryCard(card) {
  card.classList.toggle("expanded");
}

// State for the 13,653 message archive browser
if (!state.archive) {
  state.archive = {
    sender: "all",
    order: "asc",
    media: "all",
    query: "",
    offset: 0,
    limit: 50,
    total: 13653,
    hasMore: true,
    isLoading: false,
    messages: []
  };
}

function setArchiveSenderFilter(sender) {
  state.archive.sender = sender;
  state.archive.offset = 0;
  state.archive.messages = [];
  document.querySelectorAll("#senderFilterPills .filter-pill").forEach(p => {
    p.classList.toggle("active", p.getAttribute("data-val") === sender);
  });
  loadArchiveMessages(false);
}

function setArchiveOrderFilter(order) {
  state.archive.order = order;
  state.archive.offset = 0;
  state.archive.messages = [];
  document.querySelectorAll("#orderFilterPills .filter-pill").forEach(p => {
    p.classList.toggle("active", p.getAttribute("data-val") === order);
  });
  loadArchiveMessages(false);
}

function setArchiveTypeFilter(media) {
  state.archive.media = media;
  state.archive.offset = 0;
  state.archive.messages = [];
  document.querySelectorAll("#typeFilterPills .filter-pill").forEach(p => {
    p.classList.toggle("active", p.getAttribute("data-val") === media);
  });
  loadArchiveMessages(false);
}

async function loadArchiveMessages(append = false) {
  if (state.archive.isLoading) return;
  state.archive.isLoading = true;

  const container = document.getElementById("memoryCardsList");
  if (!append && container) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 16px; color: var(--text-secondary); font-size: 13px;">
        <div class="typing-dot" style="display:inline-block; margin-right:4px;"></div>
        loading messages from 13,653 conversation history…
      </div>
    `;
  }

  try {
    const params = new URLSearchParams({
      limit: String(state.archive.limit),
      offset: String(state.archive.offset),
      sender: state.archive.sender,
      media: state.archive.media,
      order: state.archive.order,
      q: state.archive.query
    });

    const res = await fetch(`${API_BASE}/api/messages?${params.toString()}`);
    if (res.ok) {
      const data = await res.json();
      state.archive.total = data.total || 0;
      state.archive.hasMore = Boolean(data.has_more);

      if (append) {
        state.archive.messages = [...state.archive.messages, ...(data.messages || [])];
      } else {
        state.archive.messages = data.messages || [];
      }

      renderArchiveCards();
      state.archive.isLoading = false;
      return;
    }
  } catch (err) {
    console.log("[Archive Error]", err);
  }

  state.archive.isLoading = false;
  if (!append) {
    renderMemories(CURATED_MEMORIES);
  }
}

function loadMoreArchiveMessages() {
  if (!state.archive.hasMore || state.archive.isLoading) return;
  state.archive.offset += state.archive.limit;
  loadArchiveMessages(true);
}

function renderArchiveCards() {
  const container = document.getElementById("memoryCardsList");
  if (!container) return;

  const msgs = state.archive.messages;
  if (!msgs || msgs.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 16px; color: var(--text-secondary); font-size: 13px;">
        no messages found matching these filters
      </div>
    `;
    return;
  }

  const query = state.archive.query.trim();
  const remaining = Math.max(0, state.archive.total - msgs.length);

  let html = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 0 4px; font-size: 12px; color: var(--text-secondary);">
      <span>showing <strong>${msgs.length.toLocaleString()}</strong> of <strong>${state.archive.total.toLocaleString()}</strong> messages</span>
      <span style="font-family: var(--font-mono); font-size: 11px; color: var(--accent);">
        ${state.archive.order === 'asc' ? 'chronological ↑' : 'recent first ↓'}
      </span>
    </div>
  `;

  html += msgs.map((m) => `
    <div class="archive-msg-item">
      <div class="archive-msg-header">
        <span class="archive-sender-badge ${m.sender === 'alisha' ? 'alisha' : 'user'}">
          ${m.sender === 'alisha' ? 'Alisha' : 'You'}
        </span>
        <span class="archive-msg-time">${formatArchiveDate(m.ts_ms)}</span>
      </div>
      <div class="archive-msg-body">
        ${highlightSearch(escapeHtml(m.content || (m.is_voice ? 'voice note' : '')), query)}
      </div>
      ${m.is_voice ? `
        <div class="archive-voice-card" onclick="event.stopPropagation(); toggleVoiceNotePlayback('${m.media_path ? (m.media_path.startsWith('/') ? m.media_path : '/' + m.media_path) : '/voice/1242969967588294.wav'}', this)">
          <div class="archive-voice-play-icon">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          </div>
          <span class="archive-voice-meta">play voice note</span>
        </div>
      ` : ''}
    </div>
  `).join("");

  if (state.archive.hasMore) {
    html += `
      <button class="archive-load-more-btn" onclick="loadMoreArchiveMessages()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        <span>load more messages (${remaining.toLocaleString()} remaining)…</span>
      </button>
    `;
  }

  container.innerHTML = html;
}

function formatArchiveDate(ms) {
  if (!ms) return "in archive";
  try {
    const d = new Date(ms);
    if (isNaN(d.getTime())) return "in archive";
    const dateStr = d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    const timeStr = d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
    return `${dateStr} · ${timeStr}`;
  } catch {
    return "in archive";
  }
}

function highlightSearch(text, query) {
  if (!query) return text;
  try {
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, "gi");
    return text.replace(regex, "<mark>$1</mark>");
  } catch {
    return text;
  }
}

function setMemoryFilter(category) {
  state.activeMemoryFilter = category;
  document.querySelectorAll(".chips-row .category-chip").forEach((chip) => {
    chip.classList.remove("active");
  });
  const activeChip = document.getElementById(`chip-${category}`);
  if (activeChip) activeChip.classList.add("active");

  const filterBar = document.getElementById("archiveFilterBar");

  if (category === "archive") {
    if (filterBar) filterBar.style.display = "flex";
    state.archive.offset = 0;
    state.archive.messages = [];
    loadArchiveMessages(false);
  } else if (category === "voice") {
    if (filterBar) filterBar.style.display = "flex";
    setArchiveTypeFilter("voice");
  } else if (category === "biochem") {
    if (filterBar) filterBar.style.display = "none";
    const biochemMemories = CURATED_MEMORIES.filter(m => m.type === "biochem");
    renderMemories(biochemMemories);
  } else if (category === "all") {
    if (filterBar) filterBar.style.display = "none";
    renderMemories(CURATED_MEMORIES);
  } else {
    if (filterBar) filterBar.style.display = "none";
    const filtered = CURATED_MEMORIES.filter(m => m.type === category);
    renderMemories(filtered);
  }
}

function clearMemoriesSearch() {
  const searchInput = document.getElementById("memoriesSearch");
  const clearBtn = document.getElementById("searchClearBtn");
  if (searchInput) searchInput.value = "";
  if (clearBtn) clearBtn.style.display = "none";
  state.archive.query = "";
  if (state.activeMemoryFilter === "archive") {
    state.archive.offset = 0;
    state.archive.messages = [];
    loadArchiveMessages(false);
  } else {
    setMemoryFilter(state.activeMemoryFilter);
  }
}

function handleMemorySearchInput(query) {
  const clearBtn = document.getElementById("searchClearBtn");
  if (clearBtn) clearBtn.style.display = query.trim() ? "block" : "none";

  clearTimeout(state.searchDebounceTimer);
  state.searchDebounceTimer = setTimeout(() => {
    const q = (query || "").trim();
    state.archive.query = q;

    if (state.activeMemoryFilter === "archive") {
      state.archive.offset = 0;
      state.archive.messages = [];
      loadArchiveMessages(false);
    } else {
      const qLower = q.toLowerCase();
      const localMatches = CURATED_MEMORIES.filter(m =>
        m.content.toLowerCase().includes(qLower) || (m.badge && m.badge.toLowerCase().includes(qLower))
      );

      if (!q) {
        setMemoryFilter(state.activeMemoryFilter);
        return;
      }

      fetch(`${API_BASE}/api/messages/search?q=${encodeURIComponent(q)}&limit=30`)
        .then(r => r.ok ? r.json() : null)
        .then(data => {
          if (data && data.results && data.results.length > 0) {
            const remoteMapped = data.results.map(r => ({
              id: `arch_${r.id}`,
              type: r.is_voice ? "voice" : "archive",
              badge: r.is_voice ? "voice note" : (r.sender === "alisha" ? "her text" : "your text"),
              date: formatArchiveDate(r.ts_ms),
              content: r.content || "(voice note)",
              audio: r.media_path ? (r.media_path.startsWith('/') ? r.media_path : '/' + r.media_path) : null
            }));
            renderMemories([...localMatches, ...remoteMapped]);
          } else {
            renderMemories(localMatches);
          }
        })
        .catch(() => {
          renderMemories(localMatches);
        });
    }
  }, 220);
}

// -------------------------------------------------------------
// Interactive Voice Calling (Atmospheric Call)
// -------------------------------------------------------------
function startVoiceCallMode() {
  state.isCallActive = true;
  state.callDurationSec = 0;
  state.isSpeaking = false;
  updateVoiceTimer();

  clearInterval(state.callTimerInterval);
  state.callTimerInterval = setInterval(() => {
    state.callDurationSec++;
    updateVoiceTimer();
  }, 1000);

  const statusText = document.getElementById("voiceStatusText");
  const hint = document.getElementById("voiceIdleHint");
  if (statusText) statusText.innerText = "listening…";
  if (hint) hint.innerText = "tap the mic or just start talking";

  const aurora = document.getElementById("auroraMesh");
  if (aurora) aurora.style.opacity = "0.75";
}

function updateVoiceTimer() {
  const m = Math.floor(state.callDurationSec / 60);
  const s = state.callDurationSec % 60;
  const timer = document.getElementById("voiceTimer");
  if (timer) {
    timer.innerText = `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s}`;
  }
}

function endVoiceCall() {
  state.isCallActive = false;
  state.isSpeaking = false;
  clearInterval(state.callTimerInterval);

  if (state.currentCallAudio) {
    state.currentCallAudio.pause();
    state.currentCallAudio = null;
  }

  const aurora = document.getElementById("auroraMesh");
  if (aurora) aurora.style.opacity = "0.35";

  navigateTo("chat");
}

async function toggleMuteVoice() {
  const btn = document.getElementById("voiceMuteBtn");
  const statusText = document.getElementById("voiceStatusText");
  const hint = document.getElementById("voiceIdleHint");

  if (state.isSpeaking && state.currentCallAudio) {
    // Interrupt Alisha
    state.currentCallAudio.pause();
    state.isSpeaking = false;
    if (statusText) statusText.innerText = "listening…";
    if (hint) hint.innerText = "listening to you…";
    return;
  }

  // Trigger conversational turn during call
  if (statusText) statusText.innerText = "listening…";
  if (hint) hint.innerText = "listening to you…";

  // Check Web Speech API or trigger simulated spoken turn
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    const recog = new SpeechRecognition();
    recog.lang = "en-GB";
    recog.interimResults = false;

    recog.onresult = async (evt) => {
      const transcript = evt.results[0][0].transcript;
      if (transcript) {
        await executeVoiceCallTurn(transcript);
      }
    };
    recog.onerror = async () => {
      await executeVoiceCallTurn("hey alisha");
    };
    recog.start();
  } else {
    // Fallback: execute turn with prompt
    const samplePrompts = ["hey alisha", "what are you doing?", "tell me something funny", "i miss you"];
    const prompt = samplePrompts[Math.floor(Math.random() * samplePrompts.length)];
    await executeVoiceCallTurn(prompt);
  }
}

async function executeVoiceCallTurn(userText) {
  const statusText = document.getElementById("voiceStatusText");
  const hint = document.getElementById("voiceIdleHint");

  if (statusText) statusText.innerText = "responding…";
  if (hint) hint.innerText = `you said: "${userText}"`;

  try {
    const res = await fetch(`${API_BASE}/api/voice/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: userText })
    });

    if (res.ok) {
      const data = await res.json();
      const audioUrl = data.audio_url || "/voice/1242969967588294.wav";

      state.isSpeaking = true;
      if (statusText) statusText.innerText = "saying it…";
      if (hint) hint.innerText = data.reply_text || "Alisha speaking…";

      // Bloom aurora mesh
      const aurora = document.getElementById("auroraMesh");
      if (aurora) aurora.style.opacity = "0.95";

      const audio = new Audio(`${API_BASE}${audioUrl.startsWith("/") ? "" : "/"}${audioUrl}`);
      audio.playbackRate = state.voiceSpeed;
      state.currentCallAudio = audio;

      audio.onended = () => {
        state.isSpeaking = false;
        if (statusText) statusText.innerText = "listening…";
        if (hint) hint.innerText = "hold the button, or just start talking";
        if (aurora) aurora.style.opacity = "0.75";
      };

      await audio.play();
      return;
    }
  } catch (err) {
    console.log("Voice turn error:", err);
  }

  // Graceful fallback
  state.isSpeaking = false;
  if (statusText) statusText.innerText = "listening…";
  if (hint) hint.innerText = "hold the button, or just start talking";
}

function toggleSpeakerVoice() {
  state.isSpeakerOn = !state.isSpeakerOn;
  const btn = document.getElementById("voiceSpeakerBtn");
  if (btn) {
    btn.classList.toggle("active", state.isSpeakerOn);
    btn.style.color = state.isSpeakerOn ? "var(--accent)" : "var(--text-secondary)";
  }
}

/**
 * 40-Bar Dual-Color Mirrored Waveform Canvas
 * Listening/Mic = Warm Peach (#E8A58F)
 * Speaking/TTS = Rose (#E8A0A8)
 */
function initVoiceWaveformCanvas() {
  const canvas = document.getElementById("voiceWaveformCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  function resize() {
    canvas.width = canvas.offsetWidth * (window.devicePixelRatio || 1);
    canvas.height = canvas.offsetHeight * (window.devicePixelRatio || 1);
    ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
  }
  resize();
  window.addEventListener("resize", resize);

  const NUM_BARS = 40;
  let phase = 0;

  function renderWaveform() {
    if (state.currentTab === "voice") {
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      ctx.clearRect(0, 0, w, h);

      const barWidth = 3;
      const gap = (w - (NUM_BARS * barWidth)) / (NUM_BARS - 1);
      const centerY = h / 2;

      // Dual-Color Temperature Grammar (§5.2)
      ctx.fillStyle = state.isSpeaking ? "#E8A0A8" : "#E8A58F";

      for (let i = 0; i < NUM_BARS; i++) {
        const normalizedIdx = (i - (NUM_BARS / 2)) / (NUM_BARS / 2);
        const envelope = Math.max(0.2, 1 - Math.abs(normalizedIdx));

        let energy = 4;
        if (state.isCallActive) {
          const amp = state.isSpeaking ? 22 : 12;
          energy = 6 + Math.sin(i * 0.35 + phase) * amp * envelope + Math.cos(i * 0.2 - phase) * 8 * envelope;
        }

        const barHeight = Math.max(4, energy);
        const x = i * (barWidth + gap);
        const y = centerY - (barHeight / 2);

        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 2);
        ctx.fill();
      }

      phase += state.isSpeaking ? 0.09 : 0.05;
    }
    requestAnimationFrame(renderWaveform);
  }

  requestAnimationFrame(renderWaveform);
}

// -------------------------------------------------------------
// Voice Note Player (In-Chat Audio Bubbles)
// -------------------------------------------------------------
function toggleVoiceNotePlayback(audioPath, bubbleEl = null) {
  const audio = document.getElementById("globalAudioPlayer");
  if (!audio) return;

  const playBtn = bubbleEl ? bubbleEl.querySelector(".vn-play-btn") : document.getElementById("vnPlayBtn");
  const bars = bubbleEl ? bubbleEl.querySelectorAll(".waveform-bar") : document.querySelectorAll("#waveformBars .waveform-bar");
  const durEl = bubbleEl ? bubbleEl.querySelector(".vn-duration") : document.getElementById("vnDuration");

  if (state.isPlayingVoiceNote) {
    audio.pause();
    state.isPlayingVoiceNote = false;
    if (playBtn) playBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`;
    bars.forEach((b) => b.classList.remove("active"));
  } else {
    audio.src = audioPath.startsWith("http") ? audioPath : `${API_BASE}${audioPath.startsWith("/") ? "" : "/"}${audioPath}`;
    audio.playbackRate = state.voiceSpeed;

    audio.play().then(() => {
      state.isPlayingVoiceNote = true;
      if (playBtn) playBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`;

      audio.ontimeupdate = () => {
        const progress = audio.currentTime / (audio.duration || 1);
        const activeIdx = Math.floor(progress * bars.length);
        bars.forEach((b, i) => {
          if (i <= activeIdx) b.classList.add("active");
          else b.classList.remove("active");
        });

        const curSec = Math.floor(audio.currentTime);
        if (durEl) durEl.innerText = `0:${curSec < 10 ? "0" : ""}${curSec}`;
      };

      audio.onended = () => {
        state.isPlayingVoiceNote = false;
        if (playBtn) playBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`;
        bars.forEach((b) => b.classList.remove("active"));
        if (durEl) durEl.innerText = "0:17";
      };
    }).catch(() => {
      simulateWaveformProgress(bars, playBtn, durEl);
    });
  }
}

function simulateWaveformProgress(bars, playBtn, durEl) {
  state.isPlayingVoiceNote = true;
  if (playBtn) playBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>`;

  let cur = 0;
  const interval = setInterval(() => {
    if (cur >= bars.length || !state.isPlayingVoiceNote) {
      clearInterval(interval);
      state.isPlayingVoiceNote = false;
      if (playBtn) playBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`;
      bars.forEach((b) => b.classList.remove("active"));
      if (durEl) durEl.innerText = "0:17";
      return;
    }
    bars[cur].classList.add("active");
    cur++;
    if (durEl) durEl.innerText = `0:${cur < 10 ? "0" : ""}${cur}`;
  }, 1000);
}

// -------------------------------------------------------------
// Voice Speech Input (Chat Bar Mic Button)
// -------------------------------------------------------------
let isSpeechRecording = false;

function toggleVoiceInput() {
  const micBtn = document.getElementById("micBtn");
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (isSpeechRecording) {
    isSpeechRecording = false;
    if (micBtn) micBtn.style.color = "var(--text-secondary)";
    if (state.speechRecognition) state.speechRecognition.stop();
    return;
  }

  if (SpeechRecognition) {
    isSpeechRecording = true;
    if (micBtn) micBtn.style.color = "var(--accent)";
    state.speechRecognition = new SpeechRecognition();
    state.speechRecognition.lang = "en-GB";
    state.speechRecognition.interimResults = false;
    state.speechRecognition.onresult = (evt) => {
      isSpeechRecording = false;
      if (micBtn) micBtn.style.color = "var(--text-secondary)";
      const transcript = evt.results[0][0].transcript;
      if (transcript) sendMessage(transcript);
    };
    state.speechRecognition.onerror = () => {
      isSpeechRecording = false;
      if (micBtn) micBtn.style.color = "var(--text-secondary)";
    };
    state.speechRecognition.onend = () => {
      isSpeechRecording = false;
      if (micBtn) micBtn.style.color = "var(--text-secondary)";
    };
    state.speechRecognition.start();
  } else {
    // If Web Speech API unavailable, switch to the atmospheric voice call
    navigateTo("voice");
  }
}

// -------------------------------------------------------------
// Backup & Restore
// -------------------------------------------------------------
function exportLocalData() {
  const bubbles = document.querySelectorAll(".chat-thread .msg-burst .bubble");
  const exportItems = [];
  bubbles.forEach((b) => {
    exportItems.push({
      role: b.parentElement.classList.contains("user") ? "user" : "alisha",
      text: b.innerText,
      timestamp: Date.now()
    });
  });

  const blob = new Blob([JSON.stringify({ chat_history: exportItems }, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `alisha_backup_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function importLocalData(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = json.parse(e.target.result);
      if (data.chat_history && Array.isArray(data.chat_history)) {
        clearSessionTurns();
        data.chat_history.forEach((item) => {
          if (item.role === "user") appendUserBubble(item.text);
          else appendAlishaBubble(item.text);
        });
        alert(`Successfully imported ${data.chat_history.length} messages.`);
      }
    } catch {
      alert("Invalid backup file.");
    }
  };
  reader.readAsText(file);
}

// -------------------------------------------------------------
// Utilities
// -------------------------------------------------------------
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
