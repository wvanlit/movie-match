const recommendMovieUrl='http://127.0.0.1/movie-match/recommendMovie/';
const noneFound = "None Found, Try Something Else"

function recommendMovie(title){
	var encodedTitle = encodeURIComponent(title)

	removeListItems();

	$.ajax({
        type: "GET",
        url: recommendMovieUrl+encodedTitle,
        success: function (result) {
        	console.log(result);
	   		if (result === ""){
	   			createListItem(noneFound);
	   		}else{
	   			s = result.split(';');
	    		s.forEach(createListItem)
	   		}  
        },
        error: function (jqXHR, textStatus, errorThrown) {
        	createListItem(noneFound);
        }
    });
}

function removeListItems(){
	$('.list-group-item').remove();
	$('.list-group-item-action').remove();
	$('#list-None Found, Try Something Else').remove();
}

function createListItem(title){
	// List Tag Setup
	var listClass = 'class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" '
	
	if (title === noneFound){
		var listID = 'id="error" '
	}else{
		var listID = 'id="list-'+title+'" '
	}
	
	// List Tag
	var listTagOpen = '<a '+listClass+listID+'>'
	var listTagClose = '</a>'

	$('.list-group').append(listTagOpen+title+listTagClose);
}