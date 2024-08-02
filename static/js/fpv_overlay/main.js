// static/js/fpvoverlay/main.js

import { createFPVOverlay } from "./components.js";

document.addEventListener("DOMContentLoaded", () => {
  const overlayContainer = document.querySelector("#fpv-overlay-container");
  let frequency = [];

  // Get query parameters
  let params = new URL(document.location.toString()).searchParams;
  let columns = params.get("columns") || 2;
  let tagLength = params.get("tagLength") || 33;
  let tagHeight = params.get("tagHeight") || 100;

  const socket = io();

  overlayContainer.classList.remove("grid-cols-2");
  overlayContainer.classList.add("grid-cols-" + columns);
  console.log(overlayContainer);

  socket.emit("sl_get_seat_info");

  socket.on("sl_seat_info", (body) => {
    updateOverlay(body);
  });

  function updateOverlay(body) {
    overlayContainer.innerHTML = "";
    const seats = body.seat_info;
    console.log(body);

    for (const [index, seat] of Object.entries(seats)) {
      if (seat.active_seat) {
        const nodeComponent = createFPVOverlay(
          seat.callsign,
          activeColorToHex(seat.active_color),
          tagLength,
          tagHeight,
          true
        );
        overlayContainer.appendChild(nodeComponent);
      }
    }
  }

  function activeColorToHex(color) {
    return "#" + pad(color.toString(16), 6);
  }
  function pad(n, z = 2) {
    return ("000000" + n).slice(-z);
  }
});
