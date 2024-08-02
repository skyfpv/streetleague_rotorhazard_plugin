// static/js/fpvoverlay/main.js

import { createPilotCard, ordinal } from "./components.js";

document.addEventListener("DOMContentLoaded", () => {
  const leaderboardContainer = document.querySelector("#leaderboard");
  const header = document.querySelector("#header");
  let stageTimes = [];
  let combinedRanks = [];

  let pilotCards = [];
  let progressToWin = 4;
  let currentProgress = 0;
  let raceCurrentTime = 0;
  let raceStartTime = Date.now();

  let pilotColors = {};
  let seatInfo = {};
  let heatResults = {};
  let lastStageTimes = [];
  let primaryLeaderboard = "by_race_time";

  updateHeader();

  // Get query parameters
  let params = new URL(document.location.toString()).searchParams;
  let columns = params.get("columns") || 2;
  let tagLength = params.get("tagLength") || 288;
  let tagHeight = params.get("tagHeight") || 30;

  const socket = io();

  socket.on("sl_seat_info", (body) => {
    seatInfo = body;
    createLeaderboard();
    updateLeaderboard();
    console.log("seat_info", seatInfo);
  });

  socket.on("autopilot_trigger", (body) => {
    const evt = body.event_name;

    if (evt === "race_stage" || evt === "race_start") {
      currentProgress = 0;
      updateLeaderboard();
    }
    if (
      evt === "race_stop" ||
      evt === "race_finish" ||
      evt === "race_first_pass" ||
      evt === "laps_save" ||
      evt === "laps_clear" ||
      evt === "laps_discard" ||
      evt === "lapDelete" ||
      evt === "lapRestoreDeleted"
    ) {
      currentProgress = progressToWin;
      updateLeaderboard();
    }
    if (evt === "heat_set") {
      socket.emit("sl_get_pilot_colors");
      socket.emit("sl_get_current_stage_times");
      socket.emit("sl_get_current_heat_results");
      console.log("heat_set");
    }
  });

  socket.on("sl_race_timing", (body) => {
    primaryLeaderboard = body.meta.primary_leaderboard;
    heatResults = body;
    console.log(heatResults);
    updateCurrentProgress();

    console.log("currentProgress: " + currentProgress);
    updateHeader();
    const oldCombinedRanks = combinedRanks;
    updateStageTimes();
    combineRanks();
    if (oldCombinedRanks.length !== combinedRanks.length) {
      console.log("combinedRanks changed");
      createLeaderboard();
    }
    updateLeaderboard();
  });

  socket.on("sl_current_stage_times", (body) => {
    console.log("sl_current_stage_times");
    console.log(body);
    lastStageTimes = body;
    updateStageTimes();
    combineRanks();
    createLeaderboard();
    updateLeaderboard();
  });

  socket.on("sl_current_heat_results", (body) => {
    console.log("sl_current_heat_results");
    console.log(body);
    heatResults = body;
    updateStageTimes();
    combineRanks();
    createLeaderboard();
    updateLeaderboard();
  });

  socket.on("sl_pilot_colors", (body) => {
    setPilotColors(body);
  });

  socket.emit("sl_get_seat_info");
  socket.emit("sl_get_pilot_colors");
  socket.emit("sl_get_current_stage_times");
  socket.emit("sl_get_current_heat_results");

  function updateCurrentProgress() {
    const leaderboard = heatResults[primaryLeaderboard];
    raceStartTime = parseFloat(leaderboard.race_start_time);

    raceCurrentTime = 0;
    let greatestProgress = 0;
    leaderboard.map((heatResult) => {
      if (heatResult.laps + heatResult.starts > greatestProgress) {
        greatestProgress = heatResult.laps + heatResult.starts;
      }
      if (heatResult.total_time_raw > raceCurrentTime) {
        raceCurrentTime = heatResult.total_time_raw;
      }
    });
    currentProgress = greatestProgress;
  }

  function setPilotColors(body) {
    console.log("updateSeatColors");
    pilotColors = {};
    for (const [key, color] of Object.entries(body)) {
      console.log(key, color);
      pilotColors[key] = color;
    }
  }

  function parseHeatResults(heatResults, active) {
    const parsedResults = [];
    heatResults.map((heatResult, heatResultIndex) => {
      parsedResults.push({
        pilot_id: heatResult.pilot_id,
        callsign: heatResult.callsign,
        starts: heatResult.starts,
        laps: heatResult.laps,
        progress: heatResult.starts + heatResult.laps,
        time: heatResult.total_time_raw,
        pace: heatResult.total_time_raw / (heatResult.laps + heatResult.starts),
        active: active,
      });
    });
    return parsedResults;
  }

  function sortTimes(r) {
    r.sort((a, b) => {
      if (a.progress !== b.progress) {
        return b.progress - a.progress;
      }
      return a.time - b.time;
    });
    return r;
  }

  function sortTimesByPace(r) {
    r.sort((a, b) => {
      const aProg = Math.min(a.progress, currentProgress);
      const bProg = Math.min(b.progress, currentProgress);
      if (aProg !== bProg) {
        return bProg - aProg;
      }
      const aVal = a.pace * aProg;
      const bVal = b.pace * bProg;
      return aVal - bVal;
    });
    return r;
  }

  function combineRanks() {
    const leaderboard = heatResults[primaryLeaderboard];

    //combine pilots from the current heat
    if (leaderboard != undefined) {
      combinedRanks = [];
      const parsedHeatResults = parseHeatResults(leaderboard, true);
      parsedHeatResults.map((result) => {
        result.color = pilotColors[result.pilot_id];
        combinedRanks.push(result);
      });
      //combine the times from the previous heats in the stage
      stageTimes.map((stageTime) => {
        stageTime.color = "#888888";

        //don't add duplicate pilots if the pilots from the current heat already have results
        const found = parsedHeatResults.find(
          (c) => c.pilot_id == stageTime.pilot_id
        );
        if (found == undefined) {
          combinedRanks.push(stageTime);
        } else {
        }
      });

      combinedRanks = sortTimesByPace(combinedRanks);
    }
  }

  function updateStageTimes() {
    stageTimes = [];
    lastStageTimes.map((heat, heatIndex) => {
      const primaryLeaderboard = heat.meta.primary_leaderboard;
      const heatResults = heat[primaryLeaderboard];
      parseHeatResults(heatResults, false).map((result) => {
        stageTimes.push(result);
      });
    });
    stageTimes = sortTimes(stageTimes);
  }

  function createLeaderboard() {
    console.log("createLeaderboard");
    leaderboardContainer.innerHTML = "";
    pilotCards = [];
    combinedRanks.map((seat, seatIndex) => {
      const card = createPilotCard(
        seat.callsign,
        seat.color,
        tagLength,
        tagHeight,
        "staging",
        `${seatIndex + 1}${ordinal(seatIndex + 1)}`
      );
      card.dataset.pilotId = seat.pilot_id;
      pilotCards.push(card);
      leaderboardContainer.appendChild(card);
    });
  }

  function updateLeaderboard() {
    console.log("updateLeaderboard");
    console.log(combinedRanks);
    combinedRanks.map((seat, seatIndex) => {
      let card = pilotCards.find((c) => c.dataset.pilotId == seat.pilot_id);
      //console.log(">>>> ", card);
      let interval = calculateInterval(seat, seatIndex);
      //if the interval is undefined, it's a dnf
      if (interval === undefined) {
        interval = "time since rival passed";
      }

      //update card info
      const intervalDiv = card.querySelector(".interval");
      const positionDiv = card.querySelector(".position");
      intervalDiv.textContent = interval;
      positionDiv.textContent = `${seatIndex + 1}${ordinal(seatIndex + 1)}`;
      // card.style.transform = `translateY(${
      //   seatIndex * tagHeight - card.dataset.initialOffsetY
      // }px)`;
      //console.log(seat);
      //console.log(seatIndex);

      card.style.transform = `translateY(${seatIndex * tagHeight}px)`;
      //console.log(card.style.transform, "==", seatIndex * tagHeight);
    });
  }

  function calculateInterval(seat, seatIndex) {
    let interval = new Date(seat.time).toISOString().slice(14, 22);

    //the first pilot is the leader, leave their interval alone
    if (seatIndex != 0) {
      const rival = combinedRanks[seatIndex - 1];
      const leastProgress = Math.min(rival.progress, seat.progress);
      let gap = seat.pace * leastProgress - rival.pace * leastProgress;
      if (gap < 0) {
        //This pilot has been passed by his rival even though he was going faster last time we checked
        //So all we know is that his interval is at minimum the duration between his rivals last lap time and now
        gap = raceCurrentTime - rival.pace * leastProgress;
      }
      interval = "+" + (gap / 1000).toFixed(2);

      if (isNaN(rival.pace) || isNaN(seat.pace)) {
        interval = new Date(seat.time).toISOString().slice(14, 22);
      }
    } else {
      if (isNaN(seat.pace)) {
        interval = `00:00.00`;
      } else {
        interval = `${new Date(
          seat.pace * Math.min(seat.progress, currentProgress)
        )
          .toISOString()
          .slice(14, 22)}`;
      }
    }
    if (seat.progress < currentProgress) {
      if (!seat.active) {
        interval = "dnf";
      }
    }

    if (seat.starts == 0) {
      if (seat.active) {
        interval = "staging";
      }
    }
    return interval;
  }

  function updateHeader() {
    header.innerHTML = `Lap ${currentProgress}/${progressToWin}`;
  }

  // function startTimer() {
  //   // Get the timer div
  //   const timerDiv = document.getElementById("timer");
  //   // Initialize the timer value
  //   let timerValue = 0;

  //   // Function to update the timer
  //   function updateTimer() {
  //     const startDate = new Date(raceStartTime);
  //     const endDate = Date.now();
  //     const timeDiff = endDate - startDate;
  //     header.innerHTML = `${new Date(startDate).toISOString()}`;
  //   }

  //   // Update the timer every second (1000 milliseconds)
  //   setInterval(updateTimer, 1000);
  // }

  // startTimer();
});
