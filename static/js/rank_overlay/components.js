// static/js/fpvoverlay/components.js

export function createPilotCard(
  callsign,
  colorClass,
  tagLength,
  tagHeight,
  interval,
  position
) {
  const nodeContainer = document.createElement("div");
  nodeContainer.className = `pilot-card flex flex-col h-[${tagHeight}px] w-full`;
  nodeContainer.style.transform = `translateY(${position * tagHeight * 0}px)`;

  const pilotTagBorder = document.createElement("div");
  pilotTagBorder.className = `pilot-border flex h-[${tagHeight}px] text-nowrap border-y-[1px] border-gray-300/75 overflow-hidden w-[0%] bg-gradient-to-l from-gray-600/60 from-0% to-[${colorClass}]/60 to-100%`;

  const pilotTag = document.createElement("div");
  pilotTag.className = `h-full w-full text-nowrap overflow-hidden flex bg-gradient-to-r from-slate-700/15 from-0% to-slate-600 to-100%`;

  const pilotPosition = document.createElement("div");
  pilotPosition.className = `position text-lg text-white font-mono font-bold w-[50px] px-2`;
  pilotPosition.textContent = `${position}`;

  const pilotCallsign = document.createElement("div");
  pilotCallsign.className = `w-[400px] text-lg text-white font-mono font-bold px-2 text-nowrap w-full text-left overflow-hidden whitespace-nowrap text-clip`;
  pilotCallsign.textContent = callsign.toUpperCase();

  const pilotInterval = document.createElement("div");
  pilotInterval.className = `interval w-full text-lg text-white font-mono font-bold px-2 text-right`;
  pilotInterval.textContent = `${interval}`;

  pilotTagBorder.appendChild(pilotTag);
  pilotTag.appendChild(pilotPosition);
  pilotTag.appendChild(pilotCallsign);
  pilotTag.appendChild(pilotInterval);
  nodeContainer.appendChild(pilotTagBorder);

  pilotTagBorder.style.width = "100%";
  // pilotTagBorder.style.transition = "width 0.75s ease-in-out";
  // setTimeout(() => {
  //   pilotTagBorder.style.width = tagLength + "%";
  // }, 100);
  // setTimeout(() => {
  //   nodeContainer.style.transform = `translateX(${0}px)`;
  // }, 100);
  return nodeContainer;
}

export function ordinal(n) {
  return ["st", "nd", "rd"][((((n + 90) % 100) - 10) % 10) - 1] || "th";
}
