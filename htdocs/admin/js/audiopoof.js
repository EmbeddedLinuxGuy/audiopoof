

var doublePattern = ['0000000100000001',
					'0000001000000010',
					'0000010000000100',
					'0000100000001000',
					'0001000000010000',
					'0010000000100000',
					'0100000001000000',
					'1000000010000000',
					'0000000100000001',
					'0000001000000010',
					'0000010000000100',
					'0000100000001000',
					'0001000000010000',
					'0010000000100000',
					'0100000001000000',
					'1000000010000000'];
					
var singlePattern = ['0000000000000001',
					'0000000000000010',
					'0000000000000100',
					'0000000000001000',
					'0000000000010000',
					'0000000000100000',
					'0000000001000000',
					'0000000010000000',
					'0000000100000000',
					'0000001000000000',
					'0000010000000000',
					'0000100000000000',
					'0001000000000000',
					'0010000000000000',
					'0100000000000000',
					'1000000000000000'];
					
var patternTimer = {};


$(document).ready(function() {
	audiopoofInit();
});



function audiopoofInit() {


	$('#vispanel li a').click(function(event){
		event.preventDefault();		

		if ($(this).hasClass('active')) {
			$(this).removeClass('active');
		} else {
			$(this).addClass('active');
		}
	})

	$('#play').click(function(event){
		event.preventDefault();
		playPattern($('#pattern').val());
	});

	$('#stop').click(function(event){
		event.preventDefault();
		stopPattern();
	});

}

function playPattern(thisPattern) {
	
	var thisPatternData = [];
	if (thisPattern == "1") {
		thisPatternData = singlePattern;
	} else {
		thisPatternData = doublePattern;
	}
	
	var patternIndex = 0;
	patternTimer = $.timer(500, function(timer){
		playPatternStep(thisPatternData, patternIndex);
		
		if ((patternIndex+2) > thisPatternData.length) {
			patternIndex = 0;
		} else {
			patternIndex = patternIndex + 1;
		}
	});
}

function stopPattern() {
	patternTimer.stop();
	$('#vispanel li a').removeClass('active');
}

function playPatternStep(thisPatternData, patternIndex) {
	//trace(patternIndex+' '+thisPatternData[patternIndex]);
	var thisPatternStep = thisPatternData[patternIndex];
	if (thisPatternStep) {
		for (var i=1; i<=thisPatternStep.length; i++) {			
			if (parseInt(thisPatternStep[i - 1])) {
				$('#btn-'+i+' a').addClass('active');
			} else {
				$('#btn-'+i+' a').removeClass('active');
			}
			
		}
		
	}
}
