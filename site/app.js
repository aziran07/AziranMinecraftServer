// Copy the server address to the clipboard, and tell the visitor what actually happened.
// A success message appears only when the clipboard write resolves; otherwise the address
// is selected so the visitor can copy it by hand.

const MANUAL_COPY_HINT =
  '복사하지 못했습니다. 주소를 선택해 두었으니 Ctrl+C(맥은 Cmd+C)로 복사하세요.';

function selectElementText(element) {
  const selection = window.getSelection();
  if (!selection) {
    return;
  }
  const range = document.createRange();
  range.selectNodeContents(element);
  selection.removeAllRanges();
  selection.addRange(range);
}

function showStatus(statusElement, message, state) {
  statusElement.textContent = message;
  statusElement.dataset.state = state;
}

async function copyAddress(button, addressElement, statusElement) {
  const address = addressElement.textContent.trim();

  try {
    if (!navigator.clipboard) {
      throw new Error('clipboard API unavailable');
    }
    await navigator.clipboard.writeText(address);
  } catch (error) {
    console.warn('클립보드 복사에 실패했습니다.', error);
    showStatus(statusElement, MANUAL_COPY_HINT, 'fail');
    addressElement.focus();
    selectElementText(addressElement);
    return;
  }

  showStatus(statusElement, `서버 주소 ${address} 를 복사했습니다.`, 'ok');
  button.focus();
}

function setUpCopyButton() {
  const button = document.getElementById('copy-address');
  const statusElement = document.getElementById('copy-status');
  if (!button || !statusElement) {
    return;
  }

  const addressElement = document.getElementById(button.dataset.copyTarget);
  if (!addressElement) {
    return;
  }

  button.addEventListener('click', () => {
    copyAddress(button, addressElement, statusElement);
  });
}

setUpCopyButton();
