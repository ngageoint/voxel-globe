$(document).ready(function() {
  var ws = new WebSocketMain();
});

/*
 * WebSocketMain handles the logic for connecting to the django channels,
 * as well as displaying data it gets from this connection to the users
 * via a notification system (noty.js) and the menu panels available by
 * clicking Tasks or Logs at the top right of the screen.
 */

function WebSocketMain() {
  this.activeDropdown = null;
  this.progressBars = {};
  this.noRevoke = [];
  this.unread = [];
  this.initializeDropdown("task");
  this.initializeDropdown("log");
  this.initializeDropdown("user_tools");
  this.connect();
}

/*
 * Attaches listeners so that the top-right menus toggle open/closed when their
 * respective buttons are clicked, and can never be opened when one of their
 * neighbors is open. Hides popup notifications when a dropdown is opened.
 */

WebSocketMain.prototype.initializeDropdown = function(name) {
  var that = this;

  $("#" + name + "_button").click(function(e) {
    e.preventDefault();
    if (that.activeDropdown == name) {
      that.activeDropdown = null;
      $(".notifications").show();
    } else {
      that.activeDropdown = name;
      $(".notifications").hide();
      $(".notifications").html('')
      if (name == "log") {
        that.markReadMessages();
      }
    }
    $(".menu:not(#" + name + "_panel), .menu_carrot:not(#" + 
        name + "_panel_carrot)").hide();
    $("#" + name + "_panel, #" + name + "_panel_carrot").toggle();
  });
}

/*
 * Attaches a click listener to the revoke button for a task with the given id.
 */

WebSocketMain.prototype.attachRevokeListener = function(id) {
  var that = this;

  if (that.noRevoke.indexOf(id) != -1) {
    $(".revoke"+id).hide();
    return;
  }

  $(".revoke"+id).button();

  $(".revoke"+id).click(function() {
    console.log('Revoking ' + id);
    $.ajax({
      type: "POST",
      url: "/apps/task/revoke/",
      data: {task_id: id}
    })
  });
}

/*
 * Creates or updates a progress bar for the task.
 */

WebSocketMain.prototype.progressBar = function(task) {
  var that = this;

  if (!task || !task.state) {
    return;
  }

  var state = task.state;
  var key = 'progress-task' + task.id;
  var pgb = that.progressBars[key];

  if (!task.result || state == "Success" || 
      state == "Failure" || state == "Revoked") {
    if (pgb) {
      pgb.destroy();
      that.progressBars[key] = undefined;
    }
    return;
  }

  var index = task.result.index ? task.result.index : task.result.i;
  var total = task.result.total;
  index = index ? index : 0;

  if (total === undefined) {
    return;
  }

  if (!pgb) {
    pgb = new ProgressBar();
    pgb.initialize('task' + task.id, total);
    pgb.update(index);
    that.progressBars[key] = pgb;
    return;
  }

  pgb.update(index);
}

WebSocketMain.prototype.markUnreadMessages = function(log_id) {
  var that = this;
  if (log_id) {
    that.unread.push(log_id);
  }
  if (that.activeDropdown == 'log') {
    that.markReadMessages();
    return;
  }
  if (that.unread.length > 0) {
    $("#unread").html("(" + that.unread.length + ")");
    var panelRight = parseInt($("#user_tools_panel").css("right"));
    var carrotRight = parseInt($("#user_tools_panel_carrot").css("right"));
    var width = $("#unread").outerWidth() + 4;
    $("#user_tools_panel").css("right", (panelRight + width) + "px");
    $("#user_tools_panel_carrot").css("right", (carrotRight + width) + "px");
  }
}

WebSocketMain.prototype.markReadMessages = function() {
  var that = this;
  if (!that.unread.length > 0) {
    return;
  }
  $("#unread").html("");
  $("#user_tools_panel").css("right", "125px");
  $("#user_tools_panel_carrot").css("right", "155px");
  $.ajax({
    type: "POST",
    url: "/apps/task/mark_as_read/",
    data: {log_ids: JSON.stringify(that.unread)},
    success: function() {
      that.unread = [];
    }
  });
}

/*
 * Connects to the websocket server. On receiving a message, checks if it's
 * a task status update, or a log message, and calls the appropriate function.
 * On open, load all the existing logs and tasks.
 * TODO: port number 1080 is hard-coded
 */
WebSocketMain.prototype.connect = function() {
  var that = this;
  that.socket = new WebSocket("ws://localhost:1080/ws_logger/" + userId + "/" + websocketSessionKey + "/");
  that.socket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    if (data.type == "status_update") {
      that.notifyTask(data.task, true);
    } else {
      that.markUnreadMessages(data.log_id);
      if (data.type == "log") {
        that.notifyLog(data.task.id, data.log_level, data.message_text, true);
      } else if (data.type == "message") {
        that.notifyMessage(data.task.id, data.message_text, true);
      }
    }
  }

  that.socket.onopen = function() {
    that.loadTasks();
    that.loadLogs();
  }
}

/*
 * Load existing tasks from the db and add them to the tasks panel.
 */
 
WebSocketMain.prototype.loadTasks = function() {
  var that = this;
  $.ajax({
    type: "GET",
    url: "/meta/rest/serviceinstance/",
    success: function(data) {
      var len = data.length;
      var tasks = [];
      var taskIds = [];

      if (len == 0) {
        $("#no_task").html("No tasks initiated yet.");
        $("#no_log").html("No messages logged yet.");
        return;
      }

      for (task of data) {
        task.finish_time = Date.parse(task.finish_time);
        tasks.push(task);
        taskIds.push(task.id);
      }

      tasks.sort(function(x, y) {
        return x.finish_time - y.finish_time;
      });
      tasks.sort();

      var i = 0;
      sendTask();

      function sendTask() {
        var t = tasks[i];
        that.makeTaskDiv(t.id);

        var task = {
          "id" : t.id,
          "path" : t.service_name,
          "name" : that.prettyName(t.service_name),
          "state" : t.status,
          "result" : t.outputs
        }

        var deferred = that.notifyTask(task, false);

        $.when(deferred).then(function() {
          i += 1;
          if (i < len) {
            sendTask();
          }
        });
      }
    }
  });
}

/*
 * Load existing logs from the db. Notify only if their task id is in
 * the task_ids array passed in, otherwise they're too old and no
 * longer relevant.
 */

WebSocketMain.prototype.loadLogs = function() {
  var that = this;
  $.ajax({
    type: "GET",
    url: "/apps/websockets/logmessage/",
    success: function(data) {
      var messages = data;
      var len = messages.length;
      if (len == 0) {
        $("#no_log").html("No messages logged yet.");
      }

      for (message of messages) {
        message.timestamp = parseDate(message.timestamp);
        if (message.read == false) {
          that.unread.push(message.id);
        }
      }

      messages.sort(function(x, y) {
        return x.timestamp - y.timestamp;
      });
      messages.sort();

      for (message of messages) {
        if (message.message_type == 'Message') {
          that.notifyMessage(message.task_id, message.message_text, false);
        } else {
          that.notifyLog(message.task_id, message.message_type, message.message_text, false);
        }
      }
    }
  });

  function parseDate(str) {
    str = str.slice(0, 19);
    str = str.split('-').join('/');
    str = str.replace('T', ' ');
    var date = Date.parse(str);
    return date;
  }
}

/*
 * Request a specific task template and on success send it to the
 * sendNotification function. alertBool is true if the task should have a pop-up
 * notification, false otherwise.
 */

WebSocketMain.prototype.notifyTask = function(task, alertBool) {
  var that = this;
  var state = task.state;
  var type = that.getNotificationType(state);

  if (state == "Success" || state == "Failure" || state == "Revoked") {
    that.noRevoke.push(task.id);
    $(".revoke"+task.id).hide();
  }

  if (typeof task.result == 'string') {
    task.result = JSON.parse(task.result);
  }

  return $.ajax({
    type : "POST",
    url : "/apps/task/status/",
    data : {
      json_data : JSON.stringify(task)
    },
    success : function(data) {
      that.sendNotification(data, 'task', type, alertBool, 'task'+task.id);
      that.attachRevokeListener(task.id);
      that.progressBar(task);
    }
  });
}

/*
 * Notify a specific log message. alertBool is true if the task should have 
 * a pop-up notification, false otherwise.
 */

WebSocketMain.prototype.notifyLog = function(taskId, logLevel, message, alertBool) {
  var that = this;
  var display_text = '(' + logLevel + ') ' + taskId + ': ' + message
  var type = that.getNotificationType(logLevel);
  that.sendNotification(display_text, 'log', type, alertBool);
}

/*
 * Notify a message about a task. Like logs, these go in the "Inbox" menu,
 * but unlike logs, they aren't constrained to the standard five log levels,
 * and are just intended to tell the user something important.
 */

WebSocketMain.prototype.notifyMessage = function(taskId, message, alertBool) {
  var that = this;
  var display_text = '(' + taskId + ') ' + message;
  var type = 'alert';
  that.sendNotification(display_text, 'log', type, alertBool);
}

/*
 * General wrapper function for sending out various notifications. Determines 
 * whether there are any menus open then adjusts alertBool accordingly.
 * Sends notification to the popup method, notifyAlert(), if alertBool is true
 * sends notification to notifyPanel() either way.
 */
WebSocketMain.prototype.sendNotification = function(message, divName, 
    notificationType, alertBool, replaceId) {
  var that = this; 
  if ($(".menu:visible").length > 0) {
    // don't send popups if any menus are open
    alertBool = false;
  }
  if (alertBool) {
    that.notifyAlert(message, notificationType);
  }
  $("#no_" + divName).css("display","none");
  that.notifyPanel(message, notificationType, divName + '_inner', replaceId);
}

/*
 * Parses the text of the message to figure out its notification type.
 * Counterintuitively, noty.js's styling has 'alert' as the default type
 * with regular black-on-white styling, which is why that's the default
 * here if none of the keywords are found within the string.
 */

WebSocketMain.prototype.getNotificationType = function(type) {
  var notification_type = 'alert';
  if (type == "Success") {
    notification_type = 'success';
  } else if (type == "Failure" || type == "Error" || type == "Fatal") {
    notification_type = 'error';
  } else if (type == "Warn") {
    notification_type = 'warning';
  }
  return notification_type;
}

/*
 * Adds an alert notification, which appears at the upper right of the screen
 * and fades out after 5 seconds.
 */

WebSocketMain.prototype.notifyAlert = function(message, notificationType) {
  var n = $(".notifications").noty({
    text: message,
    layout: 'topRight',
    closeWith: ['click', 'button'],
    theme: 'relax',
    timeout: 5000,
    type: notificationType,
    maxVisible: 5,
    callback: {
      afterShow: function() {
        $(this).find(".revoke").button();
        $(".noty_message").css("text-align", "left");
      }
    }
  });
}

/*
 * Adds a notification to one of the menu panels.
 *
 * message - the text of the message to notify
 * notificationType - controls the styling (green, red, yellow, or white)
 * notificationDivName - which panel to add the notification to
 * replaceId - if the notification with the given replaceId already exists,
 *   instead of making a new notification item, replace the text of the old
 *   one with the new message.
 */

WebSocketMain.prototype.notifyPanel = function(message, 
    notificationType, notificationDivName, replaceId) {
  var that = this;

  if (!replaceId) {
    replaceId = "";
  }
  
  var innerDomString =
      '<div class="noty_bar noty_type_' + notificationType + '">' +
        '<div class="noty_message noty-message-style">' +
          '<span class="noty_text">' +
            message +
          '</span>' +
        '</div>' +
      '</div>'

  if (replaceId && $("#" + replaceId).length) {
    var $replaceDiv = $("#" + replaceId).detach();
    $("#" + notificationDivName).prepend($replaceDiv);
    var domString = innerDomString;
    $("#" + replaceId).removeClass();
    $("#" + replaceId).addClass('noty-' + notificationType);
    $("#" + replaceId).find(".noty_bar").remove();
    $("#" + replaceId).prepend(domString);
  } else {
    var domString = 
      '<li class="noty-' + notificationType + '" + id="' + replaceId + '">' +
        innerDomString + 
      '</li>'
    $("#" + notificationDivName).prepend(domString);
  }

  $(".revoke").button();
  $(".noty_message").css({"text-align": "left", "font-weight":"normal"});
  $(".menu-content").css("padding-bottom", "15px");
}

/*
 * Given the task id, pre-create the notification panel div so that in the case
 * of many tasks loading at once on page load, they will all still end up in
 * the right order.
 */

WebSocketMain.prototype.makeTaskDiv = function(task_id) {
  if ($("#task" + task_id).length != 0) {
    return;
  }
  var taskDomString = '<li id="task' + task_id + '"></li>'
  $("#task_inner").prepend(taskDomString);
}

/* 
 * Return a title-ized version of the task path.
 */

WebSocketMain.prototype.prettyName = function(path) {
  String.prototype.toTitleCase = function () {
    return this.replace(/\w\S*/g, function(txt){
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
  };
  var index = path.search(/.([A-Za-z_]+)$/);
  var prettyName = path.slice(index, path.length);
  prettyName = prettyName.replace(".", "");
  prettyName = prettyName.replace("_", " ");
  prettyName = prettyName.toTitleCase();
  return prettyName;
}