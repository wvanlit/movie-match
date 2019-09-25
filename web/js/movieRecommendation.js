const recommendMovieUrl='http://127.0.0.1:5000/movie-match/recommendMovie/';
const noneFound = "None Found, Try Something Else"

function recommendMovie(title){
	var encodedTitle = encodeURIComponent(title)

	removeListItems();

	var s = ""
    $.get(recommendMovieUrl+encodedTitle, function(data, status){
    	console.log(status);
   		if (data === ""){
   			createListItem(noneFound);
   		}else{
   			s = data.split(';');
    		s.forEach(createListItem)
   		}    	
    }).fail(createListItem(noneFound));

	
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