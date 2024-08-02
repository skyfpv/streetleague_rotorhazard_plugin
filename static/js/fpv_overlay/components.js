// static/js/fpvoverlay/components.js

export function createFPVOverlay(
  callsign,
  colorClass,
  tagLength,
  tagHeight,
  visible
) {
  const nodeContainer = document.createElement("div");
  nodeContainer.className = `flex flex-col h-full w-full`;
  const displayArea = document.createElement("div");
  displayArea.className = "h-full";

  const pilotTag = document.createElement("div");
  pilotTag.className = `h-full text-nowrap overflow-hidden w-full p-3 font-mono font-bold text-3xl text-white flex items-center rounded-tr-[20px] bg-gradient-to-r from-[color:var(--carbon)] from-0% to-[color:var(--carbon-lite)] to-100%`;

  const pilotTagBorder = document.createElement("div");
  pilotTagBorder.className = `h-[${tagHeight}px] text-nowrap border-[1px] border-gray-300/75 overflow-hidden w-[0%] p-[6px] rounded-tr-[26px] bg-gradient-to-tr from-[color:var(--glass)] from-25% via-gray-500/60 via-50% to-[${colorClass}] to-80%`;

  const pilotCallsign = document.createElement("p");
  pilotCallsign.className = `text-4xl text-nowrap w-full overflow-hidden whitespace-nowrap text-clip`;
  pilotCallsign.textContent = callsign.toUpperCase();

  if (visible) {
    pilotTagBorder.appendChild(pilotTag);
    pilotTag.appendChild(pilotCallsign);
    nodeContainer.appendChild(displayArea);
    nodeContainer.appendChild(pilotTagBorder);
  }

  console.log(tagLength);
  pilotTagBorder.style.width = "0%";
  pilotTagBorder.style.transition = "width 0.75s ease-in-out";
  setTimeout(() => {
    pilotTagBorder.style.width = tagLength + "%";
  }, 100);
  return nodeContainer;
}
