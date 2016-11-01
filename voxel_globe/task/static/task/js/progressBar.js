function ProgressBar() {}

ProgressBar.prototype.initialize = function(parent, total, id) {
  this.total = total;
  this.progress = 0;
  this.parent = $("#" + parent);
  $("#" + parent).append('<div class="progress-bar-outer"></div>');
  $(".progress-bar-outer").append('<div class="progress-bar-inner"></div>');
  this.outer = $("#" + parent).find(".progress-bar-outer");
  this.inner = this.outer.find(".progress-bar-inner");
  if (id) {
    this.outer.attr("id", id);
  }
}

ProgressBar.prototype.update = function(number, callback) {
  this.progress = number;
  var percent = 100;
  if (this.progress < this.total) {
    percent = this.progress / this.total * 100;
  }
  this.inner.off();

  var that = this;
  this.inner.on("transitionend webkitTransitionEnd " + 
      "oTransitionEnd MSTransitionEnd", function() {
    if (typeof callback == 'function') {
      callback();
    }
  });

  this.inner.width("calc(" + percent + "% - 2px)");
}

ProgressBar.prototype.updateTotal = function(newTotal) {
  this.total = newTotal;
  if (this.progress > this.total) {
    this.inner.width("100%");
  }
}

ProgressBar.prototype.destroy = function() {
  this.outer.remove();
}