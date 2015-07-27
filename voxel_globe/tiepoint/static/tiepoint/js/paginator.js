/**
 * This class creates the paging controls for a list of items to be paged.
 */

function Paginator(config) {
	this.div = '#' + config.div;
	this.id = config.id;
	this.callback = null;
	this.visibleItem = 0;
}

Paginator.prototype.initialize = function(numberOfItems, itemsPerPage, displayingItem, callback) {
	$(this.div).html("");
	
	if (numberOfItems == 0) {
		$(this.div).html("");
	} else {
		// Add a prev page button
		// Add a next page button
		// Add a combo box with the page options
		var btnText = '<button id="prevBtn' + this.id + '">Previous Page</button>';
		btnText = btnText + '<select id="pageSelect' + this.id + '">';
		
		// Create the options
		this.numberOfPages = Math.ceil(numberOfItems/itemsPerPage);
		this.currentPage = Math.floor(displayingItem/itemsPerPage) + 1;
		this.itemsPerPage = itemsPerPage;
		var pageCount = 1;
		for (var i = 0; i < numberOfItems; i += itemsPerPage) {
			var text = "Page " + pageCount + " of " + this.numberOfPages;
			btnText = btnText + '<option value="' + pageCount + '">' + text + '</option>';
			pageCount++;
		}	
		btnText = btnText + '</select>';
		btnText = btnText + '<button id="nextBtn' + this.id + '">Next Page</button>';
		$(this.div).html(btnText);
		
		this.callback = callback;
		var that = this;

		this.selectPage(this.currentPage);
		// set up events on buttons and combo box to display the appropriate element
		$('#pageSelect' + this.id).change(function (e) {
			var items = document.getElementById('pageSelect' + that.id);
			var selectedVal = items.options[items.selectedIndex].value;
			
			that.selectPage(parseInt(selectedVal));
		});
		$('#prevBtn' + this.id).click(function (e) {
			that.selectPage(that.currentPage-1);
		});
		
		$('#nextBtn' + this.id).click(function (e) {
			that.selectPage(that.currentPage+1);
		});
	}
}

Paginator.prototype.selectPage = function(pageValue) {
	console.log("Selecting page " + pageValue);
	if (pageValue == 1) {
		$('#prevBtn' + this.id).prop("disabled", "disabled");
	} else {
		$('#prevBtn' + this.id).prop("disabled", null);
	}
	if (pageValue == this.numberOfPages) {
		$('#nextBtn' + this.id).prop("disabled", "disabled");
	} else {
		$('#nextBtn' + this.id).prop("disabled", null);
	}
	this.currentPage = pageValue;
	$('#pageSelect' + this.id + ' option[value="' + this.currentPage + '"]').prop("selected", "true");
	if (this.callback) {
		this.callback((pageValue - 1) * this.itemsPerPage);
	}
}

