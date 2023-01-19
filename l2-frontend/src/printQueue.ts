function getPlanQueue() {
  return JSON.parse(window.localStorage.getItem('planQueue'));
}

export const addIdToPlanQueue = (id) => {
  const currentPrintQueue = getPlanQueue();
  if (currentPrintQueue === null) {
    window.localStorage.setItem('planQueue', JSON.stringify([id]));
  } else if (!currentPrintQueue.includes(id)) {
    currentPrintQueue.push(id);
    window.localStorage.setItem('planQueue', JSON.stringify(currentPrintQueue));
  }
};

export const deleteIdFromPlanQueue = (id) => {
  const currentPrintQueue = getPlanQueue();
  const i = currentPrintQueue.indexOf(id);
  if (i >= 0) {
    currentPrintQueue.splice(i, 1);
    window.localStorage.setItem('planQueue', JSON.stringify(currentPrintQueue));
  }
};

export const checkIdInPlanQueue = (id) => {
  const currentPrintQueue = getPlanQueue();
  if (currentPrintQueue === null) {
    return false;
  }
  return currentPrintQueue.includes(id);
};

export const flushPlanQueue = () => {
  window.localStorage.removeItem('planQueue');
};
