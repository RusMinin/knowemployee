var QUIZ = JSON.parse(atob(qr));
$('.status_quiz p count').text(QUIZ.length)
let timer;
let secondsLeft;
let INDEX_QUIZ = 0;
let RESULTS = [];

function startTimer(duration) {
    let millisecondsLeft = duration * 1000;
    clearInterval(timer);
    
    function updateTimer() {
        let hours = Math.floor(millisecondsLeft / 3600000);
        let minutes = Math.floor((millisecondsLeft - (hours * 3600000)) / 60000);
        let seconds = Math.floor((millisecondsLeft - (hours * 3600000) - (minutes * 60000)) / 1000);
        let milliseconds = millisecondsLeft % 1000;
        hours = hours < 10 ? '0' + hours : hours;
        minutes = minutes < 10 ? '0' + minutes : minutes;
        seconds = seconds < 10 ? '0' + seconds : seconds;
        milliseconds = milliseconds < 100 ? (milliseconds < 10 ? '00' + milliseconds : '0' + milliseconds) : milliseconds;

        document.querySelector('#timer_quiz .minutes').textContent = minutes;
        document.querySelector('#timer_quiz .sec').textContent = seconds;
        document.querySelector('#timer_quiz .msec').textContent = milliseconds;

        millisecondsLeft -= 10;
        
        if (millisecondsLeft < 0) {
            clearInterval(timer);
            if(QUIZ.length != INDEX_QUIZ){
                nextQuizQuestion();
            }
        }
    }

    timer = setInterval(updateTimer, 10);
}
function stopTimer() {
    clearInterval(timer);
}

function resetTimer() {
    clearInterval(timer);
    $('#timer_quiz').html(`<span class="minutes">00</span>:<span class="sec">00</span>:<span class="msec">00</span>`)
}

function quizStart(){
    if(QUIZ[INDEX_QUIZ]['timer'] != false){
        $('.timer').removeClass('invisible')
        startTimer(QUIZ[INDEX_QUIZ]['timer'])
    }else{
        $('.timer').addClass('invisible')
    }
}

function timeToMilliseconds(timeString) {
    const [minutes, seconds, milliseconds] = timeString.split(':').map(Number);
    return (minutes * 60 * 1000) + (seconds * 1000) + milliseconds;
}


function done_screen(){
    setTimeout(()=>{
        $('.thank_you .circle_abs').css('transition', '1s ease')
        $('.thank_you .circle_abs').css('min-width', "5000px")
        $('.thank_you .circle_abs').css('min-height', "5000px")
        $('.thank_you .circle_abs').css('transform', "scale(2)")
        $('.thank_you .circle_abs').css('transform', "scale(2)")
        $('.powered').css('transition', '1s ease')
        $('.powered').css('color', "#fff")
        $('.powered a').css('color', "#000")
    }, 500)
    setTimeout(()=>{
        $('.thank_you .circle_abs').css('transition', '0')
        $('.thank_you .circle_abs').css('min-width', "100%")
        $('.thank_you .circle_abs').css('min-height', "100vh")
        $('.thank_you .circle_abs').css('border-radius', "0")
        $('.content_thankyou').removeClass('hidden')
        $('.thank_you .load').addClass('hidden')
        $('.powered').css('position', 'absolute')
        $('.powered').css('bottom', 10)
        $('.content_thankyou .star').html(`<svg viewBox="0 0 846.66 846.66" xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd"><path fill="none" stroke="#ffffff" stroke-width="20" class="path" d="M178.47 417.74c21.61 15.66-2.2 48.52-23.81 32.86L17.28 351.19C.72 339.2 10.51 313.1 30.64 314.53l300.1.57c26.62 0 26.62 40.48 0 40.48l-238.81-.46 86.54 62.62zM383.1 239.09c-8.15 25.37-46.72 12.99-38.58-12.38l59.57-184.53c6.06-18.89 32.77-18.5 38.62.14l88.04 272.75 286.82-.55c19.68 0 27.55 25.25 11.87 36.63l-232.3 168.16 89.15 272.58c6.33 19.49-17.04 34.81-32.44 21.71L423.38 645.48 191.66 814.51c-15.91 11.58-37.12-4.18-31.14-22.6l93.68-286.64c8.25-25.36 46.82-12.83 38.58 12.55l-74.25 227.02 192.61-140.5c6.92-5.27 16.75-5.63 24.14-.25l192.94 140.75-74.02-226.32c-3.04-8.31-.36-17.96 7.15-23.4l193.47-140-237.86.46c-8.92.43-17.38-5.13-20.24-14.04l-73.34-227.23-40.28 124.78z"></path></svg>`)
    }, 1000)
}

function nextQuizQuestion(){
    $('.continue button').attr('disabled', true)
    if(QUIZ.length != INDEX_QUIZ){
        let answer = false;
        if($('.grid_button .button.active').length > 0){
            answer = $('.grid_button .button.active .content_btn').text();
        }
    
        const startTimeMilliseconds = QUIZ[INDEX_QUIZ]['timer'] * 1000;
        const currentTimeString = $('#timer_quiz .minutes').text() + ':' +
                                $('#timer_quiz .sec').text() + ':' +
                                $('#timer_quiz .msec').text();

       
        const currentTimeMilliseconds = timeToMilliseconds(currentTimeString);
        const elapsedTimeMilliseconds = Number(startTimeMilliseconds) - Number(currentTimeMilliseconds);
        RESULTS.push({
            "timer": QUIZ[INDEX_QUIZ]['timer'],
            "time_quiz": elapsedTimeMilliseconds,
            "question": QUIZ[INDEX_QUIZ]['question'],
            "answer": answer
        });
    
        resetTimer();
    }

    if(QUIZ.length-1 != INDEX_QUIZ){
        INDEX_QUIZ++
        
        // Timer
        if(QUIZ[INDEX_QUIZ]['timer'] != false){
            $('.timer').removeClass('invisible')
            startTimer(QUIZ[INDEX_QUIZ]['timer'])
        }else{
            $('.timer').addClass('invisible')
        }
        
        // Status/Count
        $('.status_quiz p span').text(INDEX_QUIZ+1)
        $('.status_quiz p count').text(QUIZ.length)

        // Buttons
        let buttons = ``;
        $('.question_quiz').text(QUIZ[INDEX_QUIZ]['question'])
        QUIZ[INDEX_QUIZ]['buttons'].map((item)=>{
            buttons += `
            <button class="button">
                <div class="content_btn">${item}</div>
            </button>
            `
        })
        $('.grid_button').html(buttons)
        clickButtons()
    }else{
        function done_quiz(RESULTS){
            let username = false;
            let type = false;
            if(document.querySelector('.v-form')){
                username =  $('.v-form').val() == "" ? false : $('.v-form').val()
                type = $('.v-form').attr('type_v') == "" ? false : $('.v-form').attr('type_v')
            }
            overStatus = true;
            let formData = JSON.stringify({"up788t7f2bou7t8323vc234eg": RESULTS, "username": username, "type": type});
            fetch(`/quiz/done/${to}`, {
                method: 'POST',
                body: formData,
                headers: {
                    "Content-Type": "application/json",
                },
            })
            .then(response => response.json())
            .then(data => {
                if(data.success == true){
                    $('.wrapper .vote_container').remove()
                    $('.thank_you').removeClass('hidden')
                    done_screen()
                }else{
                    count_bad_request++;
                    if(count_bad_request > 5){
                        alert("Unfortunately, there was an error with sending the results. Check the connection")
                        location.reload()
                    }else{
                        done_quiz()
                    }
                }
            })
            .catch(error => {
                alert("Connection problem, check your internet")
                location.reload()
            });
        }
        done_quiz(RESULTS)
    }
}

function clickButtons(){
    $('.continue button').attr('disabled', true)
    $('.grid_button .button').removeClass('active')

    $('.grid_button .button').click((e)=>{
        $('.grid_button .button').removeClass('active')
        let target = $(e.target);
        let father = $(target).closest('.button');
        $(father).addClass('active')

        $('.continue button').attr('disabled', false)
    })
}
clickButtons()

$('.continue button').on('click', function() { 
    
    if (!$('.continue button').prop('disabled')) {
        if (QUIZ.length != INDEX_QUIZ) {
            nextQuizQuestion(); 
        }
    }
});

$('.v-form').on('input', function() {

    if ($('.v-form').attr('type_v') == 'email'){    
        console.log($('.v-form').val())

        var emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        var isEmail = emailPattern.test($(this).val());

        if (isEmail) {
            $('.start').prop('disabled', false);
        }else{
            $('.start').prop('disabled', true);
        }
    } else if ($('.v-form').attr('type_v') == 'phone'){
        if ($('.v-form').val().length > 10){
            var phonePattern = /^\+?[1-9]\d{1,14}$/;
            var isPhone = phonePattern.test($('.v-form').val());
    
            if (isPhone) {
                $('.start').prop('disabled', false);
            } else {
                $('.start').prop('disabled', true);
            }
        }
    } else if ($('.v-form').attr('type_v') == 'name'){
        if ($('.v-form').val().length > 3) {
            $('.start').prop('disabled', false);
        }else{
            $('.start').prop('disabled', true);
        }
    }
});

$('.start').click(()=>{ 
    $('.content_quiz_start').addClass('hidden')
    $('.content_quiz').removeClass('hidden')

    if(document.querySelector('.v-form')){
        if($('.v-form').val() != "" && $('.v-form').val().length > 3){
            quizStart()
        }else{
            $('.v-form').addClass('invalid')
        }
    }else{
        quizStart() 
    }
    

})