// static/js/autopilot/storage.js

const STORAGE_KEY = "myPluginState";

export function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function loadState() {
  const state = localStorage.getItem(STORAGE_KEY);
  return state ? JSON.parse(state) : {};
}
