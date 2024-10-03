// static/js/pre_check/main.js

function domReady(fn) {
  if (
    document.readyState === "complete" ||
    document.readyState === "interactive"
  ) {
    setTimeout(fn, 1000);
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

let params = new URL(document.location.toString()).searchParams;

const header = document.getElementById("header");
const html5QrCode = new Html5Qrcode("qr-scanner");
const scanningStatus = document.getElementById("scanning-status");
const scannerContainer = document.getElementById("scanner-container");
const heatSelection = document.getElementById("heat-selection");
const pilotControls = document.getElementById("pilot-controls");
const doneButton = document.getElementById("done");
const cancelButton = document.getElementById("cancel");
const cancelContainer = document.getElementById("cancel-container");
const originWarning = document.getElementById("origin-warning");

let uuid = randomId();

const STATE_LOADING = 0;
const STATE_SCANNING = 1;
const STATE_PILOT_LOOKUP = 2;
const STATE_PILOT_FOUND = 3;
const STATE_PILOT_ERROR = 4;

let state = STATE_LOADING;

const RACE_STATUS_READY = 0;
const RACE_STATUS_STAGING = 3;
const RACE_STATUS_RACING = 1;
const RACE_STATUS_DONE = 2;

let currentPilot = undefined;
let cameraId = undefined;
let maxJoinCount = params.get("maxJoins") || 3;

let pilots = [{ pilot_id: 0, callsign: "", team: "A", name: "" }];
let heatData = { heats: [] };
let currentHeatId = 0;
let currentClassId = 0;
let raceStatus = RACE_STATUS_READY;

let frequencyData = [];

let raceStatusColor = "white";

const socket = io();

doneButton.addEventListener("click", () => {
  currentPilot = undefined;
  checkLastHeat();
  setState(STATE_SCANNING);
});

cancelButton.addEventListener("click", () => {
  cancelCheckin();
});

function randomId(length = 6) {
  return Math.random()
    .toString(36)
    .substring(2, length + 2);
}

function setState(newState) {
  console.log("setState: ", newState);
  state = newState;
  switch (newState) {
    case STATE_LOADING:
      scanningStatus.textContent = "Loading...";
      scanningStatus.className =
        "red-500 text-white font-bold py-2 px-4 rounded-t mr-[1px]";
      break;
    case STATE_SCANNING:
      startScanning();
      scanningStatus.textContent = "Scanning...";
      scanningStatus.className =
        "bg-gray-500 text-white font-bold py-2 px-4 rounded-t mr-[1px]";
      scannerContainer.className = "flex w-full inline";
      header.textContent = "Scan badge to race";
      cancelContainer.className = "hidden";
      pilotControls.className = "hidden";
      header.className =
        "basis-1/3 bg-gray-800 rounded-b-xl p-4 text-gray-100 font-bold mb-2 text-3xl text-center border-b-4 border-gray-600";
      updateHeatTable();
      break;
    case STATE_PILOT_LOOKUP:
      stopScanning();
      scanningStatus.textContent = "Please Wait...";
      scanningStatus.className =
        "bg-yellow-400 text-white font-bold py-2 px-4 rounded-t mr-[1px]";
      cancelContainer.className = "inline";
      break;
    case STATE_PILOT_FOUND:
      scanningStatus.textContent = "Welcome";
      scanningStatus.className =
        "bg-green-500 text-white font-bold py-2 px-4 rounded-t mr-[1px]";
      scannerContainer.className = "flex w-full hidden";
      heatSelection.className = "inline";
      cancelContainer.className = "hidden";
      pilotControls.className = "inline";
      updateHeatTable();
      break;
    case STATE_PILOT_ERROR:
      scanningStatus.textContent = "Error";
      scanningStatus.className =
        "bg-red-500 text-white font-bold py-2 px-4 rounded-t mr-[1px]";
      break;
    default:
      console.error("unknown state");
      break;
  }
}

socket.on("frequency_data", (body) => {
  console.log("frequency_data: ", body);
  frequencyData = body.fdata.filter((node) => node.frequency != 0);
  console.log("frequency_data: ", body);
  updateHeatTable();
});

socket.on("race_status", (body) => {
  console.log("race_status: ", body);
  switch (body.race_status) {
    case RACE_STATUS_DONE:
      //raceStatusColor = "bg-gradient-to-b from-red-500 to-white text-white";
      raceStatusColor =
        "bg-gradient-to-l from-red-500 from-0% to-gray-200 to-10%";
      break;
    case RACE_STATUS_STAGING:
      raceStatusColor =
        "bg-gradient-to-l from-yellow-400 from-0% to-gray-200 to-10%";
      break;
    case RACE_STATUS_RACING:
      raceStatusColor =
        "bg-gradient-to-l from-green-500 from-0% to-gray-200 to-10%";
      break;
    case RACE_STATUS_READY:
      raceStatusColor =
        "bg-gradient-to-l from-blue-500 from-0% to-gray-200 to-10%";
      break;
    default:
      console.error("unknown race status");
      break;
  }
  currentHeatId = body.race_heat_id;
  currentClassId = body.race_class_id;
  updateHeatTable();
});

socket.on("sl_pre_check_pilot_info", (body) => {
  if (body.requestId == uuid) {
    console.log("sl_pre_check_pilot_info: ", body);
    if (body.pilot) {
      header.textContent = "Welcome " + body.pilot.callsign;
      header.className =
        "basis-1/3 bg-gray-800 rounded-b-xl p-4 text-gray-100 font-bold mb-2 text-3xl text-center border-b-4 border-[" +
        body.pilot.color +
        "]";
      currentPilot = body.pilot;
      checkLastHeat();
      setState(STATE_PILOT_FOUND);
    } else {
      setState(STATE_SCANNING);
    }
  }
});
// store the pilot ids and names in the pilots variable
socket.on("pilot_data", (body) => {
  console.log("pilot_data: ", body);
  pilots = body.pilots;
  pilots.unshift({ pilot_id: 0, callsign: "_", team: "A", name: "_" });
  updateHeatTable();
});

socket.on("current_heat", (body) => {
  console.log("current_heat: ", body);
  currentHeatId = body.current_heat;
  updateHeatTable();
});

socket.on("race_saved", (body) => {
  console.log("race_save");
  console.log(body);
  let saved_heat_id = body.heat_id;
  //find heat with this id in our heatData object and update it
  for (let i = 0; i < heatData.heats.length; i++) {
    if (heatData.heats[i].id == saved_heat_id) {
      heatData.heats[i].locked = true;
    }
  }

  updateHeatTable();
});

socket.on("heat_data", (body) => {
  console.log("heat_data: ", body);
  heatData = body;
  //remove all heats where
  updateHeatTable();
});

socket.on("sl_pre_check_join_confirm", (body) => {
  if (body.requestId == uuid) {
    console.log("sl_pre_check_join_confirm: ", body);
    let heatName =
      body.heat.name != null ? body.heat.name : "Heat " + body.heat.id;
    let channelInfo = body.channelInfo;
    let band = channelInfo.band;
    let channel = channelInfo.channel;
    let frequency = channelInfo.frequency;
    alert(
      "You have been added to " +
        heatName +
        "\nChannel: " +
        band +
        "" +
        channel +
        " (" +
        frequency +
        ")"
    );
  }
});

function trimOldHeats() {
  heatData.heats = heatData.heats.filter((heat) => !heat.locked);
}

function updateHeatTable() {
  trimOldHeats();
  const nodeCount = frequencyData.length;

  const tableBody = document.getElementById("heat-table-body");
  const tableHead = document.getElementById("heat-table-head");
  tableBody.innerHTML = "";
  tableHead.innerHTML = "";

  const th = document.createElement("th");
  th.className = "bg-gray-800 text-white";
  th.textContent = "Heat Name";
  tableHead.appendChild(th);
  for (let nodeIndex = 0; nodeIndex < nodeCount; nodeIndex++) {
    const th = document.createElement("th");
    th.className = "bg-gray-800 text-white";
    //th.textContent = "Slot " + (nodeIndex + 1);
    th.textContent =
      frequencyData[nodeIndex].band +
      "" +
      frequencyData[nodeIndex].channel +
      " (" +
      frequencyData[nodeIndex].frequency +
      ")";
    tableHead.appendChild(th);
  }

  heatData.heats.forEach((heat) => {
    const row = document.createElement("tr");

    let slotCellColor = "bg-gray-200";
    const notOnlyHeatAndNotCurrentHeat =
      heatData.heats.length > 2 && heat.id == currentHeatId;
    console.log("current heat is", currentHeatId, heat);

    if (heat.id == currentHeatId) {
      // slotCell.className =
      //   "bg-[var(--sl-green)] text-white px-2 py-4 text-center font-bold";

      slotCellColor = raceStatusColor;
    }

    console.log(slotCellColor);

    // Add Heat Name
    const heatNameCell = document.createElement("td");
    heatNameCell.className =
      "truncate p-2 text-center font-bold " + slotCellColor;
    heatNameCell.textContent = heat.displayname;
    row.appendChild(heatNameCell);

    // Add slots (assuming up to 8 slots)
    for (let nodeIndex = 0; nodeIndex < nodeCount; nodeIndex++) {
      const slotCell = document.createElement("td");
      slotCell.className = "truncate p-2 text-center font-bold";
      const slot = heat.slots[nodeIndex];
      const notOnlyHeatAndNotCurrentHeat =
        heatData.heats.length > 2 && heat.id == currentHeatId;
      if (heat.locked || notOnlyHeatAndNotCurrentHeat) {
        // Locked rows (grayed out)
        if (heat.id == currentHeatId) {
          // slotCell.className =
          //   "bg-[var(--sl-green)] text-white px-2 py-4 text-center font-bold";
          //slotCell.classList.add("bg-" + raceStatusColor);
        }

        slotCell.textContent = getPilotCallsign(slot.pilot_id);
      } else {
        if (heat.id == currentHeatId) {
          // slotCell.className =
          //   "bg-[var(--sl-green)] text-white px-2 py-4 text-center font-bold";
          //slotCell.classList.add("bg-" + raceStatusColor);
        }

        // Unlocked row
        const cellButton = document.createElement("button");
        if (currentPilot != undefined) {
          if (slot.pilot_id == 0) {
            cellButton.className = "truncate w-full p-2 rounded bg-gray-200";
            cellButton.textContent = "+";
            cellButton.addEventListener("mouseover", function () {
              this.textContent = "Join";
            });
            cellButton.addEventListener("mouseout", function () {
              this.textContent = "+";
            });
            cellButton.addEventListener("click", () => {
              pilotJoinHeatSlot(heat, slot);
            });
          } else {
            if (slot.pilot_id == currentPilot.id) {
              cellButton.className =
                "truncate w-full p-2 rounded bg-gray-200 hover:text-white hover:bg-red-400 hover:border-red-400 border-b-4 border-[" +
                getPilotById(slot.pilot_id).color +
                "]";
              cellButton.textContent = getPilotCallsign(slot.pilot_id);
              cellButton.addEventListener("mouseover", function () {
                this.textContent = "Leave";
              });
              cellButton.addEventListener("mouseout", function () {
                this.textContent = getPilotCallsign(slot.pilot_id);
              });
              cellButton.addEventListener("click", () => {
                pilotLeaveHeatSlot(heat, slot);
              });
            } else {
              cellButton.className = "truncate w-full p-2 rounded bg-gray-200";
              cellButton.textContent = getPilotCallsign(slot.pilot_id);
            }
          }
        } else {
          const pilotColor = getPilotById(slot.pilot_id)
            ? getPilotById(slot.pilot_id).color
            : "#ffffff";

          cellButton.className =
            "truncate  w-full p-2 rounded bg-gray-200 hover:text-white hover:bg-[" +
            pilotColor +
            "] hover:border-[" +
            pilotColor +
            "]-400 border-b-4 border-[" +
            pilotColor +
            "]";
          cellButton.textContent = getPilotCallsign(slot.pilot_id);
        }
        slotCell.appendChild(cellButton);
      }
      row.appendChild(slotCell);
    }

    tableBody.appendChild(row);
  });
}

function pilotLeaveHeatSlot(heat, slot) {
  let alteredSlot = {
    heat: heat.id,
    slot_id: slot.id,
    pilot: 0,
    method: 0,
  };
  console.log("altered slot", alteredSlot);
  socket.emit("alter_heat", alteredSlot);
  console.log(heatData);
  slot.pilot_id = 0;
  updateHeatTable();
}

function pilotJoinHeatSlot(heat, slot) {
  //find pilot in heat and remove them if they are there
  console.log("pilotJoinHeatSlot: ", heat, slot);
  for (let slotIndex = 0; slotIndex < heat.slots.length; slotIndex++) {
    if (heat.slots[slotIndex].pilot_id == currentPilot.id) {
      if (slotIndex != slot.node_index) {
        let alteredSlot = {
          heat: heat.id,
          slot_id: heat.slots[slotIndex].id,
          pilot: 0,
          method: 0,
        };
        console.log("altered slot", alteredSlot);
        socket.emit("alter_heat", alteredSlot);
        heat.slots[slotIndex].pilot_id = 0;
      }
    } else {
      console.log(heat.slots[slotIndex].pilot_id, "!= ", currentPilot.id);
    }
  }

  //if the pilot has not already joined the max number of heats, add them
  if (getPilotRegistrationCount() <= maxJoinCount) {
    let alteredSlot = {
      heat: heat.id,
      slot_id: slot.id,
      pilot: currentPilot.id,
      method: 0,
    };
    console.log("altered slot", alteredSlot);
    socket.emit("alter_heat", alteredSlot);
    slot.pilot_id = currentPilot.id;
    checkLastHeat();
    updateHeatTable();
  } else {
    alert("You can only register for " + maxJoinCount + " heats");
  }
}

//returns the number of heats the pilot with the given ID is registered for
function getPilotRegistrationCount() {
  let count = 0;
  heatData.heats.forEach((heat) => {
    heat.slots.forEach((slot) => {
      if (slot.pilot_id == currentPilot.id) {
        count++;
      }
    });
  });
  return count;
}

//makes sure that the last heat contains only empty slots. If not, create a new heat
function checkLastHeat() {
  if (heatData.heats.length > 0) {
    if (
      heatData.heats[heatData.heats.length - 1].slots.filter(
        (s) => s.pilot_id != 0
      ).length > 0
    ) {
      //add a heat with the same class as the current heat
      socket.emit("add_heat", { class: currentClassId });
      console.log("added new heat to class", currentClassId);
    } else {
      console.log(
        "last heat is empty",
        heatData.heats[heatData.heats.length - 1].slots
      );
    }
  } else {
    socket.emit("add_heat", { class: currentClassId });
    console.log("added new heat to class", currentClassId);
  }
}

function requestPilotInfo(slPilotId) {
  console.log("requestPilotInfo: ", slPilotId);
  socket.emit("sl_pre_check_get_pilot_info", {
    slPilotId: slPilotId,
    requestId: uuid,
  });
}

function populatePilotOptions(selectElement, selectedPilotId) {
  pilots.forEach((pilot) => {
    const option = document.createElement("option");
    option.value = pilot.pilot_id;
    option.textContent = pilot.callsign;
    selectElement.appendChild(option);
    console.log(
      selectedPilotId,
      "==",
      pilot.pilot_id,
      pilot.pilot_id == selectedPilotId
    );
    if (pilot.pilot_id == selectedPilotId) {
      option.selected = true;
      selectElement.value = pilot.pilot_id;
    }
  });
}

function getPilotCallsign(pilot_id) {
  const pilot = pilots.find((p) => p.pilot_id === pilot_id);
  return pilot ? pilot.callsign : "Unknown";
}

function getPilotById(pilot_id) {
  const pilot = pilots.find((p) => p.pilot_id === pilot_id);
  return pilot ? pilot : undefined;
}

function autoJoin() {
  //alert("You have been added to the heat : " + heatName);
  console.log("autoJoin: ", currentPilot);
  socket.emit("sl_pre_check_pilot", {
    slPilotId: currentPilot.slPilotId,
    requestId: uuid,
  });
}

function cancelCheckin() {
  setState(STATE_SCANNING);
}

domReady(function () {
  loadData();
  // Create instance of the object. The only argument is the "id" of HTML element created above.

  // This method will trigger user permissions
  Html5Qrcode.getCameras()
    .then((devices) => {
      /**
       * devices would be an array of objects of type:
       * { id: "id", label: "label" }
       */
      if (devices && devices.length) {
        cameraId = devices[0].id;
        setState(STATE_SCANNING);
        // .. use this to start scanning.
      }
    })
    .catch((err) => {
      console.log("unable to request camera access.");
      console.error(err);
      originWarning.className = "text-white font-bold py-2 px-4 rounded inline";
    });
});

function startScanning() {
  if (cameraId) {
    html5QrCode
      .start(
        cameraId, // retreived in the previous step.
        {
          fps: 24,
        },
        (qrCodeMessage) => {
          console.log("state: ", state, qrCodeMessage);
          if (state == STATE_SCANNING) {
            if (!currentPilot) {
              // do something when code is read. For example:
              console.log(`QR Code detected: ${qrCodeMessage}`);
              setState(STATE_PILOT_LOOKUP);
              requestPilotInfo(qrCodeMessage);
            }
          }
        },
        (errorMessage) => {
          // if(state===STATE_SCANNING){
          //   // parse error, ideally ignore it. For example:
          //   console.log(`QR Code no longer in front of camera.`);
          //   setState(`Scanning...`, "bg-gray-500");
          //   qrFound = false;
          // }
        }
      )
      .catch((err) => {
        // Start failed, handle it. For example,
        console.log(`Unable to start scanning, error: ${err}`);
        setState(STATE_PILOT_ERROR);
      });
  }
}

function stopScanning() {
  html5QrCode
    .stop()
    .then((ignore) => {
      // QR Code scanning is stopped.
      console.log("QR Code scanning stopped.");
    })
    .catch((err) => {
      // Stop failed, handle it.
      console.log("Unable to stop scanning.");
    });
}

function loadData() {
  socket.emit("load_data", {
    load_types: [
      "frequency_data",
      "pilot_data",
      "seat_data",
      "heat_data",
      "class_data",
      "format_data",
      "min_lap",
      "race_status",
      "backups_list",
      "exporter_list",
      "importer_list",
      "heatgenerator_list",
      "raceclass_rank_method_list",
      "race_points_method_list",
    ],
  });
}
