function selectFigure(id) {
  if (window.postForm) {
    if (window.selectedPosition) {
      window.selectedPosition.style.webkitBoxShadow = 'none';
      window.selectedPosition = null
    }
    if (window.selected) {
      window.selected.style.webkitBoxShadow = 'none';
    }
    if (window.selected != document.getElementById(id)) {
      window.selected = document.getElementById(id);
      window.selected.style.webkitBoxShadow = 'inset 0px 0px 20px 5px rgba(0,100,255,1)';
    } else {
      window.selected = null;
    }
  }
}

function selectPosition(id) {
  if (window.postForm) {
    if (window.selected) {
      if (window.selectedPosition) {
        window.selectedPosition.style.webkitBoxShadow = 'none';
      }
      if (window.selectedPosition != document.getElementById(id)) {
      window.selectedPosition = document.getElementById(id);
      window.selectedPosition.style.webkitBoxShadow = 'inset 0px 0px 20px 5px rgba(0,255,0,1)';
      } else {
        sendPost(window.selected.id, window.selectedPosition.id);
      }
    }
  }
}

function sendPost (start, end) {
  var startColumn = 'ABCDEFGH'.indexOf(start[0]);
  var startRow = start[1] - 1;
  var endColumn = 'ABCDEFGH'.indexOf(end[0]);
  var endRow = end[1] - 1;
  document.getElementById('startColumn').value = startColumn;
  document.getElementById('startRow').value = startRow;
  document.getElementById('endColumn').value = endColumn;
  document.getElementById('endRow').value = endRow;
  document.getElementById('form').submit()
}

const getDeviceType = () => {
  const ua = navigator.userAgent;
  if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
    return "tablet";
  }
  if (
    /Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(
      ua
    )
  ) {
    return "mobile";
  }
  return "desktop";
};

if (getDeviceType() != 'desktop') {
  document.body.innerHTML = `
<div class="centered">
  <div class="card">
    Adaptive design under construction. Please switch to desktop device
  </div>
</div>
`
}
