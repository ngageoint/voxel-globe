/**
 * This class creates and maintains state for the controls for manipulating control points.
 */
function ControlPointOptions(config) {
	this.div = '#' + config.div;
	this.id = config.id;
	this.callback = null;
	this.activePointId = null;
	this.availablePoints = {};
	this.filterImagesToActive = false;
}

ControlPointOptions.prototype.initialize = function(availablePoints, activePointId, selectionCallback, filterCallback) {
	$(this.div).html("");
	if (availablePoints == null) {
		$(this.div).html("");
	} else {
		this.availablePoints = availablePoints;
		// Add a combo box with the available points
		var btnText = '<div id="activePointSelectDiv' + this.id + '" style="display:inline-block;">Active Control Point: ';
		btnText = btnText + '<select id="activePointSelect' + this.id + '">';
		
		// Create the points
		for (var id in availablePoints) {
			var text = availablePoints[id].name;
			//availablePoints[i].pointNdx = i;
			if (availablePoints[id].isInActiveSet) {
				btnText = btnText + '<option value="' + id + '">' + text + '</option>';
			} else {
				btnText = btnText + '<option value="' + id + '" style="display:none;">' + text + '</option>';
			}
		}	
		btnText = btnText + '</select></div>';
		btnText = btnText + '<div id="noActivePointSelectDiv' + this.id + '" style="display:inline-block none;"></div>';
	//	btnText = btnText + '|&nbsp;<input id="filterImagesByControlPoint' + this.id + '" type="radio" disabled></input> Filter Images To Active Control Point';
//		btnText = btnText + '<input id="showAllImages' + this.id + '" type="radio" disabled></input> Use All Images&nbsp;|&nbsp;';
		$(this.div).html(btnText);

		this.selectionCallback = selectionCallback;
		this.filterCallback = filterCallback;
		this.filterImagesToActive = false;
		var that = this;

//		$('#showAllImages' + this.id).prop("checked", "checked");

		this.selectPoint(activePointId);
		
		this.filterCallback(this.filterImagesToActive);
		
		// set up events on buttons and combo box to display the appropriate element
		$('#activePointSelect' + this.id).change(function (e) {
			var items = document.getElementById('activePointSelect' + that.id);
			var selectedVal = items.options[items.selectedIndex].value;
			
			that.selectPoint(parseInt(selectedVal));
		});
/*		
		$('#filterImagesByControlPoint' + this.id).click(function () {
			console.log("Clicked filter images by control point.");
			that.filterImagesToActive = true;
			$('#showAllImages' + that.id).prop("checked", "");
			$('#filterImagesByControlPoint' + that.id).prop("checked", "checked");

			that.filterCallback(that.filterImagesToActive);
		});
		$('#showAllImages' + this.id).click(function () {
			console.log("Clicked show all images.");
			that.filterImagesToActive = false;
			$('#filterImagesByControlPoint' + that.id).prop("checked", "");
			$('#showAllImages' + that.id).prop("checked", "checked");
			
			that.filterCallback(that.filterImagesToActive);
		});
*/		
	}
}

ControlPointOptions.prototype.selectPoint = function(pointId) {
	console.log("Selecting point " + pointId);
	if (pointId == null) {  // If we are selecting nothing, try to find the first available...
		var firstAvailable = null;
		for (var id in this.availablePoints) {
			var text = this.availablePoints[id].name;
			if (this.availablePoints[id].isInActiveSet) {
				firstAvailable = id;
				break;
			}
		}
		this.activePointId = firstAvailable;
	} else {
		this.activePointId = pointId;
	}
	if (this.activePointId != null) {
		$('#noActivePointSelectDiv' + this.id).html("");
		$('#activePointSelectDiv' + this.id).toggle(true);
		$('#activePointSelect' + this.id + ' option[value="' + this.activePointId + '"]').prop("selected", "true");
	} else {
		$('#activePointSelectDiv' + this.id).toggle(false);
		$('#noActivePointSelectDiv' + this.id).html("No Control Points Chosen for Display.");
	}
	console.log("Selected point " + this.activePointId);
	if (this.selectionCallback) {
		if (this.activePointId != null) {
			this.selectionCallback(this.availablePoints[this.activePointId]);
		} else {
			this.selectionCallback(null); // no point selected
		}
	}
};

ControlPointOptions.prototype.refreshSelection = function() {
	this.selectPoint(this.activePointId);
};

ControlPointOptions.prototype.togglePoint = function(pointId) {
	$('#activePointSelect' + this.id + ' option[value="' + pointId + '"]').toggle(this.availablePoints[pointId].isInActiveSet);
}

ControlPointOptions.prototype.updateSelectionForToggle = function(pointId) {
	if (pointId == this.activePointId) { // turned off the currently active point....
		this.selectPoint(null);
	}
	else if (this.activePointId == null && this.availablePoints[pointId].isInActiveSet) {
		this.selectPoint(pointId); // else if we have added one element to the list, go ahead and select it
	}
};


