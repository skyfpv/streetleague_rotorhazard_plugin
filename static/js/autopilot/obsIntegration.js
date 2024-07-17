async function connect(obs, address = "localhost:4444", password = "password") {
  try {
    const { obsWebSocketVersion, negotiatedRpcVersion } = await obs.connect(
      "ws://" + address,
      password,
      {
        rpcVersion: 1,
      }
    );
    console.log(
      `Connected to server ${obsWebSocketVersion} (using RPC ${negotiatedRpcVersion})`
    );
  } catch (error) {
    console.error("Failed to connect", error.code, error.message);
  }
}

function disconnect(obs) {
  obs.disconnect();
}

async function setScene(obs, sceneName) {
  await obs.call("SetCurrentProgramScene", { sceneName: sceneName });
}

async function enableSceneItemBySourceName(
  obs,
  sceneName,
  sourceName,
  itemIndex
) {
  const response = await obs.call("GetSceneItemId", {
    sceneName: sceneName,
    sourceName: sourceName,
    searchOffset: itemIndex,
  });
  console.log(response.sceneItemId);
  await obs.call("SetSceneItemEnabled", {
    sceneName: sceneName,
    sceneItemId: response.sceneItemId,
    sceneItemEnabled: true,
  });
  setScene(obs, sceneName);
}

async function disableSceneItemBySourceName(
  obs,
  sceneName,
  sourceName,
  itemIndex
) {
  const response = await obs.call("GetSceneItemId", {
    sceneName: sceneName,
    sourceName: sourceName,
    searchOffset: itemIndex,
  });
  console.log(response.sceneItemId);
  await obs.call("SetSceneItemEnabled", {
    sceneName: sceneName,
    sceneItemId: response.sceneItemId,
    sceneItemEnabled: false,
  });
  setScene(obs, sceneName);
}

async function startReplayBuffer(obs) {
  await obs.call("StartReplayBuffer", {});
}

async function saveReplayBuffer(obs) {
  await obs.call("SaveReplayBuffer", {});
}

async function stopReplayBuffer(obs) {
  await obs.call("StopReplayBuffer", {});
}

async function startRecord(obs) {
  await obs.call("StartRecord", {});
}

async function stopRecord(obs) {
  await obs.call("StopRecord", {});
}

async function splitRecordFile(obs) {
  //not yet available in the stable obs client
  await obs.call("SplitRecordFile", {});
}
