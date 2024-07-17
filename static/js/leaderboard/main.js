// static/js/fpvoverlay/main.js

import { createLeaderboardGird } from "./components.js";

document.addEventListener("DOMContentLoaded", () => {
  const socket = io();
  const leaderboardContainer = document.querySelector("#leaderboard-container");

  // Get query parameters
  let params = new URL(document.location.toString()).searchParams;
  let classId = params.get("classId") || 0;
  let scrollDistance = params.get("scrollDistance") || 0;
  let scrollDelay = params.get("scrollDelay") || 0;
  let scrollCount = params.get("scrollCount") || 0;

  console.log("waiting socket connection");
  socket.on("connect", () => {
    console.log("socket connected!");
    socket.emit("sl_leaderboard", { classId: classId });
  });

  socket.on("sl_leaderboard", (body) => {
    console.log("got leaderboard update!");
    console.log(body);
    updateLeaderboard(body);
  });

  function updateLeaderboard(leaderboard) {
    const leaderboardName = leaderboard.name;
    const meta = leaderboard.leaderboard.meta;
    let leaderboardFields = [];
    let data = undefined;

    const standardFields = [
      { name: "laps", label: "Laps" },
      {
        name: "total_time",
        label: `Time`,
      },
      { name: "fastest_lap", label: "Fastest Lap" },
    ];

    const byConsecutivesFields = [
      { name: "consecutives_base", label: "Laps" },
      {
        name: "consecutives",
        label: `Top${meta.consecutives_count}Con Time`,
      },
      { name: "fastest_lap_source", label: "Source" },
    ];

    const byFastestLapFields = [
      { name: "fastest_lap", label: "Fastest Lap" },
      { name: "fastest_lap_source", label: "Source" },
    ];

    const byRaceTime = [
      { name: "laps", label: "Laps" },
      {
        name: "total_time",
        label: `Time`,
      },
      { name: "fastest_lap", label: "Fastest Lap" },
    ];

    if (leaderboard.ranking == false) {
      console.log(meta);
      data = leaderboard.leaderboard[meta.primary_leaderboard];
      if (meta.primary_leaderboard == "by_consecutives") {
        leaderboardFields = byConsecutivesFields;
      } else if (meta.primary_leaderboard == "by_fastest_lap") {
        leaderboardFields = byFastestLapFields;
      } else if (meta.primary_leaderboard == "by_race_time") {
        leaderboardFields = byRaceTime;
      } else {
        leaderboardFields = standardFields;
      }
    } else {
      leaderboardFields = leaderboard.ranking.meta.rank_fields;
      data = leaderboard.ranking.ranking;
    }

    leaderboardFields.push({
      name: "position",
      label: "Pos",
    });
    leaderboardFields.push({
      name: "callsign",
      label: "Pilot",
    });
    console.log(leaderboardFields);

    console.log(leaderboardName);
    console.table(data);

    let keysToRemove = ["team_name", "pilot_id"];
    let firstKeys = ["position", "callsign"];
    let lastKeys = ["heat_rank", "points", "fastest_lap_source"];

    //create filteredResults from data, filtering to include only leaderboardFields
    //also replaces data keys with their corresponding leaderboardField labels

    const filteredResults = data.map((obj) => {
      let newObj = {};

      // Add the keys from firstKeys
      firstKeys.forEach((key) => {
        if (key in obj && !keysToRemove.includes(key)) {
          leaderboardFields.forEach((fieldKey) => {
            if (fieldKey.name in obj && fieldKey.name == key) {
              newObj[fieldKey.label] = obj[key];
            }
          });
        }
      });

      // Add the remaining keys in original order
      Object.keys(obj).forEach((key) => {
        if (
          !firstKeys.includes(key) &&
          !lastKeys.includes(key) &&
          !keysToRemove.includes(key)
        ) {
          leaderboardFields.forEach((fieldKey) => {
            if (fieldKey.name in obj && fieldKey.name == key) {
              newObj[fieldKey.label] = obj[key];
            }
          });
        }
      });

      // Add the keys from lastKeys
      lastKeys.forEach((key) => {
        if (key in obj && !keysToRemove.includes(key)) {
          leaderboardFields.forEach((fieldKey) => {
            if (fieldKey.name in obj && fieldKey.name == key) {
              newObj[fieldKey.label] = obj[key];
            }
          });
        }
      });

      return newObj;
    });

    leaderboardContainer.innerHTML = "";
    const leaderboardGrid = createLeaderboardGird(
      leaderboardName,
      filteredResults,
      "emerald-400",
      scrollDistance,
      scrollDelay,
      scrollCount
    );
    leaderboardContainer.appendChild(leaderboardGrid);
    // for (const [index, seat] of Object.entries(seats)) {
    //   if (seat.active_seat) {
    //     const nodeComponent = createFPVOverlay(
    //       seat.callsign,
    //       activeColorToHex(seat.active_color),
    //       tagLength,
    //       tagHeight,
    //       true
    //     );
    //     overlayContainer.appendChild(nodeComponent);
    //   }
    // }
  }

  function activeColorToHex(color) {
    return "#" + pad(color.toString(16), 6);
  }
  function pad(n, z = 2) {
    return ("000000" + n).slice(-z);
  }
});
