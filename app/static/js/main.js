$(document).ready(function() {
    
    $(".scrollable p").hover(function() {

        $(this).addClass('country-hover');	

    }, function() {

        $(this).removeClass('country-hover');

    });
    
    $("ul.slider li").addClass('slideborder-off');
    $("img#trends-tool").addClass('trends-tool-off');

	$("#updates").focus(function() {
  		
  		$(this).val("");
  		
  		//$('#social').addClass('show-for-large-only');
  		
  		//$('#email').removeClass('medium-2');
  		//$('#email').addClass('medium-4');
  	
        //$('#updates-container').removeClass('medium-12');
        //$('#updates-container').addClass('medium-8');

        //$('#go-container').addClass('medium-4');
        
        //setTimeout(function(){ $('#go-container').show(); }, 500);
        
        $('#go-container').show();

	});
	
		
	$(".panel").hover(function() {
	
		$(this).addClass('highlight');	
	
	}, function() {
	
		$(this).removeClass('highlight');
	
	});
	
	
	$("ul.slider li").hover(function() {
	    
	    $(this).removeClass('slideborder-off');
		$(this).addClass('slideborder');
		
		//$(".orbit-caption a").addClass('bold-link');
		$(".orbit-caption a").show();
		
	
	}, function() {
	
		$(this).removeClass('slideborder');
		$(this).addClass('slideborder-off');
	    
	   // $(".orbit-caption a").removeClass('bold-link');
	   $(".orbit-caption a").hide();
	
	});
	
	
	$("img#trends-tool").hover(function() {
	    
	    $(this).removeClass('trends-tool-off');
		$(this).addClass('trends-tool-on');
		
		//$(".orbit-caption a").addClass('bold-link');
		$(".orbit-caption a").show();
		
	
	}, function() {
	
		$(this).removeClass('trends-tool-on');
		$(this).addClass('trends-tool-off');
	    
	   // $(".orbit-caption a").removeClass('bold-link');
	   $(".orbit-caption a").hide();
	
	});
		
	
});