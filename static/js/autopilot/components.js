// static/js/autopilot/components.js

export function createButton(text, onClick, colorClass) {
  const buttonContainer = document.createElement("div");
  buttonContainer.className = "flex-auto";
  const button = document.createElement("button");
  button.innerText = text;
  button.className = `${colorClass} hover:opacity-75 text-white font-bold py-2 px-4 rounded flex-auto `;
  button.addEventListener("click", onClick);
  return button;
}

export function createAutoPilotButton(text, onClick) {
  const button = document.createElement("div");
  button.className = `hover:opacity-75 shadow-inner col-start-2 rounded-full overflow-hidden`;
  button.style =
    "background: radial-gradient(circle,#6bfca0f9 0%,rgba(255, 255, 255, 1) 100%);";
  button.addEventListener("click", onClick);

  const mainButtonText = document.createElement("div");
  mainButtonText.className =
    "mt-7 text-3xl font-bold text-center text-gray-700";
  mainButtonText.innerText = "Auto Pilot";

  const subButtonText = document.createElement("div");
  subButtonText.className = "mb-2 text-center text-gray-700";
  subButtonText.innerText = text;

  button.appendChild(mainButtonText);
  button.appendChild(subButtonText);
  button.dataset.enabled = "true"; // Add this line to set the initial state

  return button;
}

export function createStateDisplay() {
  const pre = document.createElement("pre");
  pre.id = "state-display";
  pre.className = "bg-white p-4 rounded shadow-md";
  return pre;
}

export function createEventComponent(
  event,
  triggers,
  actions,
  onDelete,
  onUpdate,
  onDuplicate
) {
  const container = document.createElement("div");
  container.className = "bg-white p-4 rounded shadow-md ";
  container.dataset.eventId = event.id;

  const nameLabel = document.createElement("label");
  nameLabel.innerText = "Event Name:";
  nameLabel.className = "block text-gray-700 font-bold mb-2";

  const nameInput = document.createElement("input");
  nameInput.type = "text";
  nameInput.placeholder = "Event Name";
  nameInput.value = event.name || "";
  nameInput.className = "w-full p-2 rounded border";
  nameInput.addEventListener("input", () =>
    onUpdate(event.id, { name: nameInput.value })
  );

  const eventPropsContainer = document.createElement("div");
  eventPropsContainer.className = "grid grid-cols-2 gap-4";

  const trigger = document.createElement("div");

  const triggerLabel = document.createElement("label");
  triggerLabel.innerText = "Trigger:";
  triggerLabel.className = "block text-gray-700 font-bold mb-2";

  const triggerSelect = document.createElement("select");
  triggerSelect.className = "w-full p-2 rounded border";
  triggers.forEach((trigger) => {
    const option = document.createElement("option");
    option.value = trigger.value;
    option.text = trigger.label;
    triggerSelect.appendChild(option);
  });
  triggerSelect.value = event.trigger;
  triggerSelect.addEventListener("change", () =>
    onUpdate(event.id, { trigger: triggerSelect.value })
  );

  const action = document.createElement("div");

  const actionLabel = document.createElement("label");
  actionLabel.innerText = "Action:";
  actionLabel.className = "block text-gray-700 font-bold mb-2";

  const actionSelect = document.createElement("select");
  actionSelect.className = "w-full p-2 rounded border";
  actions.forEach((action) => {
    const option = document.createElement("option");
    option.value = action.value;
    option.text = action.label;
    actionSelect.appendChild(option);
  });
  actionSelect.value = event.action;
  actionSelect.addEventListener("change", () => {
    onUpdate(event.id, { action: actionSelect.value });
    updateParameters(event.id, actionSelect.value);
  });

  const parameterContainer = document.createElement("div");
  parameterContainer.className = "col-span-2 mt-4";

  function updateParameters(eventId, actionValue) {
    parameterContainer.innerHTML = ""; // Clear existing parameters

    const action = actions.find((action) => action.value === actionValue);
    if (action && action.params) {
      action.params.forEach((param) => {
        const paramLabel = document.createElement("label");
        paramLabel.innerText = param.label;
        paramLabel.className = "block text-gray-700 font-bold mb-2";

        let paramInput;
        switch (param.type) {
          case "text":
            paramInput = document.createElement("input");
            paramInput.type = "text";
            paramInput.value = event.params
              ? event.params[param.label] || ""
              : "";
            break;
          case "number":
            paramInput = document.createElement("input");
            paramInput.type = "number";
            paramInput.value = event.params
              ? event.params[param.label] || ""
              : "";
            break;
          case "checkbox":
            paramInput = document.createElement("input");
            paramInput.type = "checkbox";
            paramInput.checked = event.params
              ? event.params[param.label] || false
              : false;
            break;
          case "select":
            paramInput = document.createElement("select");
            paramInput.className = "w-full p-2 rounded border";
            param.options.forEach((option) => {
              const optionElement = document.createElement("option");
              optionElement.value = option.value;
              optionElement.text = option.label;
              paramInput.appendChild(optionElement);
            });
            paramInput.value = event.params
              ? event.params[param.label] || "" // Set the default value
              : ""; // Set the default value
            break;
        }

        paramInput.className = "w-full p-2 rounded border";
        paramInput.addEventListener("input", () => {
          onUpdate(eventId, {
            params: {
              ...event.params,
              [param.label]:
                paramInput.type === "checkbox"
                  ? paramInput.checked
                  : paramInput.value,
            },
          });
        });

        parameterContainer.appendChild(paramLabel);
        parameterContainer.appendChild(paramInput);
      });
    }
  }

  // Initialize parameters for the current action
  updateParameters(event.id, event.action);

  const deleteButton = createButton(
    "Delete",
    () => onDelete(event.id),
    "bg-red-500 mt-4"
  );

  const duplicateButton = createButton(
    "Duplicate",
    () => onDuplicate(event),
    "bg-blue-500 mx-4 mt-4"
  );

  const statusIndicator = document.createElement("div");
  statusIndicator.className =
    "w-2 h-full rounded-r-sm  status bg-gradient-to-t bg-red-300 from-red-500";
  statusIndicator.style.position = "absolute";
  statusIndicator.style.top = "0";
  statusIndicator.style.right = "0";
  container.style.position = "relative";

  trigger.appendChild(triggerLabel);
  trigger.appendChild(triggerSelect);
  eventPropsContainer.appendChild(trigger);

  action.appendChild(actionLabel);
  action.appendChild(actionSelect);
  eventPropsContainer.appendChild(action);

  container.appendChild(nameInput);
  container.appendChild(eventPropsContainer);
  container.appendChild(parameterContainer); // Append the parameter container
  container.appendChild(deleteButton);
  container.appendChild(duplicateButton);
  container.appendChild(statusIndicator);

  return container;
}
