// static/js/autopilot/main.js

import {
  createButton,
  createAutoPilotButton,
  createStateDisplay,
  createEventComponent,
} from "./components.js";
import { saveState, loadState } from "./storage.js";

document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".container");
  const autopilotContainer = document.getElementById("autopilot");
  const quickKeysContainer = document.getElementById("quick-keys");
  const stateDisplay = document.getElementById("state-display");
  const eventsContainer = document.getElementById("events-container");
  const addEventButton = document.getElementById("add-event");

  const synth = window.speechSynthesis;
  let state = loadState();

  // Initialize events array if it doesn't exist
  if (!state.events) {
    state.events = [];
    saveState(state);
  }

  const obs = new OBSWebSocket();
  connect(obs);

  const autopilotButton = createAutoPilotButton("Enabled", () => {
    toggleAutoPilot(autopilotButton);
  });
  autopilotContainer.appendChild(autopilotButton);
  //if the initial button state doesn't match the state, toggle the autopilot button
  if (state.enabled !== autopilotButton.dataset.enabled) {
    toggleAutoPilot(autopilotButton);
  }

  function toggleAutoPilot(button) {
    const isEnabled = button.dataset.enabled === "true";

    if (isEnabled) {
      button.style =
        "background: radial-gradient(circle,#ff4c4c 0%,rgba(255, 255, 255, 1) 100%);";
      button.querySelector(".mb-2").innerText = "Disabled";
    } else {
      button.style =
        "background: radial-gradient(circle,#6bfca0f9 0%,rgba(255, 255, 255, 1) 100%);";
      button.querySelector(".mb-2").innerText = "Enabled";
    }

    button.dataset.enabled = !isEnabled;
    state.enabled = button.dataset.enabled;
    saveState(state);
    updateStateDisplay(stateDisplay, state);
  }

  updateStateDisplay(stateDisplay, state);

  const quickKeys = [
    { label: "1", colorClass: "bg-red-500" },
    { label: "2", colorClass: "bg-green-500" },
    { label: "3", colorClass: "bg-blue-500" },
    { label: "4", colorClass: "bg-yellow-500" },
  ];

  const actionOptionTypes = ["text", "number", "checkbox"];
  const actions = [
    { value: "blank", label: "Blank", params: [] },
    {
      value: "alert",
      label: "Alert",
      params: [{ label: "Text", type: "text" }],
    },
    {
      value: "speak",
      label: "Speak",
      params: [
        { label: "Text", type: "text" },
        //TO-DO allow for voice selection
        // {
        //   label: "Voice",
        //   type: "select",
        //   options: [],
        // },
      ],
    },
    {
      value: "rhScheduleRace",
      label: "RH - Schedule Race",
      params: [{ label: "Start Delay", type: "number" }],
    },
    {
      value: "obsSetScene",
      label: "OBS - Set Scene",
      params: [{ label: "Scene Name", type: "text" }],
    },
    {
      value: "obsEnableSceneItem",
      label: "OBS - Enable Scene Item",
      params: [
        { label: "Scene Name", type: "text" },
        { label: "Item Name", type: "text" },
        { label: "Item Index", type: "number" },
      ],
    },
    {
      value: "obsDisableSceneItem",
      label: "OBS - Disable Scene Item",
      params: [
        { label: "Scene Name", type: "text" },
        { label: "Item Name", type: "text" },
        { label: "Item Index", type: "number" },
      ],
    },
    {
      value: "obsStartReplayBuffer",
      label: "OBS - Start Replay Buffer",
      params: [],
    },
    {
      value: "obsSaveReplayBuffer",
      label: "OBS - Save Replay Buffer",
      params: [],
    },
    {
      value: "obsStopReplayBuffer",
      label: "OBS - Stop/Discard Replay Buffer",
      params: [],
    },
    {
      value: "obsStartRecord",
      label: "OBS - Start Record",
      params: [],
    },
    //not yet available in the latest stable obs version
    // {
    //   value: "obsSplitRecord",
    //   label: "OBS - Split Record",
    //   params: [],
    // },
    {
      value: "obsStopRecord",
      label: "OBS - Stop Record",
      params: [],
    },
  ];

  const triggers = [
    ...quickKeys.map((key) => ({
      value: key.label,
      label: `Quick Key ${key.label}`,
    })),
    { value: "race_schedule", label: "Race Scheduled" },
    { value: "heat_set", label: "Heat Changed" },
    { value: "race_stage", label: "Race Staged" },
    { value: "race_start", label: "Race Started" },
    { value: "race_first_pass", label: "First Pass" },
    { value: "pilot_done", label: "Pilot Finished" },
    { value: "race_win", label: "Race Won" },
    { value: "lap_record", label: "Race Recorded" },
    { value: "race_stop", label: "Race Stopped" },
    { value: "race_finish", label: "Race Finished" },
    { value: "crossing_enter", label: "Crossing Enter" },
    { value: "crossing_exit", label: "Crossing Exit" },
    { value: "laps_save", label: "Laps Saved" },
    { value: "laps_clear", label: "Laps Cleared" },
    { value: "laps_discard", label: "Laps Discarded" },
    { value: "race_in_900", label: "Race Start In 15m" },
    { value: "race_in_600", label: "Race Start In 10m" },
    { value: "race_in_540", label: "Race Start In 9m" },
    { value: "race_in_480", label: "Race Start In 8m" },
    { value: "race_in_420", label: "Race Start In 7m" },
    { value: "race_in_360", label: "Race Start In 6m" },
    { value: "race_in_300", label: "Race Start In 5m" },
    { value: "race_in_240", label: "Race Start In 4m" },
    { value: "race_in_180", label: "Race Start In 3m" },
    { value: "race_in_120", label: "Race Start In 2m" },
    { value: "race_in_60", label: "Race Start In 1m" },
    { value: "race_in_30", label: "Race Start In 30s" },
    { value: "race_in_15", label: "Race Start In 15s" },
    { value: "race_in_10", label: "Race Start In 10s" },
    { value: "race_in_5", label: "Race Start In 5s" },
    { value: "race_in_4", label: "Race Start In 4s" },
    { value: "race_in_3", label: "Race Start In 3s" },
    { value: "race_in_2", label: "Race Start In 2s" },
    { value: "race_in_1", label: "Race Start In 1s" },
  ];

  quickKeys.forEach((key) => {
    const button = createButton(
      key.label,
      () => {
        handleTriggers(key.label);
      },
      key.colorClass
    );
    quickKeysContainer.appendChild(button);
  });

  // Websocket setup
  const socket = io();

  function getSpeechSynthesisVoices() {
    return new Promise((resolve, reject) => {
      const voices = window.speechSynthesis.getVoices();
      if (voices.length) {
        resolve(voices);
      } else {
        // Voices may not be loaded initially, so we listen for the voiceschanged event
        window.speechSynthesis.onvoiceschanged = () => {
          const updatedVoices = window.speechSynthesis.getVoices();
          resolve(updatedVoices);
        };
      }
    });
  }

  // TO-DO allow for voice selection
  // getSpeechSynthesisVoices().then((voices) => {
  //   voices.forEach((voice) => {
  //     const action = actions.find((action) => action.value === "speak");
  //     console.log(action);
  //     const selectParam = action.params.find(
  //       (params) => params.type === "select"
  //     );
  //     console.log(selectParam);
  //     console.log(selectParam.options);
  //     selectParam.options.push({
  //       value: voice,
  //       label: voice.name,
  //     });
  //   });
  // });

  function speak(words) {
    if (synth.speaking) {
      console.error("speechSynthesis.speaking");
      return;
    }

    if (words !== "") {
      const utterThis = new SpeechSynthesisUtterance(words);

      utterThis.onend = function (event) {
        console.log("SpeechSynthesisUtterance.onend");
      };

      utterThis.onerror = function (event) {
        console.error("SpeechSynthesisUtterance.onerror");
      };

      const voices = synth.getVoices();

      for (let i = 0; i < voices.length; i++) {
        if (voices[i].name === synth.getVoices()[0].name) {
          utterThis.voice = voices[i];
          break;
        }
      }
      // utterThis.pitch = pitch.value;
      // utterThis.rate = rate.value;
      synth.speak(utterThis);
    }
  }

  socket.on("autopilot_trigger", (body) => {
    handleTriggers(body.event_name);
  });

  function addEvent(event) {
    const newEvent = createEventComponent(
      event,
      triggers,
      actions,
      deleteEvent,
      updateEvent,
      duplicateEvent
    );
    eventsContainer.appendChild(newEvent);
  }

  function deleteEvent(eventId) {
    state.events = state.events.filter((event) => event.id !== eventId);
    saveState(state);
    updateStateDisplay(stateDisplay, state);
    document.querySelector(`[data-event-id="${eventId}"]`).remove();
  }

  function updateEvent(eventId, updates) {
    const event = state.events.find((event) => event.id === eventId);
    Object.assign(event, updates);
    saveState(state);
    updateStateDisplay(stateDisplay, state);
  }

  function duplicateEvent(event) {
    const newEvent = {
      ...event,
      id: Date.now().toString(),
    };
    state.events.push(newEvent);
    saveState(state);
    updateStateDisplay(stateDisplay, state);
    addEvent(newEvent);
  }

  addEventButton.addEventListener("click", () => {
    const newEvent = {
      id: Date.now().toString(),
      name: "",
      trigger: "",
      action: "blank",
      params: {}, // Initialize params
    };
    state.events.push(newEvent);

    const newState = {
      ...state,
      updated: new Date().toISOString(),
    };

    saveState(newState);
    updateStateDisplay(stateDisplay, newState);
    console.log("update state" + JSON.stringify(newState));

    addEvent(newEvent);
  });

  // Apply State
  state.events.forEach(addEvent);

  function updateStateDisplay(displayElement, state) {
    displayElement.textContent = JSON.stringify(state, null, 2);
  }

  function handleTriggers(trigger) {
    if (autopilotButton.dataset.enabled === "true") {
      state.events.forEach((event) => {
        if (event.trigger === trigger) {
          activateStatusIndicator(event.id);
          if (event.action === "alert") {
            const alertText = event.params["Text"] || "Trigger activated";
            alert(alertText);
          }
          if (event.action === "speak") {
            const speakText = event.params["Text"] || "Trigger activated";
            speak(speakText);
            //socket.emit("sl_leaderboard", { classId: 0 });
            //socket.emit("speak", speakText);
          }
          if (event.action === "obsSetScene") {
            console.log("Set scene: " + event.params["Scene Name"]);
            setScene(obs, event.params["Scene Name"]);
          }
          if (event.action === "rhScheduleRace") {
            socket.emit("sl_schedule_race", {
              start_delay: event.params["Start Delay"],
            });
          }
          if (event.action === "obsEnableSceneItem") {
            console.log(
              "Disable scene item: " +
                event.params["Scene Name"] +
                ", " +
                event.params["Item Name"] +
                ", " +
                parseInt(event.params["Item Index"])
            );
            enableSceneItemBySourceName(
              obs,
              event.params["Scene Name"],
              event.params["Item Name"],
              parseInt(event.params["Item Index"])
            );
          }
          if (event.action === "obsDisableSceneItem") {
            console.log(
              "Disable scene item: " +
                event.params["Scene Name"] +
                ", " +
                event.params["Item Name"] +
                ", " +
                parseInt(event.params["Item Index"])
            );
            disableSceneItemBySourceName(
              obs,
              event.params["Scene Name"],
              event.params["Item Name"],
              parseInt(event.params["Item Index"])
            );
          }
          if (event.action === "obsStartReplayBuffer") {
            console.log("Start replay buffer");
            startReplayBuffer(obs);
          }
          if (event.action === "obsSaveReplayBuffer") {
            console.log("Save replay buffer");
            saveReplayBuffer(obs);
          }
          if (event.action === "obsStopReplayBuffer") {
            console.log("Stop and discard replay buffer");
            stopReplayBuffer(obs);
          }
          if (event.action === "obsStartRecord") {
            console.log("Start record");
            startRecord(obs);
          }
          if (event.action === "obsStopRecord") {
            console.log("Stop record");
            stopRecord(obs);
          }
          if (event.action === "obsSplitRecord") {
            console.log("Split record");
            splitRecordFile(obs);
          }
        }
      });
    }
  }

  function activateStatusIndicator(eventId) {
    const eventContainer = document.querySelector(
      `[data-event-id="${eventId}"]`
    );

    console.log(eventContainer);
    const statusIndicator = eventContainer.querySelector(".status");

    console.log(statusIndicator);
    statusIndicator.classList.remove("bg-red-300");
    statusIndicator.classList.remove("from-red-500");
    statusIndicator.classList.add("bg-green-300");
    statusIndicator.classList.add("from-green-500");

    setTimeout(() => {
      statusIndicator.classList.remove("bg-green-300");
      statusIndicator.classList.remove("from-green-500");
      statusIndicator.classList.add("bg-red-300");
      statusIndicator.classList.add("from-red-500");
    }, 1000); // Change color back after 1 second
  }
});
