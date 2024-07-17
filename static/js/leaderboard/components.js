// static/js/fpvoverlay/components.js

export function createLeaderboardGird(
  name,
  results,
  colorClass,
  scrollDistance,
  scrollDelay,
  scrollCount
) {
  const itemFadeOffset = 100;
  const itemFadeTime = 500;
  const leaderboardExpandTime = 500;

  const container = document.createElement("div");
  container.className = `overflow-hidden h-screen w-full`;

  //Create leaderboard name
  const leaderboardName = document.createElement("p");
  leaderboardName.className = `relative text-4xl w-full`;
  leaderboardName.textContent = name;

  //Create divider
  const divider = document.createElement("div");
  divider.className = `relative my-4 h-0.5 border-t-0 bg-neutral-100 dark:bg-white/10`;

  //create scrollable results
  const scrollableResults = document.createElement("div");
  scrollableResults.className = `scrollableResults relative h-[100%] overflow-y-auto w-full`;
  scrollableResults.style = `
    scrollbar-width: none;
    ::-webkit-scrollbar {
      display: none;
    }
    -ms-overflow-style: none;
    .scrollable-content {
      scrollbar-width: none;
    }`;

  scrollableResults.appendChild(leaderboardName);
  scrollableResults.appendChild(divider);

  const tableItemClass = `flex-1 mx-1 w-[25px] text-ellipsis text-nowrap overflow-hidden whitespace-nowrap`;
  const tablePosClass = `w-[60px] text-nowrap overflow-hidden whitespace-nowrap`;
  const tablePilotClass = `flex-1 mx-2 min-w-[175px] text-ellipsis text-nowrap overflow-hidden whitespace-nowrap`;
  const tableRowClass = `flex min-h-11 w-full`;

  // Create table headers
  const headerRow = document.createElement("div");
  headerRow.className = tableRowClass;
  for (const [key, value] of Object.entries(results[0])) {
    const item = document.createElement("div");

    if (key === "Pos") {
      item.className = tablePosClass;
      item.textContent = "";
    } else if (key === "Pilot") {
      item.textContent = key;
      item.className = tablePilotClass;
    } else {
      item.className = tableItemClass;
      item.textContent = key;
    }
    item.style.transition = `opacity ${itemFadeTime}ms ease-in-out`;
    item.style.opacity = "0.0";
    setTimeout(() => {
      item.style.opacity = "1.0";
    }, leaderboardExpandTime);
    headerRow.appendChild(item);
  }
  scrollableResults.appendChild(headerRow);

  // Create table rows
  for (let i = 0; i < results.length; i++) {
    const row = document.createElement("div");
    row.className = tableRowClass;
    const result = results[i];
    for (const [key, value] of Object.entries(result)) {
      const item = document.createElement("div");
      item.textContent = value;
      if (key === "Pos") {
        item.className = tablePosClass;
        item.textContent = `${value}${nth(value)}`;
      } else if (key === "Pilot") {
        item.className = tablePilotClass;
      } else if (key === "Source") {
        item.className = tableItemClass;
        item.textContent = value.displayname;
      } else {
        item.className = tableItemClass;
      }

      item.style.transition = `opacity ${itemFadeTime}ms ease-in-out`;
      item.style.opacity = "0.0";
      setTimeout(() => {
        item.style.opacity = "1.0";
      }, leaderboardExpandTime + i * itemFadeOffset);
      row.appendChild(item);
    }
    scrollableResults.appendChild(row);
  }

  const leaderboardContainer = document.createElement("div");
  //leaderboardContainer.className = `relative h-[100%] overflow-hidden border-gray-300/75 w-[62px] p-[6px] rounded-[26px] bg-gradient-to-tl from-gray-600/60 from-25% via-gray-500/60 via-50% to-${colorClass} to-80%`;
  leaderboardContainer.className = `spin-gradient relative h-[100%] overflow-hidden border-gray-300/75 border-purple-500 w-[62px] p-[6px] rounded-[26px] bg-gray-500/60`;

  //leaderboardContainer.classList.add("spin-gradient");

  const leaderboardContent = document.createElement("div");
  leaderboardContent.className = `relative h-[100%] overflow-hidden w-full p-5 font-bold font-mono text-2xl text-white whitespace-nowrap text-clip text-nowrap rounded-[20px] bg-gradient-to-b from-slate-700 from-0% to-slate-800 to-100%`;

  leaderboardContent.appendChild(scrollableResults);

  leaderboardContainer.appendChild(leaderboardContent);
  leaderboardContainer.style.width = "62px";
  leaderboardContainer.style.transition = `width ${leaderboardExpandTime}ms ease-in-out`;
  setTimeout(() => {
    leaderboardContainer.style.width = "100%";
  }, 100);
  container.appendChild(leaderboardContainer);

  if (scrollCount > 0) {
    setTimeout(() => {
      let scrolls = 0;
      let scrollReverse = false;
      setInterval(function () {
        if (!scrollReverse) {
          scrollableResults.scrollBy(0, scrollDistance);
          if (scrolls != scrollCount) {
            scrolls++;
          } else {
            scrolls--;
            scrollReverse = true;
          }
        } else {
          scrollableResults.scrollBy(0, -scrollDistance);
          if (scrolls != 0) {
            scrolls--;
          } else {
            scrolls++;
            scrollReverse = false;
          }
        }
      }, scrollDelay);
    }, leaderboardExpandTime + 3000 + results.length * itemFadeOffset);
  }

  return container;
}

function nth(n) {
  return ["st", "nd", "rd"][((((n + 90) % 100) - 10) % 10) - 1] || "th";
}
