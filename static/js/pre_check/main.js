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

domReady(function () {

  const socket = io();

  // If found you qr code
  function onScanSuccess(decodeText, decodeResult) {
      alert("Pilot has been added to the heat : " + decodeText, decodeResult);
      console.log(decodeText)
      console.log(decodeResult)
      socket.emit("sl_pre_check_pilot", decodeText);
  }

  let htmlscanner = new Html5QrcodeScanner(
      "my-qr-reader",
      { fps: 10, qrbos: 250 }
  );
  htmlscanner.render(onScanSuccess);
});