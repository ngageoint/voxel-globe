function Tooltip(parent) {
  var el = document.getElementById("tooltip");
  var lastEvent;
  var on = true;
  var parentId = parent;
  setHoverListeners();

  function setHoverListeners() {
    $("#tooltip, #" + parentId)
    .mouseenter(function(e) {
      show();
    })
    .mouseleave(function(e) {
      hide();
    })
    .mousemove(function(e) {
      if (on) {
        lastEvent = e;
        $("#tooltip").css({
          "left": e.clientX - ($("#tooltip").outerWidth() + 4),
          "top": e.clientY - ($("#tooltip").outerHeight() + 4)
        });
      }
    });
  }

  function removeHoverListeners() {
    $("#tooltip, #" + parentId).off();
  }

  function show() {
    if (on) {
      el.style.display = "block";
    }
  }

  function hide() {
    el.style.display = "none";
  }

  this.text = function(str) {
    if (on) {
      el.innerHTML = str;
      if (lastEvent) {
        $("#tooltip").css({
          "left": lastEvent.clientX - ($("#tooltip").outerWidth() + 4),
          "top": lastEvent.clientY - ($("#tooltip").outerHeight() + 4)
        }); 
      }
    }
  }

  this.turnOff = function(elementId) {
    on = false;
    removeHoverListeners();
    hide();
  }
}

