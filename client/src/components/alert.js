import M from 'materialize-css';

const showError = (text) => {
  const html = `<i class="material-icons">warning</i> <span style="margin-left: 10px;">${text}</span>`;

  M.toast({
    html,
    displayLength: 10000,
    classes: 'rounded red lighten-1',
  });
};

const showWarning = (text) => {
  const html = `<i class="material-icons">warning</i> <span style="margin-left: 10px; color: black">${text}</span>`;

  M.toast({
    html,
    displayLength: 10000,
    classes: 'rounded orange lighten-3',
  });
};

export { showError, showWarning };
