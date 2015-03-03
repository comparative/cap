$(document).ready(function() {

	$("#updates").focus(function() {
  		
  		$(this).val("");
  		
  		$('#social').addClass('show-for-large-only');
  		
  		$('#email').removeClass('medium-2');
  		$('#email').addClass('medium-4');
  	
        $('#updates-container').removeClass('medium-12');
        $('#updates-container').addClass('medium-8');

        $('#go-container').addClass('medium-4');
        
        setTimeout(function(){ $('#go-container').show(); }, 500);

	});
	
		
	$(".panel").hover(function() {
	
		$(this).addClass('highlight');	
	
	}, function() {
	
		$(this).removeClass('highlight');
	
	});
	
});